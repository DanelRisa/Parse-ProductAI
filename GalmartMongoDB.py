import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient

uri = "mongodb+srv://danel:zslil9kl044iMIYs@cluster0.n1n9npc.mongodb.net/?retryWrites=true&w=majority"
db_name = "DanelProject"
collection_name = "Products"


client = MongoClient(uri)
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
    'Бакалея': 'https://store.galmart.kz/product-category/%d0%ba%d0%b70000001/',
    'Овощи и фрукты': 'https://store.galmart.kz/product-category/%d0%ba%d0%b70000255/',
    "Колбасы и сыры": ["https://store.galmart.kz/product-category/%d0%ba%d0%b70000048/%d0%ba%d0%b70000049/"],
    "Кондитерские изделия": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000061/",
    "Консервы": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000094/%d0%ba%d0%b70000095/",
    "Молочные продукты и яйца": ["https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000182/", "https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000185/",
    "https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000191/","https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000200/","https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/%d0%ba%d0%b70000198/"],
    "Моющие, чистящие средства": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000207/",
    "Напитки и алкогольные напитки": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000223/",
    "Полуфабрикаты": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000293/",
    "Хлеб и хлебобулочные изделия": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000484/",
    "Чай и кофе и какао": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000499/",
    "Мясо и рыба и птица": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000155/%d0%ba%d0%b70000163/",
    "Косметика, средства гигиены": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000109/"
    
}

for category, urls in categories.items():
    # If it's a single URL, convert it to a list with a single element for consistency
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

print('Saved in MongoDB.')