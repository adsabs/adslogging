import os
from os.path import abspath, dirname

from fabric.api import task, local, env
from fabric.context_managers import settings, cd
from fabric.decorators import with_settings

env.base_dir = abspath(dirname(__file__))

config = {
    'logstash': {
        'ports': ['9200:9200', '9292:9292', '6379:6379'],
        'vfrom': 'adsabs-adsloggingdata',
        'entrypoint': '',
        },
    'statsd': {
        'ports': ['8001:8001', '8125:8125/udp', '8126:8126', '2003:2003', '7002:7002'],
        'vfrom': 'adsabs-adsloggingdata',
        'entrypoint': '',
    }
}

def docker(cmd, sudo=False):
    with cd(env.base_dir):
        sudo = sudo and "sudo" or ""
        return local("%s docker %s" % (sudo,cmd))
    
env.run = docker

@task
def sudo():
    env.run = lambda x: docker(x, True)

@task
@with_settings(warn_only=True)
def build(image=None, rmi=False):
    for name in config.iterkeys():
        if image is not None and image != name:
            continue
        if rmi:
            env.run("rmi adsabs/%s" % name)
        env.run("build -t adsabs/%s dockerfiles/%s" % (name, name))
        
@task
@with_settings(warn_only=True)
def run(container=None, rm=False, ep=''):
    
    # start the data container
    if rm:
        env.run("stop adsabs-adsloggingdata")
        env.run("rm adsabs-adsloggingdata")
    env.run('run --name="adsabs-adsloggingdata" -v /data -v /var/log/supervisor ventz/dataos true')

    for name, conf in config.iteritems():
        if container is not None and container != name:
            continue
        if rm:
            env.run("stop adsabs-%s" % name)
            env.run("rm adsabs-%s" % name)
        else:
            ports = conf.has_key('ports') and ' '.join("-p %s" % p for p in conf['ports']) or ''
            vfrom = conf.has_key('vfrom') and '--volumes-from %s' % conf['vfrom'] or ''
            entrypoint = conf.has_key('entrypoint') and conf['entrypoint'] or ep
            env.run("run -d -t -i --name adsabs-%s %s %s adsabs/%s %s" % (name, ports, vfrom, name, entrypoint))
            
            
            