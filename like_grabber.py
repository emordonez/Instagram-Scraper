import time
import requests
import selenium.webdriver as webdriver
from bs4 import BeautifulSoup


def get_likes(url):
	response = requests.get(url)
	html = response.content
	soup = BeautifulSoup(html, 'html.parser')
	meta_data = soup.find("meta", property="og:description")
	likes = meta_data["content"].split(" ")[0]
	likes = int(likes.strip('\'').replace(',',''))

	return likes

def main():
	url = input("Enter the URL of the Instagram account: ")

	driver = webdriver.Chrome()
	driver.get(url)
	driver.set_window_size(300, 6000)

	print("Opening Instagram...")
	time.sleep(10)
	print("Scrolling through the feed...")

	driver.execute_script(
		'window.scrollTo(0, document.body.scrollHeight);'
	)
	clickin = driver.find_element_by_link_text('Load more')

	if clickin.click():
		driver.execute_script(
			'window.scrollTo(0, document.body.scrollHeight);'
		)

	scroll_counter = 0
	while scroll_counter <= 200:
		time.sleep(5)
		driver.execute_script(
			'window.scrollTo(0, document.body.scrollHeight);'
		)
		scroll_counter += 1
		print("On scroll {} of 200.".format(str(scroll_counter)))

	print("All photos loaded.")
	print("Getting photo extensions...")

	soup = BeautifulSoup(driver.page_source, 'html.parser')
	
	extension_list = []
	photo_likes = []
	ig = 'http://www.instagram.com'

	photo_counter = 0
	for link in soup.find_all('a'):
		if '/p/' in link.get('href'):
			photo_counter += 1
			extension = link.get('href')
			extension_list.append(extension)
			print("{} - ".format(str(photo_counter)) + extension)


	print("Photo extensions done.")
	print("Getting photo likes...")

	for extension in extension_list:
		url = ig + extension
		likes = get_likes(url)
		photo_likes.append(likes)
		print("{} - ".format(str(likes)) + url)

	print("Got photo likes.")
	print("Zipping and sorting lists...")

	zip_list = zip(extension_list, photo_likes)
	sorted_list = sorted(zip_list, key=lambda x:(-x[1],x[0]))

	print("List zipped and sorted.")

	with open('output.txt', 'w') as output_list:
		for item in sorted_list:
			output_list.write('{}\t\t{}\n'.format(item[1], item[0]))

	print("Done!")

if __name__ == "__main__":
	main()