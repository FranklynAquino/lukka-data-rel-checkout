from typing import List
from datetime import (datetime, timedelta)
import regex as re

from my_utils.myUtils import get_logger
from factory.obj_box.latest_prices_obj import LatestPricesObj

class LagChecker:
    def __init__(self, list_of_latest_prices: List[LatestPricesObj], source: str = None, version: str = None,logger=None):
        self.list_of_latest_prices = list_of_latest_prices
        self.source = source
        self.version = version

        self.five_min_lag = timedelta(minutes=5)
        self.three_min_lag = timedelta(minutes=3)
        self.one_min_lag = timedelta(minutes=1)
        self.lag_failure_counter = 0

    def calculate_latencies(self) -> List[LatestPricesObj]:
        list_of_lagged_ts = []
        match self.source:
            case '10500':
                for latest_price in self.list_of_latest_prices:
                    latest_ts = datetime.strptime(
                        latest_price.ts, '%Y-%m-%dT%H:%M:%SZ')
                    lag = latest_price.current_ts - latest_ts
                    match = re.compile(
                        r'[0-9]\.[0-9]{3}').search(latest_price.prices)
                    if lag <= self.one_min_lag and match:
                        print(
                            f'{self.version}({self.source}): {latest_price.pair_code} is within current time: difference: {lag} & prices include sub-pennies ({latest_price.prices})')
                    else:
                        self.lag_failure_counter += 1
                        latest_price.version = f'{self.version}'
                        latest_price.source = f'{self.source}'
                        list_of_lagged_ts.append(latest_price)
                        print(
                            f'{self.version}({self.source}):{latest_price.pair_code} is NOT within current time, difference: {lag} or prices doesn\'t include sub-pennies ({latest_price.prices})')
                return list_of_lagged_ts
            case _:
                for latest_price in self.list_of_latest_prices:
                    latest_ts = datetime.strptime(
                        latest_price.ts, '%Y-%m-%dT%H:%M:%SZ')
                    lag = latest_price.current_ts - latest_ts
                    if lag >= self.three_min_lag and lag < self.five_min_lag:
                        print(
                            f'{self.version}({self.source}): {latest_price.pair_code} is within 3-4 minutes of current time, difference: {lag}')
                    else:
                        self.lag_failure_counter += 1
                        latest_price.version = f'{self.version}'
                        latest_price.source = f'{self.source}'
                        list_of_lagged_ts.append(latest_price)
                        print(
                            f'{self.version}({self.source}): {latest_price.pair_code} is NOT within 3-4 minutes of current time, difference: {lag}')
                return list_of_lagged_ts
