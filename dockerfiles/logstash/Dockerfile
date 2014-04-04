
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
RUN apt-get install -y elasticsearch logstash supervisor
 
# Expose ports.
#   - 9200: HTTP
#   - 9292: Kibana
#   - 9300: transport
EXPOSE 9200
EXPOSE 9292
EXPOSE 9300
 
ADD assets/logstash_template.json /etc/elasticsearch/templates/logstash_template.json
ADD assets/logstash.conf /etc/logstash/logstash.conf
ADD assets/logstash-patterns /etc/logstash/patterns/patterns
ADD assets/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
ADD assets/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run supervisord
CMD ["/usr/bin/supervisord"]