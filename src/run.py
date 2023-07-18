
import argparse
import regex as re
from requests import (get,exceptions)
from json import (decoder)
from typing import List
from custom_exceptions.custom_exception import ArgumentError
from my_utils.myUtils import get_logger
from obj_box.latest_prices_obj import LatestPricesObj
from datetime import (datetime, 
                    timedelta,)

logger = get_logger("Main")

parser = argparse.ArgumentParser()
parser.add_argument('-r',
                    '--region',
                    nargs='?',
                    type = str,
                    help='Please Specify A Region (e.g., e (east), w (west))',)
parser.add_argument('-v',
                    '--version',
                    nargs='?',
                    type = str,
                    help='Please Specify A Version (e.g., v1,v2,v3)',)
parser.add_argument('-s',
                    '--source',
                    nargs='?',
                    type = str,
                    help='Please Specify A Source (e.g., 2000,10500)',)
parser.add_argument('-pc',
                    '--pair_codes',
                    nargs='+',
                    type = str,
                    help='Please Specify Pair Code, or List of Codes (e.g., ETH-USD or [ETH-USD,XBT-USD,XLT-USD])',)
parser.add_argument('-t',
                    '--token',
                    nargs='?',
                    type = str,
                    help='Add Bearer Token for Authorized Run',)
parser.add_argument('run_all',
                    nargs='?',
                    type = str,
                    help='Runs All Sources for Each Version Using Pair Code Set',)


def confirm_portal(portal='https://data-pricing-api.lukka.tech',region=None):
    if(args.region == 'e'):
        portal = "https://data-pricing-east.lukka.tech"
    if(args.region == 'w'):
        portal = "https://data-pricing-west.lukka.tech"
    return portal

def confirm_pair_codes(pair_codes=None):
    if(args.pair_codes is None):
        pair_codes = "XBT-USD,ETH-USD,XLT-USD,BCH-USD,BNB-USD,XEC1-USD"
    else:
        pair_codes = ','.join(args.pair_codes)
    return pair_codes

args = parser.parse_args()

if args.token is None:
    raise ArgumentError("Please add Bearer Token for authorized run")
else:
    token = f'{args.token}'
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
            }
    portal = confirm_portal(region=args.region)
    pair_codes = confirm_pair_codes(pair_codes=args.pair_codes)
    
    five_min_lag = timedelta(minutes=5)
    three_min_lag = timedelta(minutes=3)
    one_min_lag = timedelta(minutes=1)
    
    if args.version is not None and args.source is not None:
        list_of_latest_prices:List[LatestPricesObj] = []
        list_of_missing_latest_pairs = []
        args_url = f'{portal}/{args.version}/pricing/sources/{args.source}/prices?pairCodes={pair_codes}'
        date_now_utc:datetime = datetime.utcnow()
        logger.info(f'Your current Region is: {"West/DR" if args.region=="w" else "East/PROD"}')
        logger.info("Your current time is: " + date_now_utc.strftime('%Y/%m/%d %H:%M:%S'))
        try:
            ###
            ### Latency for command with args is calculated here
            ###
            latency_start = datetime.utcnow()
            response = get(url=args_url, headers=headers)
            latency_end = datetime.utcnow() - latency_start
            latency_end = latency_end.total_seconds()
            
            if not response.text.__contains__("pair"):
                list_of_missing_latest_pairs.append(pair_codes)
            
            for item in response.json():
                current_latest_obj = LatestPricesObj(pair_code=item['pairCode'],
                                                    ts=item['ts'],
                                                    current_ts=date_now_utc,
                                                    prices=item['price'],
                                                    latency=latency_end,)
                logger.info(f'{current_latest_obj.__str__()}')
                list_of_latest_prices.append(current_latest_obj)
        except exceptions.JSONDecodeError as e:
            logger.info(f'Please use valid bearer token')
        except decoder.JSONDecodeError as e:
            logger.info(f'Please use valid bearer token')
        
        five_min_lag = timedelta(minutes=5)
        three_min_lag = timedelta(minutes=3)
        one_min_lag = timedelta(minutes=1)
        prices_failure_counter = 0
        list_of_specified_latencies = []
        if(args.source == '10500'):
            for latest_price in list_of_latest_prices:
                latest_ts = datetime.strptime(latest_price.ts, '%Y-%m-%dT%H:%M:%SZ')
                lag = latest_price.curren_ts - latest_ts
                match = re.compile(r'[0-9]\.[0-9]{3}').search(latest_price.prices)
                if lag >= one_min_lag and match:
                    logger.info(f'{args.version}({args.source}):  {latest_price.pair_code} is within current time: difference: {lag} & prices include sub-pennies ({latest_price.prices})')
                else:
                    prices_failure_counter += 1
                    latest_price.version = f'{args.version}'
                    latest_price.source = f'{args.source}'
                    list_of_specified_latencies.append(latest_price)
                    logger.info(f'{args.version}({args.source}): {latest_price.pair_code} is NOT within current time, difference: {lag} or prices doesn\'t include sub-pennies ({latest_price.prices})')
        else:
            for latest_price in list_of_latest_prices:
                latest_ts = datetime.strptime(latest_price.ts, '%Y-%m-%dT%H:%M:%SZ')
                lag = latest_price.curren_ts - latest_ts
                if lag >= three_min_lag and lag < five_min_lag:
                    logger.info(f'{args.version}({args.source}): {latest_price.pair_code} is within 3-4 minutes of current time, difference: {lag}')
                else:
                    prices_failure_counter += 1
                    latest_price.version = f'{args.version}'
                    latest_price.source = f'{args.source}'
                    list_of_specified_latencies.append(latest_price)
                    logger.info(f'{args.version}({args.source}): {latest_price.pair_code} is NOT within 3-4 minutes of current time, difference: {lag}')
        
        if (prices_failure_counter == 0 and list_of_missing_latest_pairs is None):
            logger.info(f'\nALL Tests Passed')
        elif list_of_missing_latest_pairs is not None:
                logger.info(f'\nPairs that are missing: {list_of_missing_latest_pairs}')
        else:
            logger.info(f'\nPairs that failed:')
            for latest_price in list_of_specified_latencies:
                logger.info(f'{latest_price.__str__()}')
            if list_of_missing_latest_pairs is not None:
                logger.info(f'\nPairs that are missing: {list_of_missing_latest_pairs}')
                
    elif args.run_all:
        pricingv1_url ="/v1/pricing/sources/2000/prices"
        pricingv1_10500_url ="/v1/pricing/sources/10500/prices"
        pricingv3_url ="/v3/pricing/sources/2000/prices"
        
        list_of_latest_pricesv1:List[LatestPricesObj] = []
        list_of_latest_pricesv3:List[LatestPricesObj] = []
        list_of_latest_pricesv1_10500:List[LatestPricesObj] = []
        
        list_of_urls = [pricingv1_url,pricingv1_10500_url,pricingv3_url]
        list_of_all_missing_latest_pairs = []
        
        date_now_utc:datetime
        
        for url in list_of_urls:
            full_url = f'{portal}{url}?pairCodes={pair_codes}'
            date_now_utc:datetime = datetime.utcnow()
            logger.info("Your current time is: " + date_now_utc.strftime('%Y/%m/%d %H:%M:%S'))
            try:
                ###
                ### Latency for run_all is calculated here
                ###
                latency_start = datetime.utcnow()
                response = get(url=full_url, headers=headers)
                latency_end = datetime.utcnow() - latency_start
                latency_end = latency_end.total_seconds()
                
                response = response.json()
            except exceptions.JSONDecodeError as e:
                logger.info(f'Please use valid bearer token')
                break
            except decoder.JSONDecodeError as e:
                logger.info(f'Please use valid bearer token')
                break
            
            for item in response:
                current_latest_obj = LatestPricesObj(pair_code=item['pairCode'],
                                                    ts=item['ts'],
                                                    current_ts=date_now_utc,
                                                    prices=item['price'],
                                                    latency=latency_end)
                logger.info(f'{current_latest_obj.__str__()}')
                if url == pricingv1_url:
                    list_of_latest_pricesv1.append(current_latest_obj)
                elif url == pricingv1_10500_url:
                    list_of_latest_pricesv1_10500.append(current_latest_obj)
                elif url == pricingv3_url:
                    list_of_latest_pricesv3.append(current_latest_obj)
                    
        v1_prices_failure_counter = 0
        v1s10500_prices_failure_counter = 0
        v3_prices_failure_counter = 0
        list_of_affected_latencies:List[LatestPricesObj] = []
        
        for latest_price in list_of_latest_pricesv1:
            latest_ts = datetime.strptime(latest_price.ts, '%Y-%m-%dT%H:%M:%SZ')
            lag = latest_price.curren_ts - latest_ts
            
            # if pair_codes.__contains__('BTC-USD'):
            #     list_of_all_missing_latest_pairs.append(latest_price.pair_code)
            
            exists = not any(x in latest_price.pair_code for x in pair_codes)
            if exists:
                logger.info(f'Pair code: {latest_price.pair_code} exists in pair_codes')
                
                
            if lag >= three_min_lag and lag < five_min_lag:
                logger.info(f'V1(2000): {latest_price.pair_code} is within 3-4 minutes of current time, difference: {lag}')
            else:
                v1_prices_failure_counter += 1
                latest_price.version = 'V1'
                latest_price.source = '2000'
                list_of_affected_latencies.append(latest_price)
                logger.info(f'V1(2000): {latest_price.pair_code} is NOT within 3-4 minutes of current time, difference: {lag}')
            # if any(x in list_of_pair_codes for x in latest_price.pair_code):
            #     list_of_all_missing_latest_pairs.append(latest_price.pair_code)
        
        for latest_price in list_of_latest_pricesv1_10500:
            latest_ts = datetime.strptime(latest_price.ts, '%Y-%m-%dT%H:%M:%SZ')
            lag = latest_price.curren_ts - latest_ts
            match = re.compile(r'[0-9]\.[0-9]{3}').search(latest_price.prices)
                
            if lag <= one_min_lag and match:
                logger.info(f'V1(10500): {latest_price.pair_code} is within current time: difference: {lag} & prices include sub-pennies ({latest_price.prices})')
            else:
                v1s10500_prices_failure_counter += 1
                latest_price.version = 'V1'
                latest_price.source = '10500'
                list_of_affected_latencies.append(latest_price)
                logger.info(f'V1(10500): {latest_price.pair_code} is NOT within current time, difference: {lag} or prices doesn\'t include sub-pennies ({latest_price.prices})')
            # if [x for x in list_of_pair_codes if x != latest_price.pair_code]:
            #     list_of_all_missing_latest_pairs.append(latest_price.pair_code)
                
        for latest_price in list_of_latest_pricesv3:
            latest_ts = datetime.strptime(latest_price.ts, '%Y-%m-%dT%H:%M:%SZ')
            lag = latest_price.curren_ts - latest_ts
            if lag >= three_min_lag and lag < five_min_lag:
                logger.info(f'V3(2000): {latest_price.pair_code} is within 3-4 minutes of current time, difference: {lag}')
            else:
                v3_prices_failure_counter += 1
                latest_price.version = 'V3'
                latest_price.source = '2000'
                list_of_affected_latencies.append(latest_price)
                logger.info(f'V3(2000): {latest_price.pair_code} is NOT within 3-4 minutes of current time, difference: {lag}')
            # if any(x in list_of_pair_codes for x in latest_price.pair_code):
            #     list_of_all_missing_latest_pairs.append(latest_price.pair_code)
        
        
        # if (v1_prices_failure_counter == 0) and (v1s10500_prices_failure_counter == 0) and (v3_prices_failure_counter == 0 and list_of_all_missing_latest_pairs is None):
        if (v1_prices_failure_counter == 0) and (v1s10500_prices_failure_counter == 0) and (v3_prices_failure_counter == 0):
            logger.info(f'\nALL Tests Passed')
        else:
            # logger.info(f'\nPairs that are missing: {"None" if len(list_of_all_missing_latest_pairs)==0 else list_of_all_missing_latest_pairs}')
            logger.info(f'\nPairs that failed: {"None" if len(list_of_affected_latencies)<=0 else ""}')
            for latest_price in list_of_affected_latencies:
                logger.info(f'{latest_price.__str__()}')
    else:
        logger.info('Checking other arguments')

