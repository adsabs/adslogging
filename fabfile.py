import os
from os.path import abspath, dirname

from fabric.api import task, local, env
from fabric.context_managers import settings, cd
from fabric.decorators import with_settings

env.base_dir = abspath(dirname(__file__))
env.run = local

def docker(cmd):
    with cd(env.base_dir):
        return env.run("docker %s" % cmd)
    
@task
def sudo():
    env.run = lambda x: "sudo " + x

@task
@with_settings(warn_only=True)
def build(rmi=False):
    if rmi:
        docker("rmi adslogging/logstash adslogging/statsd")
    docker("build -t adslogging/logstash dockerfiles/logstash")
    docker("build -t adslogging/statsd dockerfiles/statsd")
        
@task
@with_settings(warn_only=True)
def run(rm=False):
    if rm:
        docker("rm data adslogging-logstash adslogging-statsd")
    docker("run -d --name adslogging-data -v /data -v /var/log/supervisor busybox true")
    docker("run -d --name adslogging-logstash -p 9200:9200 -p 9300:9300 -p 9292:9292 -p 6379:6379 --volumes-from adslogging-data adslogging/logstash")
    docker("run -d --name adslogging-statsd -p 8001:8001 -p 8125:8125/udp -p 8126:8126 -p 2003:2003 -p 2004:2004 -p 7002:7002 adslogging/statsd")