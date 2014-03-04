import os
from fabric.api import task, env, run as do
from fabric.context_managers import settings, cd
from fabric.decorators import with_settings

env.gateway = 'pogo3'
env.hosts = ['adswhy']

deploy_path = '/proj/adswhy/logstash'
logstash_dist = 'https://download.elasticsearch.org/logstash/logstash/logstash-1.4.0.beta2.tar.gz'
es_dist = 'https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.tar.gz'

@task
@with_settings(warn_only=True)
def build():
    do('[ -e %s ] || mkdir %s' % (deploy_path, deploy_path))
    with cd(deploy_path):

        # get logstash
        do('wget -O %s %s' % (os.path.basename(logstash_dist), logstash_dist))
        do('tar -xzf %s' % os.path.basename(logstash_dist))

        # get elasticsearch
        do('wget -O %s %s' % (os.path.basename(es_dist), es_dist))
        do('tar -xzf %s' % os.path.basename(es_dist))
        
        # setup the project stuff and venv
        do('[ -e adslogging ] || git clone https://github.com/adsabs/adslogging.git')
        do('[ -e venv ] || virtualenv venv')
        
@task
@with_settings(warn_only=True)
def run():
    pass