class LatestPricesObj:
    def __init__(self, pair_code,ts,current_ts,prices=None,latency=None):
        self.pair_code = pair_code
        self.ts = ts
        self.curren_ts = current_ts
        self.prices = prices
        self.latency = latency
        
    def __str__(self):
        return f'pair_code: {self.pair_code}, ts: {self.ts}, current_ts: {self.curren_ts}, prices: {self.prices}'