
import argparse
from requests import (exceptions)
from json import (decoder)
from typing import List
from custom_exceptions.custom_exception import ArgumentError
from factory.obj_box.latest_prices_obj import LatestPricesObj
from my_utils.myUtils import get_logger
from factory.latest_prices import LatestPrices

from lag_check import LagChecker

logger = get_logger("Main")

parser = argparse.ArgumentParser()
parser.add_argument('-r',
                    '--region',
                    nargs='?',
                    type=str,
                    help='Please Specify A Region (e.g., e (east), w (west))',)
parser.add_argument('-v',
                    '--version',
                    nargs='?',
                    type=str,
                    help='Please Specify A Version (e.g., v1,v2,v3)',)
parser.add_argument('-s',
                    '--source',
                    nargs='?',
                    type=str,
                    help='Please Specify A Source (e.g., 2000,10500)',)
parser.add_argument('-pc',
                    '--pair_codes',
                    nargs='+',
                    type=str,
                    help='Please Specify Pair Code, or List of Codes (e.g., ETH-USD or [ETH-USD,XBT-USD,XLT-USD])',)
parser.add_argument('-t',
                    '--token',
                    nargs='?',
                    type=str,
                    help='Add Bearer Token for Authorized Run',)
parser.add_argument('run_all',
                    nargs='?',
                    type=str,
                    help='Runs All Sources for Each Version Using Pair Code Set',)

args = parser.parse_args()

try:
    if args.token is None:
        raise ArgumentError("Invalid Token")
except ArgumentError as e:
    logger.error('Please add Bearer Token for authorized run')
else:
    token = f'{args.token}'
    logger.info('Token is valid - Starting Run')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    if args.version is not None and args.source is not None:
        latest_prices = LatestPrices(headers=headers,
                                     region=args.region,
                                     version=args.version,
                                     source=args.source,
                                     pair_codes=args.pair_codes)
        
        try:
            list_of_latest_prices = latest_prices.parse_latest_prices()
            list_of_missing_latest_pairs = latest_prices.get_list_of_missing_latest_pairs()

            lag_checker = LagChecker(list_of_latest_prices=list_of_latest_prices,
                                    source=args.source,
                                    version=args.version,)

            list_of_lagged_ts = lag_checker.calculate_latencies()

            if (lag_checker.lag_failure_counter == 0 and len(list_of_missing_latest_pairs) == 0):
                logger.info(f'ALL Tests Passed')
            elif list_of_missing_latest_pairs is not None:
                logger.info(
                    f'Pairs that are missing: {list_of_missing_latest_pairs}')
            else:
                logger.info(f'Pairs that failed:')
                for latest_price in list_of_lagged_ts:
                    logger.info(f'{latest_price.__str__()}')
                if list_of_missing_latest_pairs is not None:
                    logger.info(
                        f'Pairs that are missing: {list_of_missing_latest_pairs}')
        except exceptions.JSONDecodeError as e:
            logger.info(f'Please use valid bearer token')
        except decoder.JSONDecodeError as e:
            logger.info(f'Please use valid bearer token')
            
    elif args.run_all:
        was_token_granted = True
        sources = ['2000', '10500']
        latest_prices_v1: List[LatestPricesObj] = []
        latest_prices_v3: List[LatestPricesObj] = []
        list_of_missing_pairs_v1: List[str] = []
        list_of_missing_pairs_v3: List[str] = []

        for source in sources:
            v1 = LatestPrices(headers=headers,
                            region=args.region,
                            version='v1',
                            source=source,
                            pair_codes=args.pair_codes)
            list_of_missing_pairs_v1 = v1.get_list_of_missing_latest_pairs()
            try:
                lag_checker_v1 = LagChecker(list_of_latest_prices=v1.parse_latest_prices(),
                                            source=source,
                                            version='v1',)
            except exceptions.JSONDecodeError as e:
                logger.info(f'****Please use valid bearer token****')
                was_token_granted = False
                break
            else:
                list_of_v1_lagged_ts: List[LatestPricesObj] = lag_checker_v1.calculate_latencies()
                
            if source != '10500':
                v3 = LatestPrices(headers=headers,
                                region=args.region,
                                version='v3',
                                source=source,
                                pair_codes=args.pair_codes)
                list_of_missing_pairs_v3 = v3.get_list_of_missing_latest_pairs()
                try:
                    lag_checker_v3 = LagChecker(list_of_latest_prices=v3.parse_latest_prices(),
                                                source=source,
                                                version='v3',)
                except exceptions.JSONDecodeError as e:
                    logger.info(f'****Please use valid bearer token****')
                    was_token_granted = False
                    break
                else:
                    list_of_v3_lagged_ts: List[LatestPricesObj] = lag_checker_v3.calculate_latencies()

        # logger.info(f'Length of v1 -> {len(latest_prices_v1)}')
        # logger.info(f'Length of v3 -> {len(latest_prices_v3)}')
        
        if was_token_granted is True:
            if ((lag_checker_v1.lag_failure_counter == 0) and 
                (lag_checker_v3.lag_failure_counter == 0) and 
                (list_of_missing_pairs_v1 is None) and 
                (list_of_missing_pairs_v3 is None)):
                logger.info(f'\nALL Tests Passed')
            else:
                logger.info(
                    f'\nPairs that are missing in v1: {"None" if len(list_of_missing_pairs_v1)==0 else list_of_missing_pairs_v1}')
                logger.info(
                    f'Pairs that are missing in v1: {"None" if len(list_of_missing_pairs_v3)==0 else list_of_missing_pairs_v3}')
                
                logger.info(
                    f'Pairs that failed in v1: {"None" if len(list_of_v1_lagged_ts)<=0 else ""}')
                for latest_price in list_of_v1_lagged_ts:
                    logger.info(f'{latest_price.__str__()}')
                logger.info(
                    f'Pairs that failed in v3: {"None" if len(list_of_v3_lagged_ts)<=0 else ""}')
                for latest_price in list_of_v3_lagged_ts:
                    logger.info(f'{latest_price.__str__()}')
    else:
        logger.info('Checking other arguments')
