from fio_wrapper import FIO
import json
import asyncio
import os
import csv


fio = FIO()

path_to_csv = 'custom_scripts/custom.csv'

pioneers = ['BMP','FRM','FP','INC','PP1', 'SME', 'WEL']
settlers = ['CHP', 'CLF', 'EDM', 'FER', 'FS', 'GF', 'HYF', 'PAC', 'PPF', 'POL', 'PP2', 'REF', 'UPF', 'WPL']
technicians = ['CLR', 'ELP', 'ECA', 'HWP', 'IVP', 'LAB', 'MCA', 'ORC', 'PHF', 'PP3', 'SKF', 'SCA', 'SD', 'TNP']
engineers = ['AML', 'ASM', 'APF', 'DRS', 'PP4', 'SE', 'SPP']
scientists = ['AAF', 'EEP', 'SL', 'SPF']
sort_methods = ['percentage','profit', 'time']

start_menu = ['Go to preset filters', 'Go to custom filters',
        'Search all recipes by profit/hour', 'Search all recipes by profit in %',
    'Search all recipes by profit per order', 'Refresh market data', 'Exit']

preset_menu = ['Pioneers','Settlers', 'Technicians', 'Engineers', 'Scientists', 'Back to start menu']



def read_custom_csv(path):
    alla_rader = list()
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
    
        for rad in reader:
            alla_rader.append(rad)
        return alla_rader

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
  



def recipe_value_returns(recipes, market_info, buildings_filter=[], input_filter=[], output_filter=[], sort_method='time'):
    os.system('cls' if os.name == 'nt' else 'clear')
    profit_recipes = list()
    for recipe in recipes:
        input_mem = True
        output_mem = True
        input_sum = 0
        input_tickers = list()
        output_sum = 0
        output_tickers = list()
        if recipe['BuildingTicker'] in buildings_filter or len(buildings_filter) == 0:
            error = False
            for input_item in recipe['Inputs']:
                if len(input_item) == 0:
                    continue
                if input_item['Ticker'] in input_filter or len(input_filter) == 0:
                    input_mem = False
                if not market_info[input_item['Ticker']] == None:
                    ask_price = market_info[input_item['Ticker']]['Ask']
                else:
                    error = True
                    break
                if ask_price == None:
                    error = True
                    break
                input_sum +=  ask_price * input_item['Amount']
                input_tickers.append(input_item['Ticker'])
            for output in recipe['Outputs']:
                if len(output) == 0:
                    continue
                if output['Ticker'] in output_filter or len(output_filter) == 0:
                    output_mem = False
                if not market_info[output['Ticker']] == None:                
                    bid_price = market_info[output['Ticker']]['Bid']
                else:
                    error = True
                    break
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

    for output, input_item, building, perc_profit, profit, profit_hour in profit_recipes:
        print(f'Outputs: {output}, Inputs: {input_item}, Building: [{building}], Profit %/cash: {perc_profit:.2f} % / {int(profit)} Profit/Hour: {profit_hour:.2f} P/H')
    
    print('')
    input('Press enter to return to menu')

def terminal_menu(title, option_list):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(title)
    print('')
    for index, option in enumerate(option_list):
        print(f'{index+1}. {option}') # starting with 1, easier input on laptop
    while True:
        try:
            num = int(input('Insert number from list: '))
        except ValueError:
            print('Must be a whole number integer!')
            continue
        if 0 < num <= len(option_list):
            return option_list[num-1]
        else:
            print('Number is not in the list!')


    

def main():
    recipes = json.loads(fio.Recipe.all().model_dump_json())
    market_info = async_market_fetch(recipes, 'NC1')
    while True:
        option = terminal_menu('Welcome to RecipeMiner! Look for the most profitable recipe orders on live data on exchange NC1!', start_menu)
        match option:
            case x if x == start_menu[0]:
                while True:
                    preset_option = terminal_menu('Search by these preset filters by buildings in their category sorted by profit/hour', preset_menu)
                    match preset_option:
                        case x if x == preset_menu[0]:
                            recipe_value_returns(recipes, market_info, pioneers)
                            continue
                        case x if x == preset_menu[1]:
                            recipe_value_returns(recipes, market_info, settlers)
                            continue
                        case x if x == preset_menu[2]:
                            recipe_value_returns(recipes, market_info, technicians)
                            continue
                        case x if x == preset_menu[3]:
                            recipe_value_returns(recipes, market_info, engineers)
                            continue
                        case x if x == preset_menu[4]:
                            recipe_value_returns(recipes, market_info, scientists)
                            continue
                        case x if x == preset_menu[5]:
                            break
            case x if x == start_menu[1]:
                custom_data = read_custom_csv(path_to_csv)
                names = list()
                for data in custom_data:
                    names.append(data[0])
                while True:
                    custom_option = terminal_menu('Search by listed custom filters below:', [*names, 'Exit'])
                    if custom_option == 'Exit':
                        break
                    for data in custom_data:
                        if data[0] == custom_option:
                            recipe_value_returns(recipes, market_info, data[1].split(",") if data[1] else [], data[2].split(",") if data[2] else [], data[3].split(",") if data[3] else [], data[4])


            case x if x == start_menu[2]:
                        recipe_value_returns(recipes, market_info, sort_method='time')
                        continue
            case x if x == start_menu[3]:
                        recipe_value_returns(recipes, market_info, sort_method='percentage')
                        continue
            case x if x == start_menu[4]:
                        recipe_value_returns(recipes, market_info, sort_method='profit')
                        continue
            case x if x == start_menu[5]:
                        market_info = async_market_fetch(recipes, 'NC1')
                        continue
            case x if x == start_menu[6]:
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Welcome back for more market manipulation!')
                exit()

main()      