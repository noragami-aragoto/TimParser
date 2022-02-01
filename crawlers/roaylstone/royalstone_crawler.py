from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pprint import pprint


class RoyalstoneCrawler:

    def __init__(self, data_writer):
        self.__driver = self.__driver_init(self.__driver_options())
        self._data_writer = data_writer

    def __driver_init(self, options):
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get('https://www.royalstone.ru/fabriki/')
        return driver

    def execute(self):
        brands = self.get_brands()
        for brand in brands:
            brand_link = brand.get_attribute('href')
            self.page_brand(brand_link)

    def page_brand(self, link):
        results = []
        self.open_new_window(link)
        brand_title = self.get_brand_title()
        collections = self.get_collections()
        for collection in collections:
            collection_link = collection.get_attribute('href')
            results.append(self.page_collection(collection_link))
        self.close_current_window()
        data = {'brand_title': brand_title.replace(' ', '_'),
                'collections': results}
        self._data_writer.set_path(f'./output/roaylstone/{data.get("brand_title")}.xlsx')
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

    def page_collection_only(self, link):
        results = []
        if ';' in link:
            links = link.split(';')
            for link in links:
                pprint('-----------------------LINK-------------------')
                pprint(link)
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
        self._data_writer.set_path(f'./output/roaylstone/{data.get("brand_title")}.xlsx')
        self._data_writer.save(data)

    def get_brand_title(self):
        try:
            return self.find_condition(By.XPATH, "//h1[@class='uk-heading-bullet']").text
        except Exception as e:
            pass

    def get_collection_good(self):
        results = []
        try:
            paginations_good = self.find_conditions(By.XPATH,
                                                    "//div[@class='bx-pagination-container row']//li[position() > 1 and position() < count(//div[@class='bx-pagination-container row']//li)]")
        except:
            paginations_good = None
        count = 1
        if (paginations_good):
            for pagination in paginations_good:
                self.open_new_window(self.__driver.current_url + f'/?PAGEN_1={count}')
                cards = self.find_conditions(By.XPATH,
                                             "//div[contains(@class,'uk-card-default ') and @data-product-iblock-id]/div/a",
                                             10)
                for card in cards:
                    results.append(self.page_card(card.get_attribute('href')))
                self.close_current_window()
                count += 1
        else:
            cards = self.find_conditions(By.XPATH,
                                         "//div[contains(@class,'uk-card-default ') and @data-product-iblock-id]/div/a",
                                         10)
            for card in cards:
                results.append(self.page_card(card.get_attribute('href')))

        return results

    def page_card(self, link):
        self.open_new_window(link)
        card_title = self.get_card_title()
        card_price = self.get_card_price()
        card_features = self.get_card_features()
        card_article = self.get_card_article()
        card_picture = self.get_card_img()
        self.close_current_window()
        return {
            "card_title": card_title,
            "card_price": card_price,
            "card_features": card_features,
            "card_article": card_article,
            "card_picture": card_picture,
        }

    def get_card_article(self):
        try:
            return self.find_condition(By.XPATH, '//span[@class="changeArticle"]', 10).text
        except Exception as e:
            print(e)

    def get_card_img(self):
        try:
            return self.find_condition(By.XPATH, "//a[@class='slider-cursor-zoom'][1]", 10).get_attribute('href')
        except Exception as e:
            print(e)

    def get_card_features(self):
        try:
            features_blocks = self.find_conditions(By.XPATH, "//table/tbody/tr[td]", 10)
            results = {}
            for block in features_blocks:
                title = block.find_element(By.CLASS_NAME, "uk-width-medium").text
                feature = block.find_element(By.XPATH, 'td[position() = 2 ]').text
                results[title] = feature
            return results
        except Exception as e:
            print(e)

    def get_card_price(self):
        try:
            return self.find_condition(By.XPATH, "//div[contains(@class,'price')]", 10).text
        except Exception as e:
            pass

    def get_card_title(self):
        try:
            return self.find_condition(By.XPATH, "//H1", 10).text
        except Exception as e:
            pass

    def get_collection_images(self):
        try:
            images = self.find_conditions(By.XPATH, "//ul[@class='uk-slideshow-items']//a[@href]", 10)
            results = []
            for img in images:
                href = img.get_attribute('href')
                results.append(href)
            return results
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
            features_blocks = self.find_conditions(By.XPATH, "//div[@class='uk-card-collection']/div", 10)
            results = {}
            for block in features_blocks:
                try:
                    title, feature = block.text.split(':')
                    if title == 'Цвет':
                        colors_tor_features = []
                        colors = self.find_conditions(By.XPATH, "//div[@uk-tooltip]", 10)
                        for color in colors:
                            colors_tor_features.append(color.get_attribute('uk-tooltip'))
                        results[title] = ', '.join(colors_tor_features)
                    else:
                        results[title] = feature
                except Exception as e:
                    pass
            return results
        except Exception as e:
            print(e)

    def get_collection_title(self):
        try:
            return self.find_condition(By.XPATH, "//H1", 10).text
        except Exception as e:
            print(e)

    def get_collections(self):
        try:
            return self.find_conditions(By.XPATH, "//ul[contains(@class,'js-filter')]/li/div/div/a", 10)
        except Exception as e:
            print(e)

    def get_brands(self):
        try:
            return self.find_conditions(By.XPATH, "//ul[contains(@class,'js-filter')]/li/div/a", 10)
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
            print(f"{element} not found")
            print(e)

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
            print(f"{elements} not found")
            print(e)

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
