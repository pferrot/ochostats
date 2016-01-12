# Ochostats

Ochostats provides a ready to use <a href="https://github.com/autodesk-cloud/ochopod" target="_blank">Ochopod</a>-enabled <a href="https://github.com/etsy/statsd" target="_blank">StatsD</a>/<a href="http://graphite.readthedocs.org" target="_blank">Graphite</a>/<a href="http://grafana.org" target="_blank">Grafana</a> server.

## Instructions

You can have two options to use Ochostats:
1) Either use the base image (pferrot/ochostats:1.0.6_20151029154900CET_0.2) as is and e.g. customize dashboards from grafana UI once the container is up and running.
2) Or (recommended option) create your own Docker image by extending the Ochostats base image and include whatever customization you need (e.g. dashboards) directly within your base image. See the example under images/extend and follow the instructions below.
Use the files under images/extend/images as template and adapt to your needs as follows:
- Modify the Dockerfile:
  - Replace 'my_custom_salty_string' with your own random unique secret key for Graphite
  - *Optional*: Configure the Django timezone (search for 'Set your local timezone' in Dockerfile) - defaults to 'America/Los_Angeles'
- *Optional*: configure schemas definitions and aggregation methods for Whisper files by modifying the files under images/extend/resources/carbon
- *Optional*: customize Grafana (e.g. enable anonymous access) by editing the file images/extend/resources/grafana_init/grafana.ini
- *Optional*: customize StatsD by editing the file images/extend/resources/statsd/config.js
- *Optional*: modify the default Grafana admin password by editing the file images/extend/resources/grafana_init/change_admin_password.json
- *Optional*: modify the Grafana main org name by editing the file images/extend/resources/grafana_init/update_org_name.json
- *Optional*: create default dashboards by addind .json files under images/extend/resources/grafana_init/dashboards
- Build the image with 'docker build .' from images/extend/resources
- Tag and push your image to Docker Hub (or whatever repository you are using)
- Modify the file images/extend/resources/ochothon_custom-ochostats.yml:
  - Set a valid cluster name
  - Replace &lt;your_image_name_here&gt; with the name of the image that you just built
- Deploy your image to you Mesos/Marathon cluster with <a href="https://github.com/autodesk-cloud/ochothon" target="_blank">Ochothon</a> thanks to the file ochothon_custom-ochostats.yml that you just modified
- Configure your Ochopod clusters that you want to submit metrics to depend on 'ochostats' and send StatsD metrics to Ochostats UDP port 8125 (this is the container port - use Ochopod as usual to send the packets to the proper host and port)
- Access the Grafana UI at http://&lt;ochostats_host&gt;:3000 (get the IP/host thanks to Ochothon or the Marathon UI) and start monitoring or building beautiful graphs
  
## Release notes

### 0.2 (1/11/2016)
- Existing base image (pferrot/ochostats:1.0.6_20151029154900CET_0.2) with instructions on how to extend it
- Created datasource marked as default datasource
- Fixed bug preventing PostgreSQL from starting up due to file permission issue
- Fixed bug preventing Carbon from starting up due to stale PID file

### 0.1 (12/07/2015)
- First version