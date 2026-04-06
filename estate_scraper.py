from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import csv

class Estate_Scraper:
    def __init__(self, headless = True):
        self.headless = headless
        self.driver = None

        self.setup_driver()



    def setup_driver(self):
        op = Options()

        if self.headless:
            op.add_argument("--headless")

        op.add_argument("--disable-dev-shm-usage")
        op.add_argument("--no-sandbox")
        op.add_argument("--disable-gpu")
        op.add_argument("--disable-extensions")
        op.add_argument("--disable-plugins")

        sv = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=sv, options=op)

        self.driver.implicitly_wait(5)



    def access_website(self, url):
        try:
            print(f"アクセス中： {url}")

            self.driver.get(url)

            time.sleep(2)

            page_title = self.driver.title
            print(f"ページタイトル： {page_title}")

            return True

        except Exception as e:
            print(f"アクセスエラー：{e}")

            return False



    def close_browser(self):
        if self.driver:
            self.driver.quit()
            print("ブラウザを終了しました")



    def get_estate_count(self):
        try:
            count_element = self.driver.find_element(By.CSS_SELECTOR, ".paginate_set-hit")
            total = count_element.text

            return total

        except Exception as e:
            return "不明"




    def get_estate_data(self):
        estate_list = []

        try:
            estate_elements = self.driver.find_elements(By.CSS_SELECTOR, ".property.js-property")

            for i, estate in enumerate(estate_elements):
                try:
                    title_element = estate.find_element(By.CSS_SELECTOR, ".property_inner h2 a")
                    name = title_element.text

                    price_element = estate.find_element(By.CSS_SELECTOR, ".detailbox-property-point")
                    price = price_element.text

                    layout_element = estate.find_element(By.CSS_SELECTOR, ".detailbox-property--col3 div ")
                    layout = layout_element.text

                    address_element = estate.find_element(By.CSS_SELECTOR, ".detailbox-property-col:nth-of-type(5)")
                    address = address_element.text

                    current_estate_data = {
                        "name": name,
                        "price": price,
                        "address": address,
                        "layout": layout
                    }

                    estate_list.append(current_estate_data)


                except Exception as e:
                    continue

        except Exception as e:
            print("データ取得エラー")

        return estate_list



    def next_page(self):
        try:
            next_btn = self.driver.find_element(By.LINK_TEXT, "次へ")

            if next_btn:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(2)

                next_btn.click()
                time.sleep(2)

                return True

        except Exception:
            return False



    def save_csv(self, estate_list, filename = "estate_scraper.csv"):
            try:
                fieldnames = ["物件名", "家賃", "間取り", "住所"]

                with open(filename, "a", encoding = "utf-8-sig", newline = "") as f:

                    writer = csv.DictWriter(f, fieldnames = fieldnames)

                    if f.tell() == 0:
                        writer.writeheader()

                    for estate in estate_list:

                        writer.writerow({
                            "物件名":estate["name"],
                            "家賃":estate["price"],
                            "間取り":estate["layout"],
                            "住所":estate["address"]
                        })

                print(f"--- {len(estate_list)}件をCSVに保存しました ---")

            except Exception as e:
                print(f"csv保存エラー：{e}")



def main():
    target_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC005/?fw2=&mt=9999999&cn=9999999&ta=47&et=9999999&sc=47201&shkr1=03&ar=090&bs=040&ct=9999999&shkr3=03&shkr2=03&srch_navi=1&mb=0&shkr4=03&cb=0.0&page=57"

    scraper = Estate_Scraper(headless = False)
    try:
        if scraper.access_website(target_url):
            print("アクセスに成功しました")

            total = scraper.get_estate_count()
            print(f"発見した物件数：{total}")

            while True:
                estate_data = scraper.get_estate_data()

                if estate_data:
                    scraper.save_csv(estate_data)

                if not scraper.next_page():
                    break

        else:
            print("アクセスに失敗しました")

    except Exception as e:
        print(f"実行エラー： {e}")

    finally:
        scraper.close_browser()



if __name__ == '__main__':
    main()

