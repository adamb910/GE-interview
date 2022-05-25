import requests
import json

# Opening JSON file
f = open('input_observations.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)

res = requests.post('http://0.0.0.0:91/remapentries', json=data)
print(res.json())