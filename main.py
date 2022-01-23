from crawlers.roaylstone.royalstone_crawler import RoyalstoneCrawler
from crawlers.bestceramic.bestceramic_crawler import BestceramicCrawler
from models.parse_data_to_xlsx import ParseDataToXlsx
from update import update


def app(type, link, collection):
    # update
    # TODO: вынести в класс
    if type == 'royalstone':
        parse_data_save = ParseDataToXlsx()
        royalstone_crawler = RoyalstoneCrawler(parse_data_save)
        if not link:
            royalstone_crawler.execute()
        else:
            royalstone_crawler.page_brand(link)
    elif type == 'bestceramic':
        parse_data_save = ParseDataToXlsx()
        bestceramic_crawler = BestceramicCrawler(parse_data_save)
        if collection:
            bestceramic_crawler.page_collection_only(collection)
            exit(1)
        if not link:
            bestceramic_crawler.execute()
        else:
            bestceramic_crawler.page_brand(link)


if __name__ == '__main__':
    update()
    parsers = ['royalstone', 'bestceramic']
    start_flag = True
    type = ''
    link = ''
    collection = ''
    while (start_flag):
        command = int(input('Введите команду цыфрой \n'
                            '1: Выбрать тип парсера \n'
                            '2: Установить ссылку (если ссылка не выбрана, будут парситься все бренды)\n'
                            '3: Установить коллекцию \n'
                            '0: Старт !!!  \n'))
        if command == 1:
            count = 1
            for parser in parsers:
                print(f"{count}:  {parser} \n")
                count += 1
            ans = int(input('Тип парсера : '))
            type = parsers[(ans - 1)]
        elif command == 2:
            link = input('Введите ссылку пример "https://www.bestceramic.ru/manuf/14-ora-italiana" : ')
        elif command == 3:
            collection = input('Введите ссылку коллекции пример  "https://www.bestceramic.ru/section/lazzaro-creto" : ')
        elif command == 0:
            start_flag = False
    app(type, link, collection)
    print('\n---------------------------END---------------------------\n')
