
#
# Logstash/Elasticsearch Dockerfile
#
#
 
# Pull base image.
FROM ubuntu:precise
 
# Install ElasticSearch.

#run echo 'deb http://us.archive.ubuntu.com/ubuntu/ precise universe' >> /etc/apt/sources.list
#run echo 'deb http://us.archive.ubuntu.com/ubuntu/ main universe' >> /etc/apt/sources.list
RUN apt-key adv --keyserver hkp://pgp.mit.edu --recv D88E42B4
RUN echo 'deb http://packages.elasticsearch.org/elasticsearch/1.1/debian stable main' > /etc/apt/sources.list.d/elasticsearch.list
RUN echo 'deb http://packages.elasticsearch.org/logstash/1.4/debian stable main' > /etc/apt/sources.list.d/logstash.list
run apt-get -y update
RUN apt-get install -y build-essential
RUN fakeroot apt-get install -y openjdk-7-jdk

RUN apt-get install -y elasticsearch logstash supervisor redis-server wget
 # cd to the logstash root directory to do the plugin install

WORKDIR /opt/logstash
RUN bin/plugin install contrib
WORKDIR /

WORKDIR /usr/share/elasticsearch
RUN bin/plugin -i lmenezes/elasticsearch-kopf
RUN bin/plugin -i mobz/elasticsearch-head
RUN bin/plugin -i elasticsearch/marvel/latest
WORKDIR /

ADD assets/logstash_template.json /etc/elasticsearch/templates/logstash.json
ADD assets/logstash.conf /etc/logstash/logstash.conf
ADD assets/logstash-patterns /etc/logstash/patterns/patterns
ADD assets/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD assets/redis.conf /etc/redis/redis.conf
ADD assets/force_encoding.rb /opt/logstash/lib/logstash/filters/force_encoding.rb

add ./assets/run.sh /run.sh
run chmod +x /run.sh

# elasticsearch http
EXPOSE 9200
# kibana
EXPOSE 9292
# elasticsearch transport
EXPOSE 9300
# redis
EXPOSE 6379
# supervisord
EXPOSE 9003

cmd ["/run.sh"]
