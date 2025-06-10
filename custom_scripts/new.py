import json

string = "['FRM']"
try:
    lista = json.loads(string)
    print(lista)  # Borde skriva ut: ['FRM']
except json.JSONDecodeError as e:
    print(f"Fel: {e}")