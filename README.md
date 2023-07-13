
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


