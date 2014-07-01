adslogging
==========

centralized logging and metric collection for the ADS ecosystem

## Development Quick start

After installing [Vagrant](http://vagrantup.com/), create and boot the VM:

	vagrant up

SSH to the VM:

	vagrant ssh

Build the docker containers

    cd /vagrant
    fab all build

Run the docker containers

	fab data
    fab all run

## Included Apps & Services

### statsd

- image name: adsabs/statsd
- container name: adsabs-statsd

The `statsd` container includes:

* the [statsd](https://github.com/etsy/statsd/) service which listens for UDP messages on port 8125
* the [carbon-cache](http://graphite.readthedocs.org/en/latest/carbon-daemons.html) service which recieves the aggregated metrics data from statsd
* the [graphite](http://graphite.readthedocs.org/en/latest/index.html) frontend which is proxied by ngnix and available at http://localhost:8001
* the [ngnix](http://nginx.org/) http server which proxies requests from 8001 to the graphite service

To view and manipulate the status of the running applications, the [supervisord](http://supervisord.org/) admin UI is at http://localhost:9002

### logstash

- image name: adsabs/logstash
- container name: adsabs-logstash

The `logstash` container includes:

* the [redis](http://redis.io) "broker" which accepts incoming log events from the beaver forwarding agent on port 6379.
* the [elasticsearch](http://elasticsearch.org) instance which is accessible via http://localhost:9200
* the [logstash](http://logstash.net) instance which pulls log event data off of redis, processes the events, and then sends to elasticsearch
* the [kibana](http://www.elasticsearch.org/overview/kibana/) instance which provides a visualization/dashboard UI to the indexed data at http://localhost:9292

Additionally, the elasticsearch instance has a few plugins that provide additional interfaces to the indexed data:

* [Kopf](https://github.com/lmenezes/elasticsearch-kopf) is an elasticsearch administration and index viewer: http://localhost:9200/_plugin/kopf
* [Marvel](http://www.elasticsearch.org/overview/marvel/) is another elasticsearch admin and monitoring UI.
* Head is a less polished precursor to Kopf and should probably be dropped.

To view and manipulate the status of the running applications, the supervisord admin UI is at http://localhost:9003

### data

- container name: adsabs-adsloggingdata
- volumes provided: /data, /var/log/supervisord

Both the `statsd` and `logstash` containers mount volumes from a shared data container as part of a strategy to persist both the indexed data and the log output of the running containers.

## Vagrant settings

You can specify the amount of memory/cpus to devote to the vm by setting the `VAGRANT_MEMORY` and `VAGRANT_CPUS` environment variables prior to running `vagrant up`. e.g., `export VAGRANT_MEMOR=2g` and `export VAGRANT_CPUS=2`.

## Fabric tasks

There are two types of fabric tasks defined: prefix tasks and command tasks. The prefix tasks do things to affect the execution of the subsequent commands. Command tasks are things like `build`, `run`, `stop`, `rm`. Prefix tasks are `show`, `sudo`, `all`, and the configured container names.

Each container specified in the fabfile's `config` member gets it's own prefix task. Currently there are only the `statsd` and `logstash` containers. You can perform tasks on all containers using the prefix task `all`.

There is also the `show` prefix which outputs the actual command fabric will run instead of actually running it. `sudo` will tell fabric to run commands via sudo.

Examples:

`fab statsd run`: runs the statsd docker container

`fab all run`: runs all the containers specified in `fabfile.config`

`fab show statsd run`: shows the command fabric would use to run the statsd container

`fab logstash build`: builds the logstash docker container

`fab sudo logstash build`: executes the logstash docker build command via sudo

Fabric tasks can be chained together in various orders:

`fab all stop rm build show run`: stops, removes, and builds all containers, and then shows the command to be used for executing them

### Special tasks

#### `fab data` 
This removes and recreates the container that provides the shared data space which both the `logstash` and `statsd` containers write logs and index data to. **NOT TO BE RUN IN PRODUCTION** unless you really know what you're doing, as this will delete the existing log event indexes.

#### `fab gen_certs`
This will generate ssl certificates that can be used for secure interprocess communication, e.g. logstash-forwarder <-> logstash. The task takes two positional arguments: `container` and `name`. `container` indicates where to place the resulting certificate files, e.g., `dockerfiles/<container>/certs/`. `name` indicates what to name the resulting files: `<name>.key` and `<name>.cft`.

#### `fab reindex` 
This task can be used to reindex the log data stored in elasticsearch in the event of an index template change, for instance if new fields are added or the indexing settings for a particular field need to change. It requires one positional argument, `tag`, which will be used to create the new indexes. The base index name will then be aliased (or re-aliased) to the new index name. You can also specify a pattern to indicate the indexes to reindex. The default is `logstash-*`, which means reindex everything.

Example: you've modified the elasticsearch index template ([logstash_template.json](dockerfiles/logstash/assets/logstash_template.json)) and now want to reindex all existing data. Executing the task `fab reindex:20140701-1` will iterate through all existing indexes, reindex them with a new index name of `<base_index_name>:20140701-1`, alias `<base_index_name>` to the new name, and then delete the old index. Elasticsearch handles these aliases transparently.


