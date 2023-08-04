import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json

base_url = 'https://arbuz.kz'
category_urls = [
    {'name': 'Овощи и фрукты', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225164-svezhie_ovoshi_i_frukty#/'},
    {'name': 'Напитки и алкогольные напитки', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/14-napitki#/'},
    {'name': 'Молочные продукты и яйца', 'urls': [
        'https://arbuz.kz/ru/almaty/catalog/cat/19986-moloko_smetana_maslo#/',
        'https://arbuz.kz/ru/almaty/catalog/cat/225209-morozhenoe#/',
        'https://arbuz.kz/ru/almaty/catalog/cat/225171-iogurty_i_tvorozhnye_syrki#/'
    ]},
    {'name': 'Колбаса и сыры', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/20160-syry#/'},
    {'name': 'Кондитерские изделия', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225166-sladosti#/'},
    {'name': 'Моющие, чистящие средства', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/16-vs_dlya_doma#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
    {'name': 'Мясо и рыба и птица', 'urls': [
        'https://arbuz.kz/ru/almaty/catalog/cat/225162-myaso_ptica#/', 
        'https://arbuz.kz/ru/almaty/catalog/cat/225163-ryba_i_moreprodukty#/'
    ]},
    {'name': 'Косметика, средства гигиены', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/224407-krasota#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'},
    {'name': 'Бакалея', 'url': 'https://arbuz.kz/ru/almaty/catalog/cat/225168-vse_dlya_gotovki_i_vypechki#/?%5B%7B%22slug%22%3A%22page%22,%22value%22%3A1,%22component%22%3A%22pagination%22%7D%5D'}
]

products = []

driver_service = Service(GeckoDriverManager().install())
options = Options()
driver = webdriver.Firefox(service=driver_service, options=options)

for category in category_urls:
    category_name = category['name']
    
    if 'url' in category:
        category_urls = [category['url']]
    else:
        category_urls = category['urls']
    
    for url in category_urls:
        driver.get(url)

        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.product-item.product-card')))

        while True:
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            items = soup.find_all('article', class_='product-item product-card')
            if not items:
                break

            for item in items:
                title_elem = item.find('a', class_='product-card__title')
                price_elem = item.find('span', class_='price--wrapper price--currency_KZT')
                image_elem = item.find('img', class_='product-card__img')

                if title_elem and price_elem and image_elem:
                    title = title_elem.get('title')
                    price = price_elem.get_text(strip=True)
                    image_url = image_elem.get('data-src')
                    product_url = base_url + item.find('a', class_='product-card__link').get('href')
                    products.append({'category': category_name, 'title': title, 'price': price, 'image_url': image_url, 'product_url': product_url, 'supermarket': 'Arbuz'})

            print("Finished parsing current page")


            pagination = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.pagination.flex-wrap')))
            next_page_links = pagination.find_elements(By.CSS_SELECTOR, 'li.page-item:not(.disabled) a')
            
            next_page_link = None
            for link in next_page_links:
                if link.text.strip() == '»':
                    next_page_link = link
                    break
            
            if not next_page_link:
                break

            driver.execute_script("arguments[0].click();", next_page_link)
            
          
driver.quit()

with open('arbuz.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=4)
