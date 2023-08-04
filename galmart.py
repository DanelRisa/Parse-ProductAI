import requests
from bs4 import BeautifulSoup
import json

output_file = "galmart.json"

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
    "Колбасы и сыры": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000048/",
    "Кондитерские изделия": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000061/",
    "Консервы": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000094/",
    "Молочные продукты и яйца": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000181/",
    "Моющие, чистящие средства": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000207/",
    "Напитки и алкогольные напитки": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000223/",
    "Полуфабрикаты": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000293/",
    "Хлеб и хлебобулочные изделия": "https://store.galmart.kz/product-category/%d0%ba%d0б70000484/",
    "Чай и кофе и какао": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000499/",
    "Мясо и рыба и птица": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000155/%d0%ba%d0%b70000163/",
    "Косметика, средства гигиены": "https://store.galmart.kz/product-category/%d0%ba%d0%b70000109/"
}


products = []

for category, url in categories.items():
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
            products.append(product_data)

        print(f"Страница {page} ({category}) обработана.")

with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(products, file, ensure_ascii=False, indent=4)

print('Saved in galmart.json')
