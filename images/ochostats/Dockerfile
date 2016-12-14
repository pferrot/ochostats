FROM autodeskls/ochopod:1.0.7_20160329123700CEST

# See https://www.digitalocean.com/community/tutorials/how-to-install-and-use-graphite-on-an-ubuntu-14-04-server
# TODO: now that we upgraded to version 0.9.15 through PIP (see below), it would be best to not install anything with apt-get (version 0.9.12 comes with it),
# but it still provides some files that we rely on later on and I was too lazy to change all of that for now.
RUN apt-get update && apt-get -y install graphite-web graphite-carbon wget

RUN apt-get update && apt-get -y install python-dev

RUN pip install --upgrade pip &&\ 
    pip install --upgrade graphite-web==0.9.15 --install-option="--install-scripts=/usr/bin" --install-option="--install-lib=/usr/lib/python2.7/dist-packages" --install-option="--install-data=/var/lib/graphite" &&\ 
    pip install --upgrade carbon==0.9.15 --install-option="--install-scripts=/usr/bin" --install-option="--install-lib=/usr/lib/python2.7/dist-packages" --install-option="--install-data=/var/lib/graphite" &&\ 
    pip install --upgrade whisper==0.9.15 --install-option="--install-scripts=/usr/bin" --install-option="--install-lib=/usr/lib/python2.7/dist-packages" --install-option="--install-data=/var/lib/graphite" &&\
    # See http://stackoverflow.com/questions/27951317/install-graphite-statsd-getting-error-unknown-carbon-cache
    rm -rf /usr/local/lib/python2.7/dist-packages/twisted/ &&\
    pip uninstall -y twisted &&\
    pip install twisted==16.3.0

RUN apt-get -y install postgresql libpq-dev python-psycopg2

USER postgres

# Need to use '&&\' if we want the 'CREATE USER' and 'CREATE DATABASE' commands to work.
RUN service postgresql start &&\ 
    psql --command "CREATE USER graphite WITH PASSWORD 'password';" &&\
    psql --command "CREATE DATABASE graphite WITH OWNER graphite;"

USER root

# With the PIP install above, we need to make sure the the local_settings.py is made available to Graphite
RUN ln -s /etc/graphite/local_settings.py /usr/lib/python2.7/dist-packages/graphite/local_settings.py 

# Update paths for version 0.9.15
RUN sed -i "s/^GRAPHITE_ROOT.*/GRAPHITE_ROOT='\/var\/lib\/graphite'/" /etc/graphite/local_settings.py &&\
    sed -i "s/^CONTENT_DIR.*/CONTENT_DIR = '\/usr\/share\/graphite-web\/static'/" /etc/graphite/local_settings.py

# Replace a_salty_string with a long, random unique string to use as a secret key for this
# install. This key is used for salting of hashes used in auth tokens,
# CRSF middleware, cookie storage, etc. This should be set identically among
# instances if used behind a load balancer.
RUN sed -i "s/^#SECRET_KEY.*/SECRET_KEY = 'a_salty_string'/" /etc/graphite/local_settings.py

# Set your local timezone (Django's default is America/Chicago)
# If your graphs appear to be offset by a couple hours then this probably
# needs to be explicitly set to your local timezone.
# Set it to your time zone as specified by the "TZ" column in the list here: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones.
# Do not forget to escape forward slashes.
RUN sed -i "s/^#TIME_ZONE.*/TIME_ZONE = 'America\/Los_Angeles'/" /etc/graphite/local_settings.py

# REMOTE_USER authentication. See: https://docs.djangoproject.com/en/dev/howto/auth-remote-user/
RUN sed -i "s/^#USE_REMOTE_USER_AUTHENTICATION.*/USE_REMOTE_USER_AUTHENTICATION = True/" /etc/graphite/local_settings.py

#RUN sed -i "s/^#DATABASES\(.*\)/DATABASES = {\n'default': {\n'NAME': 'graphite',\n'ENGINE': 'django.db.backends.postgresql_psycopg2',\n'USER': 'graphite',\n'PASSWORD': 'password',\n'HOST': '127.0.0.1',\n'PORT': ''\n}\n}\n#DATABASES\1/" /etc/graphite/local_settings.py
RUN sed -i "s/'NAME': '\/var\/lib\/graphite\/graphite.db',/'NAME': 'graphite',/" /etc/graphite/local_settings.py
RUN sed -i "s/django.db.backends.sqlite3/django.db.backends.postgresql_psycopg2/" /etc/graphite/local_settings.py
RUN sed -i "s/'USER': '',/'USER': 'graphite',/" /etc/graphite/local_settings.py
RUN sed -i "s/'PASSWORD': '',/'PASSWORD': 'password',/" /etc/graphite/local_settings.py
RUN sed -i "s/'HOST': '',/'HOST': '127.0.0.1',/" /etc/graphite/local_settings.py

RUN service postgresql start &&\ 
    graphite-manage syncdb --noinput

RUN sed -i "s/^CARBON_CACHE_ENABLED=.*/CARBON_CACHE_ENABLED=true/" /etc/default/graphite-carbon

RUN sed -i "s/^ENABLE_LOGROTATION.*/ENABLE_LOGROTATION = True/" /etc/carbon/carbon.conf

ADD resources/carbon/storage-schemas.conf /etc/carbon/storage-schemas.conf

ADD resources/carbon/storage-aggregation.conf /etc/carbon/storage-aggregation.conf

#RUN service carbon-cache start

RUN apt-get -y install apache2 libapache2-mod-wsgi

RUN a2dissite 000-default

RUN cp /usr/share/graphite-web/apache2-graphite.conf /etc/apache2/sites-available

RUN a2ensite apache2-graphite

#RUN service apache2 start

# See https://www.digitalocean.com/community/tutorials/how-to-configure-statsd-to-collect-arbitrary-stats-for-graphite-on-ubuntu-14-04
RUN apt-get -y install git nodejs devscripts debhelper

RUN cd /opt && git clone https://github.com/etsy/statsd.git

#RUN service carbon-cache start

ADD resources/statsd/config.js /etc/statsd/localConfig.js

# See http://docs.grafana.org/installation/debian/
RUN apt-get install -y wget 
RUN wget https://grafanarel.s3.amazonaws.com/builds/grafana_4.0.2-1481203731_amd64.deb
RUN apt-get install -y adduser libfontconfig
RUN dpkg -i grafana_4.0.2-1481203731_amd64.deb
RUN rm grafana_4.0.2-1481203731_amd64.deb
#RUN service grafana-server start
#RUN update-rc.d grafana-server defaults 95 10


ADD resources/pod /opt/ochostats/pod
ADD resources/supervisor /etc/supervisor/conf.d
CMD /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf

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
    curl -H "Content-Type: application/json" -X POST -d @create_datasource.json http://admin:admin@127.0.0.1:3000/api/datasources &&\
    curl -H "Content-Type: application/json" -X PUT -d @update_org_name.json http://admin:admin@127.0.0.1:3000/api/org &&\
    curl -H "Content-Type: application/json" -X PUT -d @change_admin_password.json http://admin:admin@127.0.0.1:3000/api/user/password
    
# We do not need the json files anymore once they have been "executed".
RUN rm -rf  /grafana_init

# See https://github.com/nimiq/docker-postgresql93/pull/5
# work around for AUFS bug
# as per https://github.com/docker/docker/issues/783#issuecomment-56013588
RUN mkdir /etc/ssl/private-copy; mv /etc/ssl/private/* /etc/ssl/private-copy/; rm -r /etc/ssl/private; mv /etc/ssl/private-copy /etc/ssl/private; chmod -R 0700     /etc/ssl/private; chown -R postgres /etc/ssl/private

# Make sure that PID file does not exist so that carbon-cache can be properly started by supervisor
RUN rm -f /var/run/carbon-cache.pid