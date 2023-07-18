class LatestPricesObj:
    def __init__(self, pair_code,ts,current_ts,prices=None,latency=None,version=None,source=None):
        self.pair_code = pair_code
        self.ts = ts
        self.curren_ts = current_ts
        self.prices = prices
        self.latency = latency
        self.version = version
        self.source = source
        
        
    def __str__(self):
        if self.version is None and self.source is None:
            return f'pair_code: {self.pair_code}, ts: {self.ts}, current_ts: {self.curren_ts}, prices: {self.prices}, latency: {str(self.latency)[:-4]}\'s'
        else:
            return  f'pair_code: {self.pair_code}, ts: {self.ts}, current_ts: {self.curren_ts}, prices: {self.prices}, version: {self.version}, source: {self.source}, latency: {str(self.latency)[:-4]}\'s'