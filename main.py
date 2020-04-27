import requests
from bs4 import BeautifulSoup


class LinksCollector:
    max_links_count = 0
    links_list = []

    def collect_links(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # collect similar articles
        similar_articles = soup.find_all("a", {"class": "similar"}, href=True)

        for raw_link in similar_articles:
            new_link = f"https://cyberleninka.ru{raw_link['href']}"
            if new_link not in self.links_list:
                if len(self.links_list) >= self.max_links_count:
                    return

                # filter old articles
                if not self.check_publish_year(new_link):
                    continue

                self.links_list.append(new_link)
                self.collect_links(new_link)

    def check_publish_year(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        publish_year = soup.find("time").get_text()

        if int(publish_year) < 2017:
            return False
        return True

    def print_links(self):
        print(f"Collected {len(self.links_list)} links")
        # for l in self.links_list:
        #     print(l)


def generate_text(url, num):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    publish_year = soup.find("time").get_text()
    # remove ads
    ads = soup.find_all("div", {"class": "bibloid_serp bibloid_serp_ocr"})
    for ad in ads:
        ad.extract()
    article_text = soup.find("div", {"class": "ocr"})
    article_file = open(f"articles/{num}_{publish_year}.txt", "w", encoding='utf-8')
    raw_text = article_text.get_text()
    article_file.write(raw_text)
    article_file.close()


if __name__ == '__main__':
    collector = LinksCollector()
    collector.max_links_count = 5
    collector.collect_links('https://cyberleninka.ru/article/n/algoritm-vzaimnogo-isklyucheniya-v-piringovyh-sistemah')
    collector.print_links()

    links_file = open(f"articles_links.txt", "w", encoding='utf-8')
    for link in collector.links_list:
        links_file.write(link + "\n")
    links_file.close()

    article_num = 0
    for link in collector.links_list:
        generate_text(link, article_num)
        print(article_num)
        article_num = article_num + 1
