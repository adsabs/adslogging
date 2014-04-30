

from    ubuntu:precise

run mkdir -p /var/run/sshd

run echo 'deb http://us.archive.ubuntu.com/ubuntu/ precise universe' >> /etc/apt/sources.list
run apt-get -y update

# Install required packages
run apt-get -y install git nodejs libssl-dev python-ldap python-cairo python-django python-twisted python-django-tagging python-simplejson python-memcache python-pysqlite2 python-support python-pip gunicorn supervisor nginx-light
run apt-get -y install curl screen tree
run pip install whisper
run pip install --install-option="--prefix=/opt/graphite" --install-option="--install-lib=/opt/graphite/lib" carbon
run pip install --install-option="--prefix=/opt/graphite" --install-option="--install-lib=/opt/graphite/webapp" graphite-web

# install statsd
run /usr/bin/git clone https://github.com/etsy/statsd.git /opt/statsd
add ./assets/statsd_config.js /opt/statsd/config.js

# Add system service config
add ./assets/nginx.conf /etc/nginx/nginx.conf
add ./assets/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Add graphite config
add ./assets/initial_data.json /opt/graphite/webapp/graphite/initial_data.json
add ./assets/local_settings.py /opt/graphite/webapp/graphite/local_settings.py
add ./assets/carbon.conf /opt/graphite/conf/carbon.conf
add ./assets/storage-schemas.conf /opt/graphite/conf/storage-schemas.conf

add ./assets/run.sh /run.sh
run chmod +x /run.sh

# Nginx proxy to graphite
expose 8001
# statsd udp/tcp ports
expose 8125/udp 8126
# graphite ports
expose 2003
expose 2004
expose 7002
# supervisord
expose 9002

cmd ["/run.sh"]
