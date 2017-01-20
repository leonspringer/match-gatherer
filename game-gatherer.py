#!/usr/bin/env python
from bs4 import BeautifulSoup
import argparse
import urllib
import requests
import json
import re
import datetime


video_title = []
# out_file = 'gamelinks.html' 

#url = "http://www.fullmatchesandshows.com"
#url = "http://www.fullmatchesandshows.com/2017/01/08/villarreal-vs-barcelona-highlights-full-match-2/"


def get_links(url, verbose):
    page = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"})
    soup = BeautifulSoup(page.content)
    if url == "http://www.fullmatchesandshows.com" or url == "http://www.fullmatchesandshows.com/":
        # Main page links
        urls = []
        data_configs = []
        #Get links on first page
        for module in soup.find_all(class_="td-module-thumb"):
            url = module.find('a')
            urls.append(url.attrs['href'])
        for url in urls:
            sub_urls = []
            print ('[+] Checking: {0}'.format(url))
            page = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"})
            sub_soup = BeautifulSoup(page.content)
            # Get first content on link on first page (typically a highlight)
            for post_content in sub_soup.find_all("div", class_="td-post-content"):
                data_configs.append(post_content.find_all("script")[1])
            # Look through MOTD, 1st Half, 2nd Half, etc...
            for item in sub_soup.find_all(lambda tag: tag.name == 'li' and tag.get('class') == ['button_style']):
                sub_url = item.find("a")
                sub_urls.append(sub_url.attrs['href'])
            for sub_url in sub_urls:
                if verbose:
                    print ('[+] Getting additional content: {0}'.format(sub_url)) 
                page = requests.get(sub_url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"})
                sub_soup = BeautifulSoup(page.content)
                for post_content in sub_soup.find_all("div", class_="td-post-content"):
                    data_configs.append(post_content.find_all("script")[1])
        return data_configs
    else:
        # Individual link
        sub_urls = []
        data_configs = []
        # Get first content on link on first page (typically a highlight)
        for post_content in soup.find_all("div", class_="td-post-content"):
            data_configs.append(post_content.find_all("script")[1])
            print ('[+] Checking: {0}'.format(url))
        # Look through MOTD, 1st Half, 2nd Half, etc...
        for item in soup.find_all(lambda tag: tag.name == 'li' and tag.get('class') == ['button_style']):
            sub_url = item.find("a")
            sub_urls.append(sub_url.attrs['href'])
        for sub_url in sub_urls:
            if verbose:
                print ('[+] Checking: {0}'.format(sub_url)) 
            page = requests.get(sub_url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"})
            sub_soup = BeautifulSoup(page.content)
            for post_content in sub_soup.find_all("div", class_="td-post-content"):
                data_configs.append(post_content.find_all("script")[1])
        return data_configs

def build_urls(data_configs):
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

def run(url, html_off, out_file, verbose):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_configs = get_links(url, verbose)
    json_urls, video_urls = build_urls(data_configs)
    json_content = parse_remote_json(json_urls)
    video_title = print_json_object(json_content)
    if not html_off:
        if verbose:
            if type(out_file)==str:
                print "Writing output file to: {0}".format(out_file)
            else:
                print "Writing output file to: {0}".format(out_file[0])
        if type(out_file)==str:
            html_file = open(out_file,"a+")
        else:
            html_file = open(out_file[0],"a+")
        for v_url, v_title in zip(video_urls, video_title):
            print v_title
            print v_url
            print "--------------"
            if not html_off:
                html_file.write('{0}   -   <a href ="{1}">{2}</a><br/>\n'.format(now, v_url, v_title))
        html_file.close()
    else:
        for v_url, v_title in zip(video_urls, video_title):
            print v_title
            print v_url
            print "--------------"
            
def parse_args():
    parser = argparse.ArgumentParser()     
    parser.add_argument('-f', '--file', nargs=1, default='links.html', dest='out_file', help='Output html file name and location')
    parser.add_argument('-o', '--html_off', action='store_true', default=False, help='Disable html file output')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('url', nargs='?', default='http://www.fullmatchesandshows.com')
    args = parser.parse_args()
    return parser.parse_args()

if __name__ == '__main__':
    parser = parse_args()
    links = run(parser.url, parser.html_off, parser.out_file, parser.verbose)
    






