# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "adslogging-precise64"

  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "https://oss-binaries.phusionpassenger.com/vagrant/boxes/ubuntu-12.04.3-amd64-vbox.box"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.

  # elasticsearch port
  config.vm.network :forwarded_port, guest: 9200, host: 9200
  # kibana port
  config.vm.network :forwarded_port, guest: 9292, host: 9292
  # graphite admin port
  config.vm.network :forwarded_port, guest: 8001, host: 8001
  # statsd port
  config.vm.network :forwarded_port, guest: 8125, host: 8125, protocol: 'udp'

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", "/vagrant/"

  config.vm.provision :shell, :path => "vagrant_bootstrap.sh"
  
  #config.vm.provision :puppet do |puppet|
  #  puppet.manifests_path = "puppet/manifests"
  #  puppet.manifest_file  = "site.pp"
  #end
    
#  config.vm.provision "docker" do |docker|
#    docker.run "busybox",
#      args: "--name data -v /data -v /var/log/supervisor",
#      cmd: "true"
#  end
#  
#  config.vm.provision "docker" do |docker|
#    docker.build_image "/vagrant/dockerfiles/logstash",
#      args: "-t adslogging/logstash"
#    docker.run "adslogging/logstash",
#      args: "--name logstash -p 9200:9200 -p 9300:9300 -p 9292:9292 -p 6379:6379 " \
#            "--volumes-from data"
#  end
#  
#  config.vm.provision "docker" do |docker|
#    docker.build_image "/vagrant/dockerfiles/statsd",
#      args: "-t adslogging/statsd"
#    docker.run "adslogging/statsd",
#      args: "--name statsd -p 8001:8001 -p 8125:8125/udp -p 8126:8126 " \
#            "--volumes-from data"
#  end

end
