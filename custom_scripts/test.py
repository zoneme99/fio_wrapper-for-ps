from statistics import quantiles
from fio_wrapper import FIO
import json
import asyncio

# Initialize FIO client
fio = FIO()

# Get DW ticker information from all exchanges
#material = fio.Exchange.get('DW.NC1')
#material = fio.Recipe.all()
# Replace 'your_file.json' with the actual filename
#with open('custom_scripts/all_recipes.json', 'r') as f:
#    data = json.load(f)

#print(type(json.loads(fio.Exchange.get('DW.NC1').model_dump_json())))
#exit()

data = json.loads(fio.Recipe.all().model_dump_json())





def async_market_fetch(recipes):
    
    def gather_tickers(recipes):
        tickers = list()
        for recipe in recipes:
            #iterating all inputs
            for input_item in recipe['Inputs']:
                if len(input_item) == 0:
                    continue
                else:
                    if not input_item['Ticker'] in tickers:
                        tickers.append(input_item['Ticker'])
            #Iterating all outputs
            for input_item in recipe['Outputs']:
                if len(input_item) == 0:
                    continue
                else:
                    if not input_item['Ticker'] in tickers:
                        tickers.append(input_item['Ticker'])
        return tickers
    
    async def ticker_info(ticker, exchange_ticker):
        try:
            print(f"Requesting {ticker}.{exchange_ticker}...")
            ticker_data = await asyncio.to_thread(lambda: fio.Exchange.get(f'{ticker}.{exchange_ticker}'))
        except Exception as e: 
            print(f"Error with {ticker}: {e}")
            return None
        info = json.loads(ticker_data.model_dump_json())
        print(f"Success: {ticker}")
        return info

    async def gather_ticker_info(ticker_list, exchange_ticker):
        tasks = [ticker_info(ticker, exchange_ticker) for ticker in ticker_list]
        results = await asyncio.gather(*tasks)  # await behövs här
        print("All input hämtad:")
        return results

    
    tickers = gather_tickers(recipes)
    result = asyncio.run(gather_ticker_info(tickers, 'NC1'))
    market_info = dict(zip(tickers, result))
    return market_info
  



def recipe_value_returns(recipes, market_info, buildings_filter):
    profit_recipes = list()
    input_sum = 0
    output_sum = 0
    for recipe in recipes:
        if recipe['BuildingTicker'] in buildings_filter:

            for input in recipe['Inputs']:
                input_sum += market_info[input['Ticker']]['Ask'] * input['Amount']
            for output in recipe['outputs']:
                output_sum += market_info[output['Ticker']]['Bid'] * output['Amount']
            percent_profit = (output_sum - input_sum) / input_sum




market_info = async_market_fetch(data)




        #print(key, recipe[key])
    #break
                #for ticker, quantity in dict2.values():
                    #print(ticker)
                    #print(f'nice ticker: {ticker} and nice amount {quantity}')
# Print results
#print(material.model_dump_json())