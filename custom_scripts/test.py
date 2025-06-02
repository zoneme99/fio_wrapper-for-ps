from statistics import quantiles
from fio_wrapper import FIO
import json

# Initialize FIO client
fio = FIO()

# Get DW ticker information from all exchanges
#material = fio.Exchange.get('DW.NC1')
#material = fio.Recipe.all()
# Replace 'your_file.json' with the actual filename
with open('custom_scripts/all_recipes.json', 'r') as f:
    data = json.load(f)


for recipe in data:
    for key in recipe.keys():
        for inputs in recipe['Inputs']:
            print(inputs, fio.Exchange.get(f'{inputs['Ticker']}.NC1')['Ask'])
        #print(key, recipe[key])
    #break
                #for ticker, quantity in dict2.values():
                    #print(ticker)
                    #print(f'nice ticker: {ticker} and nice amount {quantity}')
# Print results
#print(material.model_dump_json())