#!/bin/bash

statsd_host=${STATSD_PORT_8125_UDP_ADDR-localhost}
es_heap_size=${ES_HEAP_SIZE-4g}

mkdir -p /data/elasticsearch
chown -R elasticsearch /data/elasticsearch
mkdir -p /data/redis

sed -i -e "s/statsd { host => \"localhost\"/statsd { host => \"$statsd_host\"/g" /etc/logstash/logstash.conf
sed -i -e "s/ES_HEAP_SIZE=[^\s,]\+/ES_HEAP_SIZE=\"$es_heap_size\"/g" /etc/supervisor/conf.d/supervisord.conf

/usr/local/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf