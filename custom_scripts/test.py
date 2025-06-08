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

recipes = json.loads(fio.Recipe.all().model_dump_json())





def async_market_fetch(recipes, exchange_ticker):
    
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
    result = asyncio.run(gather_ticker_info(tickers, exchange_ticker))
    market_info = dict(zip(tickers, result))
    return market_info
  



def recipe_value_returns(recipes, market_info, buildings_filter=[], input_filter=[], output_filter=[], sort_method=True):
    profit_recipes = list()
    profit_string = list()
    for recipe in recipes:
        input_mem = True
        output_mem = True
        input_sum = 0
        input_tickers = list()
        output_sum = 0
        output_tickers = list()
        if recipe['BuildingTicker'] in buildings_filter or len(buildings_filter) == 0:
            error = False
            for input in recipe['Inputs']:
                if len(input) == 0:
                    continue
                if input['Ticker'] in input_filter or len(input_filter) == 0:
                    input_mem = False
                ask_price = market_info[input['Ticker']]['Ask']
                if ask_price == None:
                    error = True
                    break
                input_sum +=  ask_price * input['Amount']
                input_tickers.append(input['Ticker'])
            for output in recipe['Outputs']:
                if len(output) == 0:
                    continue
                if output['Ticker'] in output_filter or len(output_filter) == 0:
                    output_mem = False            
                bid_price = market_info[output['Ticker']]['Bid']
                if bid_price == None:
                    error = True
                    break
                output_sum += bid_price * output['Amount']
                output_tickers.append(output['Ticker'])
            if len(input_tickers) == 0 or len(output_tickers) == 0 or error == True or input_mem or output_mem:
                continue
            percent_profit = ((output_sum - input_sum) / input_sum)*100
            profit = output_sum - input_sum
            profit_hour = profit / (recipe['TimeMs'] / (1000*60*60))
            profit_recipes.append((output_tickers, input_tickers, recipe['BuildingTicker'] ,percent_profit, profit, profit_hour))
    match sort_method:
        case 'percentage':
            filter_num = 3
        case 'profit':
            filter_num = 4
        case 'time':
            filter_num = 5

    profit_recipes = sorted(profit_recipes, key= lambda x: x[filter_num], reverse=True)

    for output, input, building, perc_profit, profit, profit_hour in profit_recipes:
        profit_string.append((f'Outputs: {output}, Inputs: {input}, Building: [{building}], Profit %/cash: {perc_profit:.2f} % / {int(profit)} Profit/Hour: {profit_hour:.2f} P/H'))
    return profit_string




#market_info = async_market_fetch(recipes, 'NC1')
with open('custom_scripts/market_info.json', 'r') as f:
    market_info = json.load(f)

pioneers = ['BMP','FRM','FP','INC','PP1', 'SME', 'WEL']
sort_methods = ['percentage','profit', 'time']
profit_list = recipe_value_returns(recipes, market_info, buildings_filter=['PP1'], sort_method=sort_methods[1])
for profit in profit_list:
    print(profit)
