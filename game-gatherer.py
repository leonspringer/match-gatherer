#!/usr/bin/env python
from bs4 import BeautifulSoup
import urllib
import requests
import json
import re


video_title = []

url = "http://www.fullmatchesandshows.com"
#url = "http://www.fullmatchesandshows.com/2017/01/08/villarreal-vs-barcelona-highlights-full-match-2/"
page = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"})
soup = BeautifulSoup(page.content)

if url == "http://www.fullmatchesandshows.com" or url == "http://www.fullmatchesandshows.com/":
    # Main page links
    urls = []
    data_configs = []
    for module in soup.find_all(class_="td-module-thumb"):
        url = module.find('a')
        urls.append(url.attrs['href'])
    for url in urls:
        print ('[+] Checking: {0}'.format(url)) 
        page = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"})
        sub_soup = BeautifulSoup(page.content)
        for post_content in sub_soup.find_all("div", class_="td-post-content"):
            data_configs.append(post_content.find_all("script")[1])

else:
    # Individual link
    data_configs = []
    for post_content in soup.find_all("div", class_="td-post-content"):
        data_configs.append(post_content.find_all("script")[1])
        print ('[+] Checking: {0}'.format(url))


def get_links():
    json_urls = []
    video_urls = []
    for data_config in data_configs:
        if "zeus.json" in str(data_config):
            #print data_config

            reg = "\/\/((\w+\.*\w+\.\w+)\/(\d+)\/(\w+)\/(\w\d)\/(\d+)\/(\w+\.\w+))"
            data_config = re.findall(reg, str(data_config))
            json_build_url = "https://" + data_config[0][0]
            json_urls.append(json_build_url)
            video_build_url = 'https://cdn.video.playwire.com/' + data_config[0][2] + '/' + data_config[0][3] + '/' + data_config[0][5] + '/video-sd.mp4'
            video_urls.append(video_build_url)
        else:
            print  "nope"
    return json_urls, video_urls

def print_json_object(json_content):
    for j_object in json_content:
        video_title.append(j_object['settings']['title'])
    return video_title

def parse_remote_json(urls):
    json_content = []
    if type(urls) == list:
        for url in urls:
            try:
                res = requests.get(url)
                json_load_content = json.loads(res.content)
                json_content.append(json_load_content)
            except:
                print('Json url malformed: {0}'.format(url))
        return json_content
    else:
        try:
            res = requests.get(urls)
            json_load_content = json.loads(res.content)
            json_content.append(json_load_content)
        except:
            print('Json url malformed: {0}'.format(urls))
        return json_content

json_urls, video_urls = get_links()
json_content = parse_remote_json(json_urls)
video_title = print_json_object(json_content)
print video_title
print video_urls





# # html/body/div[6]/div[2]/div/div[2]/div[1]/div/article/div[2]/div[5]/script

# url = "http://www.fullmatchesandshows.com/2017/01/05/athletic-bilbao-vs-barcelona-highlights/"
# # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"}
# page = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"})
# tree = html.fromstring(page.content)


# soup = BeautifulSoup(page)

# html.tostring(tree)
# acp_content = tree.xpath('//*[@id="zeus_1483728924478"]')
# data_config = tree.xpath('//*[@id="acp_content"]/script')



# print 'Buyers: ', data_config