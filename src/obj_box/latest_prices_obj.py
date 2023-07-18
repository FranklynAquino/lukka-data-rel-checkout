class LatestPricesObj:
    def __init__(self, pair_code,ts,current_ts,prices=None,latency=None,version=None,source=None):
        self.pair_code:str = pair_code
        self.ts = ts
        self.curren_ts = current_ts
        self.prices = prices
        self.latency = latency
        self.version = version
        self.source = source
        
    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.pair_code == other.pair_code 
                and self.ts == other.ts 
                and self.prices == other.prices
                and self.latency == other.latency
                and self.version == other.version
                and self.source == other.source)
    
    def __hash__(self):
        return hash((self.__class__,
                    self.pair_code,
                    self.ts,
                    self.prices,
                    self.latency,
                    self.version,
                    self.source))
        
    def __str__(self):
        if self.version is None and self.source is None:
            return f'pair_code: {self.pair_code}, ts: {self.ts}, current_ts: {self.curren_ts}, prices: {self.prices}, latency: {str(self.latency)[:-4]}\'s'
        else:
            return  f'pair_code: {self.pair_code}, ts: {self.ts}, current_ts: {self.curren_ts}, prices: {self.prices}, version: {self.version}, source: {self.source}, latency: {str(self.latency)[:-4]}\'s'