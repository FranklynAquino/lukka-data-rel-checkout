from dataclasses import dataclass

@dataclass
class LatestPricesObj:
    pair_code:str
    prices:int
    ts:str
    current_ts:str
    latency:str