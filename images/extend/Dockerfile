FROM pferrot/ochostats:1.0.7_20160329123700CEST_0.4

# Replace a_salty_string with your own salty string: should be a long, random unique 
# string to use as a secret key for this install. This key is used for salting of hashes
# used in auth tokens, CRSF middleware, cookie storage, etc. This should be set identically among
# instances if used behind a load balancer.
RUN sed -i "s/SECRET_KEY = 'a_salty_string'/SECRET_KEY = 'my_custom_salty_string'/" /etc/graphite/local_settings.py

# Set your local timezone (Django's default is America/Chicago)
# If your graphs appear to be offset by a couple hours then this probably
# needs to be explicitly set to your local timezone.
# Set it to your time zone as specified by the "TZ" column in the list here: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones.
# Do not forget to escape forward slashes.
RUN sed -i "s/TIME_ZONE = 'America\/Los_Angeles'/TIME_ZONE = 'Europe\/Paris'/" /etc/graphite/local_settings.py

ADD resources/statsd/config.js /etc/statsd/localConfig.js

ADD resources/carbon/storage-schemas.conf /etc/carbon/storage-schemas.conf

# Init grafana (grafana.ini, configure datasource, change default admin password).
# Note that we use a template for grafana.ini: the actual grafana.ini file is
# generated in pod.py. This allows to pass some dynamic configuration information
# to the pod, like the Grafana root URL.
ADD resources/grafana_init/grafana.ini /etc/grafana/grafana.ini
ADD resources/grafana_init/templates/grafana.ini /opt/ochostats/templates/grafana.ini

ADD resources/grafana_init /grafana_init

RUN service postgresql start &&\
    service grafana-server start &&\
    service carbon-cache start &&\
    cd /grafana_init &&\
    curl -H "Content-Type: application/json" -X PUT -d @update_org_name.json http://admin:admin@127.0.0.1:3000/api/org &&\
    find dashboards -name "*.json" -exec curl -H "Content-Type: application/json" -X POST -d @{} http://admin:admin@127.0.0.1:3000/api/dashboards/db \; &&\
    curl -H "Content-Type: application/json" -X PUT -d @change_admin_password.json http://admin:admin@127.0.0.1:3000/api/user/password
    
# We do not need the json files anymore once they have been "executed".
RUN rm -rf  /grafana_init

# Make sure that PID file does not exist so that carbon-cache can be properly started by supervisor
RUN rm -f /var/run/carbon-cache.pid

# Create volumes so that data is not lost and possible to backup.
VOLUME /var/lib/graphite /var/lib/grafana /var/lib/postgresql/9.3/main

