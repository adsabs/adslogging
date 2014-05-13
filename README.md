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

Services!

    Elasticsearch: http://localhost:9200
    Elasticsearch Kopf: http://localhost:9200/_plugin/kopf
    Kibana: http://localhost:9292
    Supervisord: http://localhost:9002 & http://localhost:9003
    Graphite: http://localhost:8001
