import os
import sys
from os.path import abspath, dirname

from fabric.api import task, local, env
from fabric.context_managers import settings, cd, hide
from fabric.contrib.console import confirm
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
                  '9002:9002', # supervisord
                  ],
        'vfrom': 'adsabs-adsloggingdata',
        'entrypoint': '',
    },
    {
        'name': 'logstash',
        'ports': ['9200:9200', # elasticsearch REST
                  '9292:9292', # kibana
                  '6379:6379', # redis
                  '9003:9003', # supervisord
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

env.show_cmd = False

@task
def show():
    env.show_cmd = True

def docker(cmd, sudo=False, **kwargs):
    with cd(env.base_dir):
        sudo = sudo and "sudo" or ""
        cmd = "%s docker %s" % (sudo, cmd)
        if env.show_cmd:
            print cyan(cmd) 
        else:
            return local(cmd, **kwargs)

def sudo_docker(cmd, **kwargs):
    return docker(cmd, True, **kwargs)
    
env.docker = docker

@task
def sudo():
    """
    execute commands via sudo
    """
    env.docker = sudo_docker

@task
@with_settings(warn_only=True)
def build():
    """
    build the containers
    """
    for name in env.containers:
        env.docker("build -t adsabs/%s dockerfiles/%s" % (name, name))
        
@task
@with_settings(warn_only=True)
def rmi():
    """
    remove the images
    """
    for name in env.containers:
        env.docker("rmi adsabs/%s" % name)
        
@task
@with_settings(warn_only=True)
def run(ep='', **kwargs):
    """
    execute the containers
    
    ep - specify an alternate entrypoint, e.g., "ep=bash"
    **kwargs - additional kwargs will be converted to environment variables passed to container
    
    """
    for conf in config:
        if conf['name'] not in env.containers:
            continue
        ports = conf.has_key('ports') and ' '.join("-p %s" % p for p in conf['ports']) or ''
        vfrom = conf.has_key('vfrom') and '--volumes-from %s' % conf['vfrom'] or ''
        links = conf.has_key('links') and ' '.join("--link %s" % l for l in conf['links']) or ''
        evars = len(kwargs) and ' '.join(["-e %s=%s" % (x[0],x[1]) for x in kwargs.items()]) or ''
        
        entrypoint = conf.has_key('entrypoint') and conf['entrypoint'] or ep
        env.docker("run -d -t -i --name adsabs-%s %s %s %s %s adsabs/%s %s" \
                   % (conf['name'], evars, ports, vfrom, links, conf['name'], entrypoint))
    
@task
@with_settings(warn_only=True)
def data(yes=False):
    """
    remove and recreate the shared data container. WARNING! this will delete existing data & logs!
    """
    # start the data container
    with settings(hide('running', 'stdout', 'stderr')):
        containers = env.docker('ps -a', capture=True)
        if not yes:
            if not confirm("This will erase all existing data. Are you sure?", default=False):
                print cyan("OK, nevermind")
                return
        if 'adsabs-adsloggingdata' in containers:
            env.docker("stop adsabs-adsloggingdata")
            env.docker("rm adsabs-adsloggingdata")
        env.docker('run --name="adsabs-adsloggingdata" -v /data -v /var/log/supervisor ventz/dataos true')

@task
@with_settings(warn_only=True)
def stop():
    """
    stop the containers
    """
    for c in env.containers:
        env.docker("stop adsabs-%s" % c)
    
@task
@with_settings(warn_only=True)
def rm():
    """
    remove the containers
    """
    for c in env.containers:
        env.docker("rm adsabs-%s" % c)
         
@task
@with_settings(warn_only=True)
def gen_certs(container, name):
    """
    generate ssl certificates for use by other services communicating with logstash
    e.g., logstash-forwarder
    """
    path = os.path.join("dockerfiles", container, "certs")
    local("mkdir -p %s" % path)
    local("openssl req -x509 -batch -nodes -newkey rsa:2048 -keyout %s/%s.key -out %s/%s.crt" % (path, name, path, name))
         
@task
@with_settings(warn_only=True)
def data_backup(output_dir, output_file="adsloggingdata.tar"):
    from tempfile import mkdtemp
    tmpdir = mkdtemp()
    env.docker("run --rm --volumes-from adsabs-adsloggingdata -v %s:/backup debian tar --ignore-failed-read -cf /backup/%s /data" \
               % (tmpdir, output_file))
    local("mv %s %s" % (os.path.join(tmpdir, output_file), os.path.join(output_dir, output_file)))
    # force remove the temp directory in case something went wrong with previous comand
    local("rm -rf %s" % tmpdir)
    
@task
@with_settings(warn_only=True)
def rotate_backups(backup_dir, force=False):
    from tempfile import NamedTemporaryFile
    assert os.path.exists(backup_dir)
    with NamedTemporaryFile() as f:
        print >>f, "%s/*.tar {\nrotate 7\ndaily\ncompress\nmissingok\nnocreate\n}" % os.path.abspath(backup_dir)
        f.flush()
        force = force and "-f" or ""
        statefile = "%s/backup.state" % os.path.abspath(backup_dir)
        local("/usr/sbin/logrotate %s -s %s %s" % (force, statefile, f.name))

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
    """
    reindex the existing elasticsearch data. for use after indexing template changes
    """
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
            
