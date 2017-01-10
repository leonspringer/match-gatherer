#!/usr/bin/env python
import requests
import argparse
import re
import subprocess
import os
import json
import urllib
import datetime


video_title = []
visited_links = []
correct_pattern_links = []
json_correct_pattern_links = []

def get_links(urls, ignore):
    links = []
    ignore_list = ignore.split(',')
    for link in urls:
        valid_link = True
        for ext in ignore_list:
            if ext and link.endswith(ext):
                valid_link = False
                break
        if valid_link:
            links.append(link)
    return links

def clean_url(url):
    if url.endswith('</a>'):
        url = url.replace('</a>', '')
    if url.startswith('//'):
        url = 'http:' + url
    return url

def get_all_website_links(url, ignore):
    links = []
    urls = []
    try:
        if url in visited_links:
            print('[*] Ignoring {0}'.format(url))
            return []
        resp = requests.get(clean_url(url))
        urls = re.findall('[http|https]?//(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', resp.content)
        visited_links.append(url)
        links = get_links(urls, ignore)
        print('[+] Analyzed {0}'.format(url))
    except Exception as e:
        print('[-] Could not connect to {0}. Error: {1}'.format(url, e))
    return links

def find_pattern_links(pattern, links):
    pattern_links = []
    for link in links:
        if pattern in link:
            print('[+] Correct pattern link found: {0}'.format(link))
            pattern_links.append(link)
            correct_pattern_links.append(link)
    return pattern_links

def is_valid_domain(url, domains):
    valid_domain = False
    domains_list = domains.split(',')
    for domain in domains_list:
        if domain in url:
            valid_domain = True
            break
    return valid_domain

def handle_recursion(website_links, correct_links,  depth, ignore, pattern, domains):
    if depth <= 0:
        return correct_links
    else:
        for link in website_links:
            #print link
            if is_valid_domain(link, domains):
                correct_links = parse_web(link, pattern, depth-1, ignore, domains)
    return correct_links
    

def parse_web(url, pattern, depth=2, ignore='', domains=''):
    if is_valid_domain(url, domains):
        links = get_all_website_links(url, ignore)
        found_correct_links = find_pattern_links(pattern, links)
        return handle_recursion(links, found_correct_links, depth, ignore, pattern, domains)
    return []


def print_json_object(json_content):
    for j_object in json_content:
        video_title.append(j_object['settings']['title'])
    return video_title
    # try: 
    #     if type(json_content) == list:
    #         for j_object in json_content:
    #             print '1'
    #             video_title.append(json_content['settings']['title'])
    #         return video_title
    #     elif json_content.get('settings'):
    #         print '2'
    #         return json_content['settings']['title']
    #     elif json_content.get('title'):
    #         print '3'
    #         return json_content['title']
    #     else:
    #         print '4'
    #         return json_content
    # except Exception as e:
    #         print('Json content malformed or missing: {0}'.format(json_content, e))
    #         quit()
    # # html_file = open('links.htm',"a+")
    # # html_file.write('<p>{0}</p>\n'.format(json_content['settings']['title']))
    # # html_file.close()
    # print 'returns:'
    # print video_title
    # return video_title


def parse_remote_json(urls):
    json_content = []
    for url in urls:
        try:
            res = requests.get(url)
            json_load_content = json.loads(res.content)
            json_content.append(json_load_content)
        except:
            print('Json url malformed: {0}'.format(url))
    return json_content

def build_final_urls(links):
    final_urls = []
    final_json_urls = []
    for link in links:
        try:
            if link.startswith('//'):
                link = link[2:]
            data = link.split('/')
            final_url = 'https://cdn.video.playwire.com/' + data[1] + '/videos/' + data[4] + '/video-sd.mp4'
            final_urls.append(final_url)
            final_json_url = 'https://config.playwire.com/' + data[1] + '/videos/v2/' + data[4] + '/zeus.json'
            final_json_urls.append(final_json_url)
        except:
            print('Manifest url malformed: {0}'.format(link))
    return final_urls, final_json_urls

def download_files(links):
    success = True
    path = os.path.join(os.path.expanduser('~'), 'Desktop')
    for link in links:
        print('[+] Downloading {0}'.format(link))
        ret = urllib.urlretrieve(link, path + "\\file.mp4")
        #ret = subprocess.call(['wget','-P', path, link])
        if ret != 0:
            print('[+] An error occurred downloading file from {0}'.format(link))
            success = False
    if success:
        print('[+] Files correctly downloaded to {0}'.format(path))

def run(url, pattern, depth=0, ignore='', domains='', auto=1):
    print('[+] Scraping website...')
    links = parse_web(url, pattern, depth, ignore, domains)
    final_urls, final_json_urls = build_final_urls(correct_pattern_links)
    video_urls = final_urls   
    if auto == 1:
        download_files(video_urls)
    else:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #video_urls = re.sub('[\'\[\]]', '', '{0}'.format(video_urls))
        html_file = open('links.htm',"a+")
        raw_json = parse_remote_json(final_json_urls)
        video_title = print_json_object(raw_json)
        for v_url, v_title in zip(video_urls, video_title):
            print v_url
            print v_title
            html_file.write('{0}   -   <a href ="{1}">{2}</a><br/>\n'.format(now, v_url, v_title))
        html_file.close()
        print('[+] Files can be downloaded from: {0}'.format(video_urls))
    return links

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('-p', '--pattern', default='manifest.f4m')
    parser.add_argument('-jp', '--json_pattern', default='zeus.json')
    parser.add_argument('-d', '--depth', type=int, default=1)
    parser.add_argument('-i', '--ignore', default='js,woff,tiff,css,jpg,png,swf,mp3')
    parser.add_argument('-vd', '--domains', default='playwire,fullmatchesandshows')
    parser.add_argument('-a', '--auto', type=int, default=0)
    return parser.parse_args()

if __name__ == '__main__':
    parser = parse_args()
    links = run(parser.url, parser.pattern, parser.depth, parser.ignore, parser.domains, parser.auto)
