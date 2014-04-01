#Set global path for exec calls
Exec { path => [ "/bin/", "/sbin/" , "/usr/bin/", "/usr/sbin/", "/usr/local/bin" ] }

# starts redis on 127.0.0.1:6379
class { 'redis':
  version => '2.6.5',
  redis_port => '6378',
  redis_bind_address => '0.0.0.0' 
}

class { 'logstash':
  manage_repo => true,
  repo_version => '1.4',
  restart_on_change => false,
  status => 'running',
  init_defaults_file => '/vagrant/logstash/logstash_defaults',
  require   => [Class[redis]]
}

class { 'elasticsearch':
  manage_repo => true,
  repo_version => '1.1.0',
  status => 'running',
  config => {
    'node' => {
      'name' => 'elasticsearch001'
    },
    'index'                => {
      'number_of_replicas' => '0',
      'number_of_shards'   => '5'
    },
    'network'              => {
      'host'               => $::ipaddress,
    }
  },
}

elasticsearch::template { 'logstash':
   file => '/vagrant/elasticsearch/logstash_template.json',
}

elasticsearch::plugin {'mobz/elasticsearch-head':
  module_dir => 'head'
}

elasticsearch::plugin {'elasticsearch/marvel/latest':
  module_dir => 'marvel'
}

logstash::configfile { 'configname':
   source => '/vagrant/logstash/logstash.conf',
}

file { '/etc/logstash/patterns/ads-patterns':
  ensure => 'present',
  source => '/vagrant/logstash/patterns/ads-patterns',
  require => [Class[logstash]]
}

# "This installs Kibana and starts it running on port 5601 and connects to an Elasticsearch index running on localhost:9200"
#include 'kibana'
