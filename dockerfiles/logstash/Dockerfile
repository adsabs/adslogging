
#
# Logstash/Elasticsearch Dockerfile
#
#
 
# Pull base image.
FROM ubuntu:precise
 
# Install ElasticSearch.

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-key adv --keyserver hkp://pgp.mit.edu --recv D88E42B4
RUN echo 'deb http://packages.elasticsearch.org/elasticsearch/1.1/debian stable main' > /etc/apt/sources.list.d/elasticsearch.list
RUN echo 'deb http://packages.elasticsearch.org/logstash/1.4/debian stable main' > /etc/apt/sources.list.d/logstash.list
RUN apt-get update
RUN apt-get install -y build-essential
RUN fakeroot apt-get install -y openjdk-7-jdk

RUN apt-get install -y elasticsearch logstash supervisor redis-server
 
ADD assets/logstash_template.json /etc/elasticsearch/templates/logstash_template.json
ADD assets/logstash.conf /etc/logstash/logstash.conf
ADD assets/logstash-patterns /etc/logstash/patterns/patterns
ADD assets/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

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

cmd ["/run.sh"]
