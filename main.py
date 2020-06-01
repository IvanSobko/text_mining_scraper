from bs4 import BeautifulSoup
from lxml.html import fromstring
import requests
import time
import re
import os
import glob


class Scrapper:
    def __init__(self):
        self.ip_addresses = self.get_proxies()

    def start_collecting(self, page_count, url):
        page_num = 1
        while True:
            if page_num > page_count:
                break
            page = f"{url}?page={page_num}"
            self.collect_texts(page)
            page_num = page_num + 1

    def collect_texts(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        news_hrefs = soup.findAll("a", {"class": "news-block__text link-more"})
        news_date = soup.findAll("div", {"class": "date-circle"})
        date_time = []
        for div in news_date:
            date_div = div.find("div", {"class": "date"})
            time_div = div.find("div", {"class": "time"})
            time_str = time_div.text.replace(':','.')
            date_time.append(f"{date_div.text}_{time_str}")
        print("Dates:", date_time)
        for a, date in zip(news_hrefs, date_time):
            start = time.time()
            news_page = BeautifulSoup(requests.get('https://www.tourprom.ru/'+a['href']).text, "html.parser")
            div = news_page.find('div', {'class' : 'block panel-body-wrap--padding news-detail'})
            # remove ad
            for item in div.findChildren(recursive=True):
                if item.name == "em":
                    item.extract()

            text = ""
            for item in div.findChildren(recursive=True):
                text = text + item.text
            news_file = open(f"news/{date}.txt", "w", encoding='utf-8')
            news_file.write(text)
            news_file.close()
            self.text_num = self.text_num + 1
            print(f"===== Collected by now: {self.text_num}... Time spent to collect: {(time.time() - start)}")

    ip_addresses = []
    text_num = 0


    def get_proxies(self):
        url = 'https://free-proxy-list.net/anonymous-proxy.html'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = []
        for i in parser.xpath('//tbody/tr')[:40]:
            if i.xpath('.//td[7][contains(text(),"yes")]') and (i.xpath('.//td[5][contains(text(),"elite proxy")]')):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.append(proxy)
        return proxies

    def request_with_proxy(self, url):
        attempt_num = 1
        proxy_num = 0
        while True:
            if proxy_num >= len(self.ip_addresses):  # refresh proxies
                print("Refreshing proxies")
                self.ip_addresses = self.get_proxies()
                proxy_num = 0
            ip = self.ip_addresses[proxy_num]
            proxy = {"http": ip, "https": ip}
            print("Using proxy: ", ip)
            session = requests.Session()
            session.trust_env = False
            try:
                start = time.time()
                response = session.get(url, proxies=proxy, timeout=6)
                print(f"Got response, time: {(time.time() - start)}\n")
                return response
            except requests.exceptions.Timeout:
                print('The request timed out')
                proxy_num = proxy_num + 1
                continue
            except:
                print("Skipping. Connection error. Retrying, attempt number:", attempt_num)
                proxy_num = proxy_num + 1
                attempt_num = attempt_num + 1
                continue


def formate_texts():
    # data = "вки. Туристам , "
    # formatted_data = re.sub(r'(\.)([^\s])', r'. \2', data)            # add space after dot
    # formatted_data = re.sub(r'([^0-9])(\Z)', r'\1. ', formatted_data) # add dot after EOF
    # formatted_data = re.sub(r'(\s)(\.)', r'\2', formatted_data)       # remove space before dot
    # formatted_data = re.sub(r'(\s)(,)', r'\2', formatted_data)        # remove space before coma
    # print(formatted_data)
    # return
    txtfiles = []
    for file in glob.glob("news/*.txt"):
        txtfiles.append(file)
    for i in txtfiles:
        with open(i, 'r+', encoding='utf-8') as text_file:
            data = text_file.read()
            formatted_data = re.sub(r'(\.)([^\s])', r'. \2', data) # add space after dot
            formatted_data = re.sub(r'([^0-9])(\Z)', r'\1. ', formatted_data) # add dot after EOF
            formatted_data = re.sub(r'(\s)(\.)', r'\2', formatted_data) # remove space before dot
            formatted_data = re.sub(r'(\s)(,)', r'\2', formatted_data) # remove space before coma
            text_file.seek(0)
            text_file.write(formatted_data)
            text_file.truncate()
            text_file.close()
        print(f"Proccessed {i} file")


if __name__ == '__main__':
    collector = Scrapper()
    collector.start_collecting(89, "https://www.tourprom.ru/news/")
    formate_texts()
