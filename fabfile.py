import os
import sys
from os.path import abspath, dirname

from fabric.api import task, local, env
from fabric.context_managers import settings, cd, hide
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

def create_task(name, conf):
    def _task():
        env.containers = [name]
    t = task(name=name)(_task)
    setattr(sys.modules[__name__], name, t)
    return t
    
# generate tasks for each defined container
for container, conf in config.iteritems():
    create_task(container, conf)
    
@task
def all():
    env.containers = config.keys()

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
def run(ep=''):
    for name in env.containers:
        conf = config[name]
        ports = conf.has_key('ports') and ' '.join("-p %s" % p for p in conf['ports']) or ''
        vfrom = conf.has_key('vfrom') and '--volumes-from %s' % conf['vfrom'] or ''
        entrypoint = conf.has_key('entrypoint') and conf['entrypoint'] or ep
        env.docker("run -d -t -i --name adsabs-%s %s %s adsabs/%s %s" % (name, ports, vfrom, name, entrypoint))
    
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
            
            
            