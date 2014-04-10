#!/bin/bash

mkdir -p /usr/share/elasticsearch/data
chown -R elasticsearch /usr/share/elasticsearch/data
mkdir -p /data/elasticsearch
chown -R elasticsearch /data/elasticsearch

/usr/bin/supervisord
