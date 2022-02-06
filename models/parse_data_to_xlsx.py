from models.parse_data_write import ParseDataWriter
from pprint import pprint
import xlsxwriter


class ParseDataToXlsx(ParseDataWriter):
    __file_path = ''

    def set_path(self, file_path):
        self.__file_path = file_path
        self.check_file_path()

    def check_file_path(self):
        if not self.__file_path:
            raise Exception('File path is undefined')

    def save(self, data=False):
        workbook = xlsxwriter.Workbook(filename=self.__file_path, options={'strings_to_urls': False})
        worksheet_products = workbook.add_worksheet('Товары')
        worksheet_collection = workbook.add_worksheet('Коллекции')
        self.collections_collector(worksheet_collection, data.get('collections'))
        self.product_collector(worksheet_products, data.get('collections'))
        print(f'\n Файл {self.__file_path} сохранен \n')
        workbook.close()

    def product_collector(self, worksheet, data):
        correct_list = {}
        column = 0
        features_headlines = self.products_features_headlines(data)
        column = self.write_headless('Название коллкции', column, worksheet, correct_list)
        column = self.write_headless('Код коллекции', column, worksheet, correct_list)
        column = self.write_headless('Название товара', column, worksheet, correct_list)
        column = self.write_headless('Артикуль товара', column, worksheet, correct_list)
        column = self.write_headless('Фотография товара', column, worksheet, correct_list)
        column = self.write_headless('Цена товара', column, worksheet, correct_list)
        column = self.write_features_headless(features_headlines, column, worksheet, correct_list)
        self.write_product_data(data, worksheet, correct_list)

    def write_product_data(self, data, worksheet, correct_list):
        row = 1
        for collection in data:
            collection_title = collection.get('collection_title')
            collection_code = collection.get('collection_code')
            for good in collection.get('collection_goods'):
                if good:
                    worksheet.write(row, correct_list.get('Название коллкции'), collection_title)
                    worksheet.write(row, correct_list.get('Код коллекции'), collection_code)
                    worksheet.write(row, correct_list.get('Название товара'), good.get('card_title'))
                    worksheet.write(row, correct_list.get('Артикуль товара'), good.get('card_article'))
                    worksheet.write(row, correct_list.get('Фотография товара'), good.get('card_picture'))
                    worksheet.write(row, correct_list.get('Цена товара'), good.get('card_price'))
                    try:
                        for feature_key, feature_value in good.get('card_features').items():
                            worksheet.write(row, correct_list.get(feature_key), feature_value)
                    except:
                        pass
                    row += 1

    def collections_collector(self, worksheet, data):
        correct_list = {}
        column = 0
        features_headlines = self.collection_features_headlines(data)
        column = self.write_headless('Название коллкции', column, worksheet, correct_list)
        column = self.write_headless('Код', column, worksheet, correct_list)
        column = self.write_headless('Фотографии', column, worksheet, correct_list)
        column = self.write_features_headless(features_headlines, column, worksheet, correct_list)
        self.write_collection_data(data, worksheet, correct_list)

    def write_collection_data(self, data, worksheet, correct_list):
        row = 1
        for collect_card in data:
            worksheet.write(row, correct_list.get('Код'), collect_card.get('collection_code'))
            worksheet.write(row, correct_list.get('Название коллкции'), collect_card.get('collection_title'))
            img_list_to_str = ' ; '.join(collect_card.get('collection_pictures'))
            worksheet.write(row, correct_list.get('Фотографии'), img_list_to_str)
            collection_features = collect_card.get('collection_features')
            if collection_features:
                for feature_key, feature_value in collection_features.items():
                    worksheet.write(row, correct_list.get(feature_key), feature_value)
            row += 1

    def write_headless(self, title_headline, column, worksheet, correct_list):
        correct_list[title_headline] = column
        worksheet.write(0, column, title_headline)
        column += 1
        return column

    def write_features_headless(self, features_headlines, column, worksheet, correct_list):
        for headline in features_headlines:
            worksheet.write(0, column, headline)
            correct_list[headline] = column
            column += 1
        return column

    def collection_features_headlines(self, data):
        feature_keys = []
        for collection_obj in data:
            features_obj = collection_obj.get('collection_features')
            if features_obj:
                for key in features_obj.keys():
                    if key not in feature_keys:
                        feature_keys.append(key)
            return feature_keys
        return ''

    def products_features_headlines(self, data):
        feature_keys = []
        for collection_obj in data:
            for good in collection_obj.get('collection_goods'):
                if good:
                    features_obj = good.get('card_features')
                    for key in features_obj.keys():
                        if key not in feature_keys:
                            feature_keys.append(key)
        return feature_keys
