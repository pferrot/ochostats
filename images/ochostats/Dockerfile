FROM autodeskls/ochopod:1.0.6_20151029154900CET

# See https://www.digitalocean.com/community/tutorials/how-to-install-and-use-graphite-on-an-ubuntu-14-04-server
RUN apt-get update && apt-get -y install graphite-web graphite-carbon

RUN apt-get -y install postgresql libpq-dev python-psycopg2

USER postgres

# Need to use '&&\' if we want the 'CREATE USER' and 'CREATE DATABASE' commands to work.
RUN service postgresql start &&\ 
    psql --command "CREATE USER graphite WITH PASSWORD 'password';" &&\
    psql --command "CREATE DATABASE graphite WITH OWNER graphite;"

USER root

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

# Uncomment in case you need custom storage schemas. 
ADD resources/carbon/storage-schemas.conf /etc/carbon/storage-schemas.conf

# Uncomment in case you need custom aggregation rules.
#ADD resources/carbon/storage-aggregation.conf /etc/carbon/storage-aggregation.conf

#RUN service carbon-cache start

RUN apt-get -y install apache2 libapache2-mod-wsgi
#RUN apt-get -y install apache2 libapache2-mod-wsgi

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
RUN wget https://grafanarel.s3.amazonaws.com/builds/grafana_2.5.0_amd64.deb
RUN apt-get install -y adduser libfontconfig
RUN dpkg -i grafana_2.5.0_amd64.deb
RUN rm grafana_2.5.0_amd64.deb
#RUN service grafana-server start
#RUN update-rc.d grafana-server defaults 95 10


ADD resources/pod /opt/ochostats/pod
ADD resources/supervisor /etc/supervisor/conf.d
CMD /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf

# docker run -d -p 8125:8125/udp -p 3000:3000 -p 3050:80 53115ee22736