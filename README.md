
# Lukka Data Release Checkout Mini

A script dedicated for Pricing API, that checkouts several endpoints.


## Requirements

**Pricing API bearer token**
## Argument Reference

#### Authentication (-t)

```shell
    python3 run.py -t <token>
```
| Argument | Flag     | Description                |
| :-------- | :------- | :------------------------- |
| `--token` | `-t` | Insert bearer token after this argument/flag to run|

#### Run all endpoints using all sources (run_all)

```shell
    python3 run.py run_all -t <token>
```

| Argument | Flag     | Description                |
| :-------- | :------- | :------------------------- |
| `run_all` |  | **Only** Runs v1 & v3 (source:2000,10500)|


#### Run by version, source, or pair code  (-v, -s, -pc)

```shell
    python3 run.py -v <version> -s <source> -pc <pair-codes> -t <token>
```

| Argument | Flag     | Description                |
| :-------- | :------- | :------------------------- |
| `--version` | `-v` | Specify version (e.g. v1, v3)| 
| `--source`| `-s` | Specify source (e.g. 2000,10500)|
| `--pair_codes`| `-pc` | Specify 1 or many pairCodes (e.g. ETH-USD BNB-USD)|