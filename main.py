import requests
from bs4 import BeautifulSoup



def generate_text(url, iteration):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    similar_articles = soup.find_all("a", {"class": "similar"}, href=True)
    for l in similar_articles:
        new_link = f"https://cyberleninka.ru{l['href']}"
        if new_link not in links_list:
            links_list.append(new_link)
    publish_year = soup.find("time")
    # remove ads
    ads = soup.find_all("div", {"class": "bibloid_serp bibloid_serp_ocr"})
    for ad in ads:
        ad.extract()
    article_text = soup.find("div", {"class": "ocr"})
    article_file = open(f"articles/{iteration}_{publish_year.get_text()}.txt", "w", encoding='utf-8')
    raw_text = article_text.get_text()
    article_file.write(raw_text)
    article_file.close()


if __name__ == '__main__':
    #starting link
    links_list = ['https://cyberleninka.ru/article/n/algoritm-vzaimnogo-isklyucheniya-v-piringovyh-sistemah']
    max_iter = 10
    iteration = 0
    for link in links_list:
        if (iteration >= max_iter):
            print("max depth reached")
            break
        generate_text(link, iteration)
        iteration = iteration + 1