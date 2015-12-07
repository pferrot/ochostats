Add as many .json files as you want. See schema details here: http://docs.grafana.org/reference/http_api/#create-update-dashboard

If you exported your existing dashboards from the Grafana UI, you need to slightly modify the JSON as follows:

- replace the ID value with null (very first element)
- encapsulate the entire JSON with th "dashboard" element, e.g.:

{
  "dashboard": {
  
    ...<what got exporter from the UI here>...
  
  }
}