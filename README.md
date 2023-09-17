# nimbus-monitor-api
API for the Nimbus protocol.

## How it works
- collects data from monitor-scraper (`api` and `validators_info` tables) and token-price-collector databases;
- response with collected data, urls: `0.0.0.0:{API_PORT}/api` and `0.0.0.0:{API_PORT}/validators`;
- default Prometheus metrics are available at `0.0.0.0:{API_PORT}/metrics`.


## Requirements
* Python 3.9


## Setup
```shell
pip install -r requirements.txt
```


## Run
The service receives its configuration parameters from environment variables. Export required parameters from the list below and start the service:
```shell
bash run.sh
```

To stop the service, send the SIGINT or SIGTERM signal to the process.


## Configuration parameters
#### Required
* `DATABASE_URL_MONITOR` - The URL to the `monitor-scraper` database. Example: `postgres://admin:1234@localhost:5432/monitor-scraper`.
* `DATABASE_URL_TOKEN_PRICE` - The URL to the `token-price-collector` database. Example: `postgres://admin:1234@localhost:5432/token-price-collector`.

#### Optional
* `API_PORT` - The default value is `8000`.
* `LOG_LEVEL` - The logging level of the logging module: `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. The default level is `INFO`.
* `PROMETHEUS_METRICS_PREFIX` - The default value is `monitor_api_`.
* `TOKEN_SYMBOL_PARA` - The token symbol in the parachain. The following values are supported: [`glmr`, `movr`].
* `TOKEN_SYMBOL_RELAY` - The token symbol in the relay chain. The following values are supported: [`dot`, `ksm`].
