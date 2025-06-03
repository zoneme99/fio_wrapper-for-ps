from statistics import quantiles
from fio_wrapper import FIO
import json
import asyncio

# Initialize FIO client
fio = FIO()

# Get DW ticker information from all exchanges
material = fio.Exchange.get('DW.NC1')
#material = fio.Recipe.all()
# Replace 'your_file.json' with the actual filename
with open('custom_scripts/all_recipes.json', 'r') as f:
    data = json.load(f)





def async_recipe_returns(recipes):
    
    def gather_ticker_inputs(recipes):
        input_tickers = list()
        for recipe in recipes:
            for input_item in recipe['Inputs']:
                if len(input_item) == 0:
                    continue
                else:
                    if not input_item['Ticker'] in input_tickers:
                        input_tickers.append(input_item['Ticker'])
        return input_tickers
    
    async def ask_price(ticker, exchange_ticker):
        try:
            print(f"Requesting {ticker}.{exchange_ticker}...")
            ticker_data = await asyncio.to_thread(lambda: fio.Exchange.get(f'{ticker}.{exchange_ticker}'))
        except Exception as e: 
            print(f"Error with {ticker}: {e}")
            return 'error'
        price = ticker_data.Ask
        print(f"Success: {ticker} = {price}")
        return price

    async def gather_ask_price(input_tickers, exchange_ticker):
        tasks = [ask_price(ticker, exchange_ticker) for ticker in input_tickers]
        results = await asyncio.gather(*tasks)  # await behövs här
        print("Alla uppgifter klara:", results)
    
    input_tickers = gather_ticker_inputs(recipes)
    result = asyncio.run(gather_ask_price(input_tickers, 'NC1'))
    print(result)


                
    #Ask_price[inputs['Ticker']] = fio.Exchange.get(f'{inputs['Ticker']}.NC1').Ask

async_recipe_returns(data)



        #print(key, recipe[key])
    #break
                #for ticker, quantity in dict2.values():
                    #print(ticker)
                    #print(f'nice ticker: {ticker} and nice amount {quantity}')
# Print results
#print(material.model_dump_json())