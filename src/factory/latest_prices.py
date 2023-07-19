from requests import (get,
                    exceptions)
from json import (decoder)
from dataclasses import (dataclass,
                        field,
                        InitVar)
from typing import List
from .obj_box.latest_prices_obj import LatestPricesObj
from datetime import datetime
from my_utils.myUtils import get_logger

@dataclass
class LatestPrices:
    """
    Latest Prices Factory for parsing process, 
    outputs list of LatestPrice objects
    """
    headers: str
    region: str
    version: str
    source: str
    portal: InitVar[str] = field(default="https://data-pricing-api.lukka.tech",)
    pair_codes: InitVar[str] = field(default="XBT-USD,ETH-USD,XLT-USD,BCH-USD,BNB-USD,XEC1-USD,BTC-USD",)

    def __post_init__(self,region,pair_codes):
        match region:
            case 'e':
                self.portal = "https://data-pricing-east.lukka.tech"
            case 'w':
                self.portal = "https://data-pricing-west.lukka.tech"
            
        if pair_codes is not None:
            self.pair_codes = ','.join(pair_codes)
            
        #convert self.pair_codes to list
        self.list_of_pair_codes = self.pair_codes.split(',')
            
        self.logger = get_logger('Latest Prices Factory')
        self.list_of_missing_latest_pairs = []

    def parse_latest_prices(self) -> List[LatestPricesObj]:
        args_url = f'{self.portal}/{self.version}/pricing/sources/{self.source}/prices?pairCodes={self.pair_codes}'
        date_now_utc:datetime = datetime.utcnow()
        self.logger.info(f'Your current Region is: {"West/DR" if self.region=="w" else "East/PROD"}')
        self.logger.info("Your current time is: " + date_now_utc.strftime('%Y/%m/%d %H:%M:%S'))
        list_of_latest_prices = []
        try:
            ###
            ### Latency for command with args is calculated here
            ###
            latency_start = datetime.utcnow()
            response = get(url=args_url, headers=self.headers)
            latency_end = datetime.utcnow() - latency_start
            latency_end = latency_end.total_seconds()
            
            
            for pc in self.list_of_pair_codes:
                if not response.text.__contains__(pc):
                    self.list_of_missing_latest_pairs.append(pc)
            
            for item in response.json():
                current_latest_obj = LatestPricesObj(pair_code=item['pairCode'],
                                                    ts=item['ts'],
                                                    current_ts=date_now_utc,
                                                    prices=item['price'],
                                                    latency=latency_end,)
                self.logger.info(f'{current_latest_obj.__repr__()}')
                list_of_latest_prices.append(current_latest_obj)
            return list_of_latest_prices
        except exceptions.JSONDecodeError as e:
            self.logger.info(f'Please use valid bearer token')
        except decoder.JSONDecodeError as e:
            self.logger.info(f'Please use valid bearer token')
            
    def get_list_of_missing_latest_pairs(self) -> List[str]:
        return self.list_of_missing_latest_pairs