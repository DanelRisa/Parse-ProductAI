from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

from pymongo import MongoClient
# imports for galmart
import requests
from bs4 import BeautifulSoup
import os

from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')

def scrape_arbuz():
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    base_url = 'https://arbuz.kz'
    category_urls = [
        {'name': 'Овощи и фрукты', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225164-svezhie_ovoshi_i_frukty#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
        {'name': 'Напитки и алкогольные напитки', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/14-napitki#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
        {'name': 'Молоко, сливки, растительное молоко, сгущенное молоко, коктейли молочные', 'urls': [
            'https://arbuz.kz/ru/almaty/catalog/cat/20077-slivki#/',
            'https://arbuz.kz/ru/almaty/catalog/cat/20050-moloko#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D',
            'https://arbuz.kz/ru/almaty/catalog/cat/224177-rastitelnoe_moloko#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D',
            'https://arbuz.kz/ru/almaty/catalog/cat/74410-fermerskoe_moloko#/',
            'https://arbuz.kz/ru/almaty/catalog/cat/20072-sgush_nnoe_moloko',
            'https://arbuz.kz/ru/almaty/catalog/cat/224700-suhoe_moloko',
        ]},
        {'name': 'Масло сливочное, спреды, маргарин', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225446-slivochnoe_maslo#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
        {'name': 'Творог, сметана, кефир и кисломолочные продукты  ', 'urls': ['https://arbuz.kz/ru/almaty/catalog/cat/20016-kislomolochnye_napitki#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D',
            'https://arbuz.kz/ru/almaty/catalog/cat/20089-smetana#/',
            'https://arbuz.kz/ru/almaty/catalog/cat/224761-kurt_zhent#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D',
            'https://arbuz.kz/ru/almaty/catalog/cat/225076-kozhe_shubat',
            'https://arbuz.kz/ru/almaty/catalog/cat/224700-suhoe_moloko']},

        {'name': 'Сыр', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/20160-syry#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
        {'name': 'Йогурты и творожные сырки', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225171-iogurty_i_tvorozhnye_syrki#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
        {'name': "Мука, соль, сахар, приправы, соусы", 'urls':['https://arbuz.kz/ru/almaty/catalog/cat/225449-muka#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D',
            'https://arbuz.kz/ru/almaty/catalog/cat/224402-specii_i_pripravy#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D']},
        {'name': "Крупы, макаронные изделия", 'urls':['https://arbuz.kz/ru/almaty/catalog/cat/224398-krupy_bobovye#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A2,%22component%22%3A%22pagination%22%7D%5D',
            'https://arbuz.kz/ru/almaty/catalog/cat/224399-makarony_i_lapsha#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D']},
        {'name': 'Яйца', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225245-yaica#/'},
        {'name': 'Растительное масла', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225448-rastitelnye_masla#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},

        {'name': 'Кондитерские изделия', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225166-sladosti#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
        {'name': 'Моющие, чистящие средства', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/16-vs_dlya_doma#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
        {'name': 'Мясо и рыба и птица', 'urls': [
            'https://arbuz.kz/ru/almaty/catalog/cat/225162-myaso_ptica#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D', 
            'https://arbuz.kz/ru/almaty/catalog/cat/225163-ryba_i_moreprodukty#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'
        ]},
        {'name': 'Косметика, средства гигиены', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/224407-krasota#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
        {'name': 'Консервы', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/20205-konservy#/'},
        {'name': 'Снеки', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/19820-sneki_i_krekery#/'},
        {'name':'Хлеб и хлебобулочные изделия', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225165-hleb_vypechka#/'}

    ]

    products = []

    options = Options()
    options.headless = True
    service = Service(executable_path=GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    for category in category_urls:
        category_name = category['name']
        
        if 'url' in category:
            category_urls = [category['url']]
        else:
            category_urls = category['urls']
        
        for url in category_urls:
            driver.get(url)

            try:
                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.product-item.product-card')))
            except TimeoutException as te:
                print(f"Timeout occurred while waiting for products in category {category_name}. Skipping to the next category.")
                continue

            while True:
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                items = soup.find_all('article', class_='product-item product-card')
                if not items:
                    break

                for item in items:
                    try:
                        title_elem = item.find('a', class_='product-card__title')
                        price_elem = item.find('span', class_='price--wrapper price--currency_KZT')
                        image_elem = item.find('img', class_='product-card__img')

                        if title_elem and price_elem and image_elem:
                            title = title_elem.get('title')
                            price = price_elem.get_text(strip=True)
                            image_url = image_elem.get('data-src')
                            product_url = base_url + item.find('a', class_='product-card__link').get('href')
                            products.append({'title': title, 'price': price, 'image_url': image_url, 'product_url': product_url, 'supermarket': 'Arbuz', 'category': category_name})
                            collection.insert_one({'title': title,'price': price, 'image_url': image_url, 'product_url': product_url, 'supermarket': 'Arbuz','category': category_name })
                    except Exception as e:
                        print(f"Error occurred while parsing an item: {e}")

                # Find pagination elements (if any)
                pagination = driver.find_elements(By.CSS_SELECTOR, 'ul.pagination.flex-wrap')
                if not pagination:
                    print(f"No pagination found in category {category_name}. Skipping to the next category.")
                    break

                next_page_links = pagination[0].find_elements(By.CSS_SELECTOR, 'li.page-item:not(.disabled) a')
                
                next_page_link = None
                for link in next_page_links:
                    if link.text.strip() == '»':
                        next_page_link = link
                        break
                
                if not next_page_link:
                    break

                driver.execute_script("arguments[0].click();", next_page_link)
                
    driver.quit()
    client.close()

            

def scrape_galmart():

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    def parse_product_card(card, category):
        title = card.find('h2', class_='woocommerce-loop-product__title').text.strip()
        price_element = card.find('span', class_='woocommerce-Price-amount')
        price = price_element.text.strip() if price_element else "Цена не найдена"
        image_url = card.find('img')['src']
        product_url = card.find('a', class_='ast-loop-product__link')['href']

        return {
            'title': title,
            'price': price,
            'image_url': image_url,
            'product_url': product_url,
            'supermarket': 'Galmart',
            'category': category
        }

    categories = {
        'Овощи и фрукты': 'https://store.galmart.kz/product-category/%d0%ba%d0%b70000255/',
        "Напитки и алкогольные напитки": ['https://store.galmart.kz/product-category/%d0%ba%d0%b70000223/%d0%ba%d0%b70000240/',
        'https://store.galmart.kz/product-category/%d0%ba%d0%b70000223/%d0%ba%d0%b70000245/'],
        'Молоко, сливки, растительное молоко, сгущенное молоко, коктейли молочные':['https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000200/'],
        'Масло сливочное, спреды, маргарин':'https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000191/',
        'Творог, сметана, кефир и кисломолочные продукты':'https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000185/',
        'Сыр': 'https://store.galmart.kz/product-category/%d0%ba%d0%b70000048/%d0%ba%d0%b70000055/',
        'Йогурты и творожные сырки':[' https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000182/',
        'https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000185/%d0%ba%d0%b70000190/'],
        'Мука, соль, сахар, приправы, соусы': ['https://store.galmart.kz/product-category/%d0%ba%d0%b70000001/%d0%ba%d0%b70000009/',
        'https://store.galmart.kz/product-category/%d0%ba%d0%b70000001/%d0%ba%d0%b70000026/'],
        'Крупы, макаронные изделия':'https://store.galmart.kz/product-category/%d0%ba%d0%b70000001/%d0%ba%d0%b70000002/',
        'Яйца':'https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000198/',
        'Растительное масла':'https://store.galmart.kz/product-category/%d0%ba%d0%b70000001/%d0%ba%d0%b70000005/',
        "Кондитерские изделия": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000061/",
        "Консервы": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000094/%d0%ba%d0%b70000095/",
        "Моющие, чистящие средства": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000207/",
        "Полуфабрикаты": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000293/",
        "Хлеб и хлебобулочные изделия": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000484/",
        "Чай и кофе и какао": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000499/",
        "Мясо и рыба и птица": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000155/%d0%ba%d0%b70000163/",
        "Косметика, средства гигиены": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000109/"
    }

    for category, urls in categories.items():
        if not isinstance(urls, list):
            urls = [urls]

        for url in urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            pagination = soup.find('nav', class_='woocommerce-pagination')
            if pagination:
                last_page_link = pagination.find_all('a', class_='page-numbers')[-2]
                last_page = int(last_page_link.text)
            else:
                last_page = 1

            for page in range(1, last_page + 1):
                page_url = f'{url}page/{page}/'
                response = requests.get(page_url)
                soup = BeautifulSoup(response.content, 'html.parser')

                product_cards = soup.find_all('li', class_='ast-col-sm-12')

                for card in product_cards:
                    product_data = parse_product_card(card, category)
                    collection.insert_one(product_data)  # MongoDB

                print(f"Страница {page} ({category}) обработана.")

    client.close()


def parse_both_websites():
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    collection.drop()

    scrape_arbuz()
    scrape_galmart()
    print('Data removed and updated in MongoDB.')

    client.close()




