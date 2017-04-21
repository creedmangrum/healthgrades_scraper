import requests
import ipdb

from constants import specialties, specialties_to_search


base_url = 'https://www.healthgrades.com/api3/autosuggest/what'
alpha = 'abcdefghijklmnopqrstuvwxyz'
# specialties = set()
search_params = {
	'pt': '40.59135,-74.09885'
}

# for char1 in alpha:
# 	for char2 in alpha:
# 		search_params['term'] = str(char1 + char2)
# 		print(search_params['term'])
# 		r = requests.get(base_url, search_params)

# 		response = r.json()
# 		categories = response.get('response').get('categories')
# 		specialty = [category for category in categories if category['category'] == 'Specialty']
# 		if specialty:
# 			suggestions = specialty[0].get('suggestions')
# 			suggestion_values = [suggestion['value'] for suggestion in suggestions]

# 			specialties.update(suggestion_values)

ipdb.set_trace()