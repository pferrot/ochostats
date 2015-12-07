# Ochostats

Ochostats provides a ready to use <a href="https://github.com/autodesk-cloud/ochopod" target="_blank">Ochopod</a>-enabled <a href="https://github.com/etsy/statsd" target="_blank">StatsD</a>/<a href="http://graphite.readthedocs.org" target="_blank">Graphite</a>/<a href="http://grafana.org" target="_blank">Grafana</a> server.

## Instructions

- *Optional*: slightly adapt the Dockerfile under images/ochostats/images:
  - Set a long, random unique secret key for Graphite (search for 'Replace a_salty_string' in Dockerfile)
  - Configure the Django timezone (search for 'Set your local timezone' in Dockerfile) 
- *Optional*: configure schemas definitions and aggregation methods for Whisper files by modifying the files under images/ochostats/resources/carbon
- *Optional*: customize Grafana (e.g. enable anonymous access) by editing the file images/ochostats/resources/grafana_init/grafana.ini
- *Optional*: customize StatsD by editing the file images/ochostats/resources/statsd/config.js
- *Optional*: modify the default Grafana admin password by editing the file images/ochostats/resources/grafana_init/change_admin_password.json
- *Optional*: modify the Grafana main org name by editing the file images/ochostats/resources/grafana_init/update_org_name.json
- *Optional*: create default dashboards by addind .json files underunder images/ochostats/resources/grafana_init/dashboards
- Build the image with 'docker build .' from images/ochostats/resources
- Tag and push your image to Docker Hub (or whatever repository you are using)
- Deploy your image to you Mesos/Marathon cluster with <a href="https://github.com/autodesk-cloud/ochothon" target="_blank">Ochothon</a> thanks to the file images/ochostats/resources/ochothon_ochostats.yml *after* you have modified it to use your freshly created Docker image
- Configure your Ochopod clusters that you want to submit metrics to depend on 'ochostats' and send StatsD metrics to Ochostats UDP port 8125 (this is the container port - use Ochopod as usual to send the packets to the proper host and port)
- Access the Grafana UI at http://&lt;ochostats_host&gt;:3000 (get the IP/host thanks to Ochothon or the Marathon UI) and start building beautiful graphs
  
## Release notes

### 0.1 (12/07/2015)
- First version