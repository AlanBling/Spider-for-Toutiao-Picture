# Author: Alan Zhang
# Date: 2018.08.28

# In God we trust.

import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool

def get_page(offset):
	# 需要七个参数
	params = {
		'offset': offset,
		'format': 'json',
		'keyword': '街拍',
		'autoload': 'true',
		'count': '20',
		'cur_tab': '1',
		'from': 'search_tab'
	}

	# 拼接url
	url = 'https://www.toutiao.com/search_content/?' + urlencode(params)

	try:
		response = requests.get(url)
		if response.status_code == 200:
			return response.json()
	except requests.ConnectionError:
		return None


def get_images(json):
	if json.get('data'):
		for item in json.get('data'):
			title = item.get('title')
			images = item.get('image_list')
			# 这里注意：并不是所有的item都有'title'，做一个if判断，将没有的剔除掉
			if title:
				for image in images:
					image_url = ('http:'+ str(image.get('url'))).replace("list", "large")
					yield {
						'image': image_url,
						'title': title
					}

def save_image(item):
	if not os.path.exists(item.get('title')):
		os.mkdir(item.get('title'))
	try:
		response = requests.get(item.get('image'))
		if response.status_code == 200:
			file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
			if not os.path.exists(file_path):
				with open(file_path, 'wb') as f:
					f.write(response.content)
			else:
				print('Already Download', file_path)
	except requests.ConnectionError:
		print('Failed to Save Image')

def main(offset):
	json = get_page(offset)
	for item in get_images(json):
		print(item)
		save_image(item)

GROUP_START = 1
GROUP_END = 20

if __name__ == '__main__':
	pool = Pool()
	groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
	pool.map(main, groups)
	pool.close()
	pool.join()