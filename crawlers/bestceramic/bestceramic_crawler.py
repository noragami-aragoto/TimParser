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


class BestceramicCrawler:

    def __init__(self, data_writer):
        self.__driver = self.__driver_init(self.__driver_options())
        self._data_writer = data_writer

    def __driver_init(self, options):
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get('https://www.bestceramic.ru/manuf')
        return driver

    def execute(self):
        brands = self.get_brands()
        for brand in brands:
            brand_link = brand.get_attribute('href')
            self.page_brand(brand_link)

    def page_brand(self, link):
        results = []
        self.open_new_window(link)
        pagination = self.find_conditions(By.XPATH, "//div[@class='pagination']//a[@class='pagination__item']", 5)
        if (pagination):
            brand_title = self.get_brand_title()
            results = self.page_pagination_brand(results)
            for button in pagination:
                button.click()
                results = self.page_pagination_brand(results)
        else:
            brand_title = self.get_brand_title()
            collections = self.get_collections()
            for collection in collections:
                collection_link = collection.get_attribute('href')
                results.append(self.page_collection(collection_link))
        self.close_current_window()
        data = {'brand_title': brand_title.replace(' ', '_'),
                'collections': results}
        self._data_writer.set_path(f'./output/bestceramic/{data.get("brand_title")}.xlsx')
        self._data_writer.save(data)

    def page_pagination_brand(self, results):
        collections = self.get_collections()
        for collection in collections:
            collection_link = collection.get_attribute('href')
            results.append(self.page_collection(collection_link))
        return results

    def page_collection_only(self, link):
        self.open_new_window(link)
        results = []
        collection_title = self.get_collection_title()
        collection_features = {'Характеристики': 'нету'}
        collection_code = self.__driver.current_url
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
        self._data_writer.set_path(f'./output/bestceramic/{data.get("brand_title")}.xlsx')
        self._data_writer.save(data)

    def page_collection(self, link):
        self.open_new_window(link)
        collection_title = self.get_collection_title()
        collection_features = {'Характеристики': 'нету'}
        collection_code = self.__driver.current_url
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

    def get_brand_title(self):
        try:
            return self.find_condition(By.XPATH, "//h1[@class='title-section']").text.replace(
                'Каталог продукции фабрики ',
                '')
        except Exception as e:
            pass

    def get_collection_good(self):
        results = []
        pagination = []
        if (self.find_conditions(By.XPATH, "//div[@class='pagination']/a[@class='pagination__item']")):
            pagination = len(
                self.find_conditions(By.XPATH, "//div[@class='pagination']/a[@class='pagination__item']")) + 1
        if (pagination):
            while (self.find_conditions(By.XPATH,
                                        "//button[@class='button-reset more_button _transition button-text _font-s _theme-a' and  not(contains(@style,'display: none'))]")):
                elems = self.find_conditions(By.XPATH,
                                             "//button[@class='button-reset more_button _transition button-text _font-s _theme-a' and  not(contains(@style,'display: none'))]")
                if elems:
                    if isinstance(elems, Iterable):
                        for i in elems:
                            self.__driver.execute_script("arguments[0].click();", i)
                    else:
                        self.__driver.execute_script("arguments[0].click();", elems)
            results = self.pagination_collection(results)
        else:
            cards = self.find_conditions(By.XPATH,
                                         "//div[@class='labels__item labels__item_kod']/../../..//div[@class='plate__title']/a",
                                         10)
            for card in cards:
                results.append(self.page_card(card.get_attribute('href')))
        return results

    def pagination_collection(self, results):
        cards = self.find_conditions(By.XPATH,
                                     "//div[@class='labels__item labels__item_kod']/../../..//div[@class='plate__title']/a",
                                     10)
        for card in cards:
            page_card_data = self.page_card(card.get_attribute('href'))
            if page_card_data:
                results.append(page_card_data)
        return results

    def page_card(self, link):
        self.open_new_window(link)
        if (self.find_condition(By.XPATH, "//div[@class='product-single']")):
            card_title = self.get_card_title()
            card_price = self.get_card_price()
            card_features = self.get_card_features()
            card_article = self.get_card_article()
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
        self.close_current_window()
        return []

    def get_card_article(self):
        try:
            return self.find_condition(By.XPATH, "//div[@class='labels__item labels__item_kod'][1]", 10).text
        except Exception as e:
            print(e)

    def get_card_img(self):
        try:
            if self.find_condition(By.XPATH,
                                   "//div[@class='product-slider__inner-small slick-initialized slick-slider slick-vertical']"):
                results = []
                elements = self.find_conditions(By.XPATH,
                                                "//div[@class='product-slider__inner-small slick-initialized slick-slider slick-vertical']//div[contains(@class,'slick-slide')]")
                for elem in elements:
                    self.__driver.execute_script("arguments[0].click();", elem)
                    results.append(self.find_condition(By.XPATH, '//picture[1]/img[1]').get_attribute('src'))
                return results
            else:
                return [self.find_condition(By.XPATH, '//picture[1]/img[1]').get_attribute('src')]
        except Exception as e:
            print(e)

    def split_img(self, main_img):
        src_split = main_img.split('/')
        foundation = src_split[2:-1]
        new_img_resolution = re.sub(r'\d+x\d+', r'1024x768', src_split[-1])
        img = 'https://' + '/'.join(foundation) + '/' + new_img_resolution
        return img

    def get_card_features(self):
        try:
            features_blocks = self.find_conditions(By.XPATH, "//div[@class='product-characteristic__inner']/div/div",
                                                   10)
            results = {}
            for block in features_blocks:
                title = block.find_element(By.XPATH, "div[@class='product-characteristic__item-text']").text
                feature = block.find_element(By.XPATH, "div[@class='product-characteristic__item-value']").text
                results[title] = feature
            return results
        except Exception as e:
            print(e)

    def get_card_price(self):
        try:
            price = self.find_condition(By.XPATH, "//div[@class='plate__footer plate-line'][1]", 10).text
            price = price.split('\n')
            return ''.join(price[1:])
        except Exception as e:
            pass

    def get_card_title(self):
        try:
            return self.find_condition(By.XPATH, "//h1[@itemprop='name']", 10).text
        except Exception as e:
            pass

    def get_collection_images(self):
        try:
            if (not self.find_condition(By.XPATH,
                                        "//button[contains(@class,'product-slider__inner-arrow product-slider__inner-arrow_next')]")):
                self.__driver.execute_script('document.location.reload()')
                self.get_collection_images()
            else:
                result = []
                imgs = self.find_conditions(
                    By.XPATH, "//div[@class='slick-slide' and contains(@style,'position: relative')]//img")
                if (imgs):
                    for img in imgs:
                        result.append(img.get_attribute('src'))
                else:
                    result.append(
                        self.find_condition(By.XPATH, "//div[@class='product-slider__item']/picture/img").get_attribute(
                            'src'))
            return result
        except Exception as e:
            print(e)

    def get_collection_code(self):
        try:
            return self.find_condition(By.XPATH, "//div[@class='uk-margin']/article", 10).text.split(":")[-1].replace(
                ' ', '')
        except Exception as e:
            print(e)

    def get_collection_features(self):
        try:
            features_blocks = self.find_conditions(By.XPATH, "//div[@class='section-justify__col']/div", 10)
            results = {}
            for block in features_blocks:
                try:
                    title, feature = block.text.split(':')
                    results[title] = feature
                except Exception as e:
                    pass
            return results
        except Exception as e:
            print(e)

    def get_collection_title(self):
        try:
            return self.find_condition(By.XPATH, "//h1[@class='title-section']", 10).text
        except Exception as e:
            print(e)

    def get_collections(self):
        try:
            return self.find_conditions(By.XPATH, "//div[@class='plate__title']/a", 10)
        except Exception as e:
            print(e)

    def get_brands(self):
        try:
            return self.find_conditions(By.XPATH,
                                        "//div[@class='manufacturers-page__inner']//a[@class='manufacturers-page__name-text']",
                                        10)
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
        sleep(3)
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
