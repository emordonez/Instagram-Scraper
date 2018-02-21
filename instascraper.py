import json
import re
import requests
import time

import selenium.webdriver as webdriver

from bs4 import BeautifulSoup
from math import ceil

def scroll_to_bottom(webdriver):
	webdriver.execute_script(
		'window.scrollTo(0, document.body.scrollHeight);'
	)
	return

def get_likes(soup):
	meta_data = soup.find("meta", property="og:description")
	likes = meta_data["content"].split(" ")[0]
	likes = int(likes.strip('\'').replace(',',''))
	
	return likes

def get_location(soup):
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
	url = input("Enter the URL of the Instagram account: ")
	print("Opening Instagram...")
	
	driver = webdriver.Chrome()
	driver.get(url)
	driver.set_window_size(300, 6000)

	scroll_max = int(input("\nHow many photos does this account have? "))/12
	scroll_max = ceil(scroll_max)
	time.sleep(3)
	print("Scrolling through the feed...")
	scroll_to_bottom(driver)

	clickin = driver.find_element_by_link_text('Load more')
	if clickin.click(): scroll_to_bottom(driver)

	scroll_counter = 0
	while scroll_counter < scroll_max:
		time.sleep(5)
		scroll_to_bottom(driver)
		scroll_counter += 1
		print("On scroll {} of {}.".format(str(scroll_counter), str(scroll_max)))

	print("\nAll photos loaded.")
	print("Getting photo links...\n")

	soup = BeautifulSoup(driver.page_source, 'html.parser')

	photo_links = []
	total_likes = []
	location_tags = []

	ig = 'http://www.instagram.com'

	photo_counter = 0
	for link in soup.find_all('a'):
		if '/p/' in link.get('href'):
			photo_counter += 1
			extension = link.get('href')
			photo_links.append(ig + extension)
			print("{} - ".format(str(photo_counter)) + extension)

	print("\nPhoto links done.")
	print("Getting likes and locations...\n")

	counter = 0
	total = len(photo_links)
	for url in photo_links:
		response = requests.get(url)
		html = response.content
		soup = BeautifulSoup(html, 'html.parser')

		likes = get_likes(soup)
		location = re.sub(r'[^\x00-\x7f]',r'', get_location(soup))
		
		total_likes.append(likes)
		location_tags.append(location)

		counter += 1
		print("{} of {} - {} likes at {}".format(str(counter), str(total), str(likes), location))

	print("\nGot total likes and locations.")
	print("Zipping and sorting lists...\n")

	zipped_list = zip(total_likes, location_tags, photo_links)
	sorted_list = sorted(zipped_list, key=lambda x: -x[0])

	print("Lists zipped and sorted.")

	with open('output.txt', 'a') as f:
		for item in sorted_list:
			f.write('{}\t{}\t{}\n'.format(str(item[0]), item[1], item[2]))

	print("\nDone! List of photos ranked by likes with locations saved in 'output.txt'")

if __name__ == '__main__':
	main()