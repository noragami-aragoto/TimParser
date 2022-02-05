import time

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import re
from pprint import pprint as print
from collections.abc import Iterable


class Mosplitka_crawler:

    def __init__(self, data_writer):
        self.__driver = self.__driver_init(self.__driver_options())
        self._data_writer = data_writer

    def __driver_init(self, options):
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get('https://mosplitka.ru/brands/plitka/')
        return driver

    def execute(self):
        brands = self.get_brands()
        for brand in brands:
            self.page_brand(brand)

    def page_brand(self, link):
        results = []
        self.open_new_window(link)
        pagination = 0
        try:
            pagination = len(self.find_conditions(By.XPATH, "//ul[@class='pagination-catalog__items']/li"))
        except:
            pass
        if pagination >= 2:
            for i in range(1, pagination + 1):
                link = self.__driver.current_url + f'?PAGEN_1={i}'
                self.open_new_window(link)
                brand_title = self.get_brand_title()
                collections = self.get_collections()
                for collection in collections:
                    collection_link = collection.get_attribute('href')
                    results.append(self.page_collection(collection_link))
                self.close_current_window()
        else:
            brand_title = self.get_brand_title()
            collections = self.get_collections()
            for collection in collections:
                collection_link = collection.get_attribute('href')
                results.append(self.page_collection(collection_link))
            self.close_current_window()
        data = {'brand_title': brand_title.replace(' ', '_'),
                'collections': results}
        self._data_writer.set_path(f'./output/mosplitka/{data.get("brand_title")}.xlsx')
        self._data_writer.save(data)

    def page_collection(self, link):
        self.open_new_window(link)
        collection_title = self.get_collection_title()
        collection_features = self.get_collection_features()
        collection_code = self.get_collection_code()
        collection_pictures = self.get_collection_images()
        collection_goods = self.get_collection_good()
        self.close_current_window()
        return {
            "collection_title": collection_title,
            "collection_features": collection_features,
            "collection_code": collection_code,
            "collection_pictures": collection_pictures,
            "collection_goods": collection_goods,
        }

    def get_collection_good(self):
        results = []
        cards = self.find_conditions(By.XPATH,
                                     "//div[@class='m-product']/a",
                                     10)
        for card in cards:
            results.append(self.page_card(card.get_attribute('href')))
        return results

    def page_collection_only(self, link):
        results = []
        if ';' in link:
            links = link.split(';')
            for link in links:
                self.open_new_window(link)
                collection_title = self.get_collection_title().replace(':', ' ')
                collection_features = self.get_collection_features()
                collection_code = self.get_collection_code()
                collection_pictures = self.get_collection_images()
                collection_goods = self.get_collection_good()
                self.close_current_window()
                results.append({
                    "collection_title": collection_title,
                    "collection_features": collection_features,
                    "collection_code": collection_code,
                    "collection_pictures": collection_pictures,
                    "collection_goods": collection_goods,
                })
        else:
            self.open_new_window(link)
            collection_title = self.get_collection_title().replace(':', ' ')
            collection_features = self.get_collection_features()
            collection_code = self.get_collection_code()
            collection_pictures = self.get_collection_images()
            collection_goods = self.get_collection_good()
            self.close_current_window()
            results.append({
                "collection_title": collection_title,
                "collection_features": collection_features,
                "collection_code": collection_code,
                "collection_pictures": collection_pictures,
                "collection_goods": collection_goods,
            })
        data = {'brand_title': collection_title.replace(' ', '_'),
                'collections': results}
        self._data_writer.set_path(f'./output/mosplitka/{data.get("brand_title")}.xlsx')
        self._data_writer.save(data)

    def page_card(self, link):
        self.open_new_window(link)
        card_title = self.get_card_title()
        card_price = self.get_card_price()
        card_features = self.get_card_features()
        card_article = card_features.get('Артикул')
        card_imgs = self.get_card_img()
        card_picture = ''
        if card_imgs:
            card_picture = ';'.join(card_imgs)
        self.close_current_window()
        return {
            "card_title": card_title,
            "card_price": card_price,
            "card_features": card_features,
            "card_article": card_article,
            "card_picture": card_picture,
        }

    def get_card_img(self):
        try:
            results = []
            count = len(self.find_conditions(By.XPATH, "//ul[@class='tile-picture-prev']/li"))
            img = "//div[@class='pop-images-big-item slick-slide slick-current slick-active']//img"
            self.__driver.execute_script("document.querySelector('.tile-picture-main__img').click()")
            for i in range(0, count):
                results.append(self.find_condition(By.XPATH, img).get_attribute('src'))
                self.__driver.execute_script("document.querySelector('.pop-images-arrow__right').click()")
            return results
        except Exception as e:
            print(e)

    def get_card_features(self):
        try:
            results = {}
            features_blocks = self.find_conditions(By.XPATH,
                                                   "//div[@class='communication-prop']//li[@class='tile-prop-tabs__item']")
            for block in features_blocks:
                items = self.find_conditions(By.XPATH, 'div', 10, block)
                results[items[0].text] = items[1].text
            return results
        except Exception as e:
            print(e)

    def get_card_price(self):
        try:
            return self.find_condition(By.XPATH, "//p[@class='tile-shop__price']", 10).text
        except Exception as e:
            pass

    def get_card_title(self):
        try:
            return self.find_condition(By.XPATH, "//h1[@class='tile__title']", 10).text
        except Exception as e:
            pass

    def get_collection_images(self):
        try:
            count_imgs = len(self.find_conditions(By.XPATH,
                                                  "//div[@class='swiper-container_collection-small swiper-container swiper-container-horizontal swiper-container-thumbs']/div/div/a"))
            img_selector = "//div[@class='swiper-slide swiper-slide-active']/a[@data-gallery]"
            results = []
            results.append(self.find_condition(By.XPATH, img_selector).get_attribute('href'))
            for i in range(1, count_imgs):
                button = self.find_condition(By.XPATH, "//div[@class='swiper-button-next']")

                self.__driver.execute_script("arguments[0].click();", button)
                results.append(self.find_condition(By.XPATH, img_selector).get_attribute('href'))
            return results
        except Exception as e:
            print(e)

    def get_collection_code(self):
        try:
            return self.find_condition(By.XPATH, "//div[@class='name-fav--wrapper']/a", 10).get_attribute('data-id')
        except Exception as e:
            print(e)

    def get_collection_features(self):
        try:
            features_blocks = self.find_conditions(By.XPATH, "//div[@class='size-use--wrapper']//div[@class='row']", 10)
            results = {}
            for block in features_blocks:
                items = self.find_conditions(By.XPATH, "div", 10, block)
                results[items[0].text] = items[1].text
            return results
        except Exception as e:
            print(e)

    def get_collection_title(self):
        try:
            return self.find_condition(By.XPATH, "//div[@class='name-fav--wrapper']//h1", 10).text
        except Exception as e:
            print(e)

    def get_collections(self):
        try:
            return self.find_conditions(By.XPATH, "//div[@class='card']//div[contains(@class,'card__name')]//a", 10)
        except Exception as e:
            print(e)

    def get_brand_title(self):
        try:
            return self.find_condition(By.XPATH, "//h1[@class='page__title']").text
        except Exception as e:
            pass

    def get_brands(self):
        try:
            links = self.find_conditions(By.XPATH,
                                         "//div[contains(@class,'brands-list__item')]//a[@class='brands-list__name']",
                                         10)
            results = []
            for link in links:
                split_link = list(filter(None, link.get_attribute('href').split('/')))[-1]
                results.append(f'https://mosplitka.ru/catalog/plitka/{split_link}')
            return results
        except Exception as e:
            print(e)

    def find_condition(self, by, element, time=5, driver_element=False):
        if driver_element:
            driver = driver_element
        else:
            driver = self.__driver
        try:
            element = WebDriverWait(driver, time).until(
                EC.presence_of_element_located((by, element))
            )
            return element
        except BaseException as e:
            pass

    def find_conditions(self, by, element, time=5, driver_element=False):
        if driver_element:
            driver = driver_element
        else:
            driver = self.__driver
        try:
            elements = WebDriverWait(driver, time).until(
                EC.presence_of_all_elements_located((by, element))
            )
            return elements
        except BaseException as e:
            pass

    def close_current_window(self):
        try:
            current_window = len(self.__driver.window_handles)
            self.__driver.execute_script('window.close()')
            self.__driver.switch_to.window(self.__driver.window_handles[current_window - 2])
        except:
            pass

    def open_new_window(self, url):
        try:
            print(f"URL : {url}")
            self.__driver.execute_script(f"window.open('{url}')")
            self.__driver.switch_to.window(self.__driver.window_handles[-1])
        except:
            pass

    def __driver_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        return chrome_options
