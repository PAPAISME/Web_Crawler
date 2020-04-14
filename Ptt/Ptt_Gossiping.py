import requests
import time
import json
from bs4 import BeautifulSoup

PTT_URL = "https://www.ptt.cc"


def get_web_page(url):
    resp = requests.get(url=url, cookies={"over18": "1"})

    if resp.status_code == 200:
        return resp.text
    else:
        print(f"Invalid url: {url}")

        return None


def get_articles(dom, date):
    soup = BeautifulSoup(dom, "html5lib")

    # 取得文章相關資料
    articles = []

    divs = soup.find_all("div", "r-ent")

    for div in divs:
        if div.find("div", "date").text.strip() == date:
            # 取得推文數
            push_count = 0
            push_string = div.find("div", "nrec").text

            if push_string:
                try:
                    # 轉換字串成數字
                    push_count = int(push_string)
                except ValueError:
                    # 若轉換失敗，可能是 "爆" 或 "X1", "X2"
                    # 若不是，不做任何事，push_count 保持為 0
                    if push_string == "爆":
                        push_count = 99
                    else:
                        push_count = -10

            # 取得文章連結及標題
            if div.find("a"):
                href = div.find("a")["href"]
                title = div.find("a").text
                author = div.find("div", "author").text

                articles.append({
                    "title": title,
                    "author": author,
                    "push_count": push_count,
                    "href": href})

    # 取得上一頁連結
    paging_div = soup.find("div", "btn-group btn-group-paging")
    prev_url = paging_div.find_all("a")[1]["href"]

    return articles, prev_url


if __name__ == "__main__":
    current_page = get_web_page(f"{PTT_URL}/bbs/Gossiping/index.html")

    if current_page:
        articles = []

        # 今天日期，去掉開頭的 "0" 以符合 PTT 網站格式
        today = time.strftime("%m/%d").lstrip("0")

        # 目前頁面的今日文章
        current_articles, prev_url = get_articles(current_page, today)

        # 若目前頁面有今日文章則加入 articles，並回到上一頁繼續尋找是否有今日文章
        while current_articles:
            articles += current_articles

            current_page = get_web_page(PTT_URL + prev_url)

            current_articles, prev_url = get_articles(current_page, today)

        # 儲存或處理文章資訊
        print(f"今天有 {len(articles)} 篇文章")

        hot_spec = 50

        print(f"熱門文章 (> {hot_spec} 推):")

        for article in articles:
            if int(article["push_count"]) > hot_spec:
                print(article)

        with open("Gossiping.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=4, sort_keys=True, ensure_ascii=False)
