# Prometheus Communicator

Web service that transmit the alerts from Prometheus to other places, powered by Jinja templating.

> [!WARNING]
> This project is still a prototype.


## Usage

1. Install this application

   ```bash
   pip install 'git+https://github.com/tzing/prometheus-communicator.git#egg=prometheus-communicator'
   ```

2. Create a configuration file

   This application reads `config.yaml` in the current working directory by default. Or you can specify the path by environment variable `PROMETHEUS_COMMUNICATOR_CONFIG_PATH`.

   ```yaml
   receivers:
     - # unique name of the receiver
       name: demo
       # handler type
       # currently only `http` handler is supported. It sends a request to the specified URL with the rendered template.
       handler: http
       params:
         # URL to send the request
         url: https://httpbin.org/post
         # (Optional) HTTP method to use. Default is POST.
         method: POST
         # (Optional) HTTP headers to send. Default is JSON content type.
         headers:
           Content-Type: application/json
         # Jinja template to render the request body.
         # The alertmanager webhook payload is passed as variables.
         # See https://prometheus.io/docs/alerting/latest/configuration/#webhook_config for the payload structure.
         template: |-
           {
             "alerts": {
               {%- for alert in alerts %}
               "{{ alert.fingerprint }}": "{{ alert.status }}"
               {{- ',' if not loop.last }}
               {%- endfor %}
             }
           }
   ```

3. Run the application

   ```bash
   fastapi run prometheus_communicator
   ```

4. Setup Prometheus Alertmanager

   ```yaml
   receivers:
     - name: communicator-demo
       webhook_configs:
         - url: http://localhost:8000/v1/webhook/demo
   ```

With the above configurations, the application will listen on `http://localhost:8000/v1/webhook/demo` for incoming alerts. When an alert is received, it will send a POST request to `https://httpbin.org/post` with the following JSON body:

```json
{
    "alerts": {
        "fingerprint1": "firing",
        "fingerprint2": "firing"
    }
}
```
