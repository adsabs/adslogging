#!/bin/bash

if [ ! -z $SECRET_KEY ]; then
  sed -E -i "s/^environment = (.*)$/environment = \1,SECRET_KEY='$SECRET_KEY'/" /etc/supervisor/conf.d/supervisord.conf
fi

mkdir -p /data/graphite/storage/log/webapp
mkdir -p /data/graphite/storage/whisper
touch /data/graphite/storage/graphite.db /data/graphite/storage/index
chmod 0775 /data /data/graphite /data/graphite/storage /data/graphite/storage/whisper
chmod 0664 /data/graphite/storage/graphite.db
cd /opt/graphite/webapp/graphite && python manage.py syncdb --noinput

# carbon stores it's db here
chown -R www-data /data/graphite/storage
# carbon writes it's pid here
chown -R www-data /opt/graphite/storage

/usr/local/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

