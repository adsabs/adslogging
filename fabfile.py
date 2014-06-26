import os
import sys
from os.path import abspath, dirname

from fabric.api import task, local, env
from fabric.context_managers import settings, cd, hide
from fabric.colors import cyan, red
from fabric.utils import abort
from fabric.decorators import with_settings

env.base_dir = abspath(dirname(__file__))

# ORDER IS IMPORTANT HERE 
# containers that are linked to should appear first
config = [
    {
        'name': 'statsd',
        'ports': ['8001:8001', # ngnix proxy to graphite server
                  '8125:8125/udp', # statsd
                  '127.0.0.1:8126:8126', # statsd management
                  '9002:9002',
                  ],
        'vfrom': 'adsabs-adsloggingdata',
        'entrypoint': '',
    },
    {
        'name': 'logstash',
        'ports': ['9200:9200', # elasticsearch REST
                  '9292:9292', # kibana
                  '6379:6379', # redis
                  '9003:9003',
                  ],
        'vfrom': 'adsabs-adsloggingdata',
        'links': ['adsabs-statsd:statsd'],
        'entrypoint': '',
    },
]

def create_task(conf):
    def _task():
        env.containers = [conf['name']]
    t = task(name=conf['name'])(_task)
    setattr(sys.modules[__name__], conf['name'], t)
    return t
    
# generate tasks for each defined container
for conf in config:
    create_task(conf)
    
# check that status of vm.overcommit_memory setting which is 
# needed by redis. See: http://redis.io/topics/admin
with settings(hide('running'), warn_only=True):
    vm_oc_memory = local("sysctl -n vm.overcommit_memory", capture=True)
    if vm_oc_memory == "0":
        print red("WARNING: vm.overcommit_memory kernel setting is set to 0 which " \
                  + "which is not recommended for redis (see http://redis.io/topics/admin). " \
                  + "Run `sysctl vm.overcommit_memory=1` on the host machine to correct this.")
    
@task
def all():
    env.containers = [x['name'] for x in config]

def docker(cmd, sudo=False, **kwargs):
    with cd(env.base_dir):
        sudo = sudo and "sudo" or ""
        return local("%s docker %s" % (sudo,cmd), **kwargs)

def sudo_docker(cmd, **kwargs):
    return docker(cmd, True, **kwargs)
    
env.docker = docker

@task
def sudo():
    env.docker = sudo_docker

@task
@with_settings(warn_only=True)
def build():
    for name in env.containers:
        env.docker("build -t adsabs/%s dockerfiles/%s" % (name, name))
        
@task
@with_settings(warn_only=True)
def rmi():
    for name in env.containers:
        env.docker("rmi adsabs/%s" % name)
        
@task
@with_settings(warn_only=True)
def run(ep='', **kwargs):
    for conf in config:
        if conf['name'] not in env.containers:
            continue
        ports = conf.has_key('ports') and ' '.join("-p %s" % p for p in conf['ports']) or ''
        vfrom = conf.has_key('vfrom') and '--volumes-from %s' % conf['vfrom'] or ''
        links = conf.has_key('links') and ' '.join("--link %s" % l for l in conf['links']) or ''
        evars = ""
        if len(kwargs):
            for k,v in kwargs.items():
                evars += "-e %s=%s" % (k,v)
        entrypoint = conf.has_key('entrypoint') and conf['entrypoint'] or ep
        env.docker("run -d -t -i --name adsabs-%s %s %s %s %s adsabs/%s %s" % (conf['name'], evars, ports, vfrom, links, conf['name'], entrypoint))
    
@task
@with_settings(warn_only=True)
def data():
    # start the data container
    with settings(hide('running', 'stdout', 'stderr')):
        containers = env.docker('ps -a', capture=True)
        if 'adsabs-adsloggingdata' in containers:
            env.docker("stop adsabs-adsloggingdata")
            env.docker("rm adsabs-adsloggingdata")
        env.docker('run --name="adsabs-adsloggingdata" -v /data -v /var/log/supervisor ventz/dataos true')

@task
@with_settings(warn_only=True)
def stop():
    for c in env.containers:
        env.docker("stop adsabs-%s" % c)
    
@task
@with_settings(warn_only=True)
def rm():
    for c in env.containers:
        env.docker("rm adsabs-%s" % c)
         
#### reindexing stuff ###
TAG_SEPARATOR = ':'
pyes = None

def get_targets(index_pattern):
    import fnmatch
    targets = []
    indexes = pyes.aliases()
    for index_name, index_meta in indexes.iteritems():
        if fnmatch.fnmatch(index_name, index_pattern):
            aliases = index_meta['aliases'].keys()
            if len(aliases) > 1:
                raise Exception("I'm confused! %s has %d aliases!" % (index_name, len(aliases)))
            elif len(aliases) == 0:
                alias = index_name
            else:
                alias = aliases[0]
            targets.append((index_name, alias))
    return targets
        
@task
def reindex(tag, index="logstash-*", es_host="localhost:9200"):
    # use this one for the basics
    import pyelasticsearch
    # use this one only for the reindex command
    import elasticsearch
    from elasticsearch.helpers import reindex

    if '.' in tag or ':' in tag:
        abort("Sorry! '.' and ':' are not allowed in index tag values")
        
    global pyes
    pyes = pyelasticsearch.ElasticSearch('http://' + es_host)
    targets = get_targets(index)

    for index_name, alias in targets:

        print(cyan("working on %s" % index_name))

        if TAG_SEPARATOR in index_name:
            new_index_name = TAG_SEPARATOR.join([index_name[:index_name.rindex(TAG_SEPARATOR)], tag])
        else:
            new_index_name = TAG_SEPARATOR.join([index_name, tag])
            
        print(cyan("new_index_name: %s" % new_index_name))

        print(cyan("reindexing: %s -> %s" % (index_name, new_index_name)))
        host, port = es_host.split(':')
        es = elasticsearch.Elasticsearch([{'host': host, 'port': port}])
        
        # Return value is a tuple of counts: (reindexed docs, failures)
        reindexed = reindex(es, index_name, new_index_name)
        print(cyan("result: %s" % str(reindexed)))

        # if everything went OK
        if reindexed[0] > 0 and reindexed[1] == 0:
            if new_index_name != index_name:
                print(cyan("deleting: %s" % index_name))
                pyes.delete_index(index_name)

                print(cyan("creating alias %s > %s" % (new_index_name, alias)))
                actions = [{ "add" : { "index" : new_index_name, "alias" : alias } }]
                pyes.update_aliases({ "actions" : actions })
            
