
#
# Statsd/Graphite Dockerfile
# Inspiration from https://github.com/nickstenning/dockerfiles
# Inspiration from https://github.com/bosky101/statsd-core
#
 
# Pull base image.
FROM ubuntu:precise

run mkdir -p /var/run/sshd

run echo 'deb http://us.archive.ubuntu.com/ubuntu/ precise universe' >> /etc/apt/sources.list
run apt-get -y update

# Install required packages
run apt-get -y install git nodejs libssl-dev python-ldap python-cairo python-django python-twisted python-django-tagging python-simplejson python-memcache python-pysqlite2 python-support python-pip gunicorn supervisor nginx-light
run apt-get -y install curl screen tree

# install graphite packages
run pip install whisper
run pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/lib" carbon
run pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/webapp" graphite-web

# install statsd
run /usr/bin/git clone https://github.com/etsy/statsd.git /opt/statsd
add ./assets/statsd_config.js /opt/statsd/config.js

# Add system service config
add ./assets/nginx.conf /etc/nginx/nginx.conf
add ./assets/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Add graphite config
add ./assets/initial_data.json /var/lib/graphite/webapp/graphite/initial_data.json
add ./assets/local_settings.py /var/lib/graphite/webapp/graphite/local_settings.py
add ./assets/carbon.conf /var/lib/graphite/conf/carbon.conf
add ./assets/storage-schemas.conf /var/lib/graphite/conf/storage-schemas.conf
run mkdir -p /var/lib/graphite/storage/whisper
run touch /var/lib/graphite/storage/graphite.db /var/lib/graphite/storage/index
run chown -R graphite /var/lib/graphite/storage
run chmod 0775 /var/lib/graphite/storage /var/lib/graphite/storage/whisper
run chmod 0664 /var/lib/graphite/storage/graphite.db
run cd /var/lib/graphite/webapp/graphite && python manage.py syncdb --noinput

# Nginx
expose  :8080
# Carbon line receiver port
#expose  :2003
# Carbon pickle receiver port
#expose  :2004
# Carbon cache query port
#expose  :7002
# statsd udp/tcp ports
expose 8125/udp 8126

# create the user that graphite/carbon runs as using
# note: 1000 is the vagrant uid
RUN adduser --system --home /var/lib/graphite --no-create-home -u 1000 --disabled-password graphite

cmd ["/usr/bin/supervisord"]