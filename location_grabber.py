import json
import re
import requests

from bs4 import BeautifulSoup

def get_location(url):
	response = requests.get(url)
	html = response.content
	soup = BeautifulSoup(html, 'html.parser')

	script = soup.find('script', text=re.compile('window._sharedData'))
	json_text = re.search(r'^\s*window._sharedData\s*=\s*({.*?})\s*;\s*$', script.string, flags=re.DOTALL | re.MULTILINE).group(1)
	data = json.loads(json_text)
	location_data = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['location']


	if (location_data is not None) and (location_data['has_public_page']):
		location = location_data['name']
	else:
		location = "**NO LOCATION GIVEN**"

	return location

def main():
	ig = 'http://www.instagram.com'
	
	ranking_list = []
	with open('photo_rankings.txt', 'r') as rankings:
		for item in rankings:
			ranking_list.append(item.split())
		
	print("Read ranked likes.")
	print("Now finding photo locations...")

	counter = 0
	total = len(ranking_list)
	for item in ranking_list:
		counter += 1
		url = ig + item[1]	
		item.append(url)	
		try:
			item[1] = get_location(url)
			item[1] = re.sub(r'[^\x00-\x7f]',r'', item[1])

			print("Found {} of {} locations -- {}.".format(str(counter), str(total), item[1]))
		except:
			item[1] = "**NO LOCATION FOUND--CONNECTION TIMED OUT**"
			print("No location found for photo {}--connection timed out.".format(str(counter)))
			pass

	print("All locations found!")
	print("Now saving...")

	counter = 0
	with open('likes_and_locations.txt', 'w') as output:
		for item in ranking_list:
			counter += 1
			output.write("{}\t{}\t{}\n".format(item[0], item[1], item[2]))
			print("Wrote {} of {} items.".format(str(counter), str(total)))

	print("Done!")

if __name__ == "__main__":
	main()