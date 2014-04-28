#!/bin/bash

statsd_host=${STATSD_PORT_8125_UDP_ADDR-localhost}

mkdir -p /usr/share/elasticsearch/data
chown -R elasticsearch /usr/share/elasticsearch/data
mkdir -p /data/elasticsearch
chown -R elasticsearch /data/elasticsearch
mkdir -p /data/redis

sed -i -e "s/statsd { host => \"localhost\"/statsd { host => \"$statsd_host\"/g" /etc/logstash/logstash.conf

/usr/bin/supervisord
