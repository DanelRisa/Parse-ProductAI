import json
import os
import streamlit as st
import openai
from dotenv import load_dotenv

load_dotenv()f
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def get_products_by_name(data, product_name, category=None):
    found_products = []
    for product in data:
        product_title = product["title"]
        product_category = product["category"]
        similarity = fuzz.token_set_ratio(product_name.lower(), product_title.lower())
        if similarity >= 75:
            if category is None or category.lower() == product_category.lower():
                found_products.append(product)
    return found_products


def get_cheapest_product(data, product_name, category=None):
    products = get_products_by_name(data, product_name, category)
    if products:
        try:
            cheapest_product = min(products, key=lambda p: float(p["price"].replace(" ", "").replace(",", "").replace("₸", "")))
            return cheapest_product
        except ValueError:
            return None
    return None


openai.api_key = os.getenv('OPENAI_API_KEY')


def generate_gpt_response(prompt, api_key):
    load_dotenv()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[
            {"role": "system", "content": "You are a helpful cooking assistant."},
            {"role": "user", "content": "напиши только список продуктов без обьяснений, граммовок, цифр только продукты для приготовления блюда " + prompt + "и определи каждый ингредиент рецепта в какой из перечисленных категорий относится исходя из названия продукта и его предназначени для использования Бакалея, Овощи и фрукты, Колбасы и сыры, Кондитерские изделия, Консервы, Молочные продукты и яйца, Напитки и алкогольные напитки, Полуфабрикаты, Хлеб и хлебобулочные изделия, Чай и кофе и какао, Мясо и рыба и птица. Напиши ответ в виде название продукта, категории и  ничего лишнего. Если зелень, мясо, специи то сразу уточни какая, не используй слово зелень. НЕ ИСПОЛЬЗУЙ слово яйца, используй яйцо. Если растительное масло то напиши сразу какой подсолнечное масло или другие виды. УКРОП относится категории Овощи и фрукты. Пиши название продукта - категорию. НЕ ИСПОЛЬЗУЙ СКОБКИ"}
        ],
        max_tokens=2500,
        n=1,
        stop=None,
        temperature=0.0,
        api_key=api_key
    )

    return response.choices[0].message.get('content', '')


def parse_ingredients_from_gpt_response(response):
    ingredient_lines = response.split("\n")
    ingredients = []
    for ingredient_line in ingredient_lines:
        parts = ingredient_line.split(" -", 1)

        if len(parts) == 2:
            ingredient = parts[0].strip()
            category = parts[1].strip()
            ingredients.append((ingredient, category))
    return ingredients


def main():
    st.set_page_config(page_title="Ask your ProductAI")
    st.header("Ask your Assistant 💬")

    if 'history' not in st.session_state:
        st.session_state.history = []

    # read data from file
    with open("arbuz.json", "r") as file:
        data = json.load(file)

    api_key = os.getenv('OPENAI_API_KEY')  # Assuming that the API key is stored in an environment variable

    # show user input
    user_question = st.text_input("Ask a question about a dish you want to cook:")
    user_budget = st.number_input("Enter your budget:")
    if user_question:
        user_question = user_question.lower().strip()

        gpt_response = generate_gpt_response(user_question, api_key)
        ingredients = parse_ingredients_from_gpt_response(gpt_response)

        for ingredient, category in ingredients:
            cheapest_product = get_cheapest_product(data, ingredient, category)

            if cheapest_product:
                st.write(f"{ingredient} - {category}:")

                st.write(cheapest_product["title"])
                st.write("Цена: " + cheapest_product["price"])
            else:
                # Если не найден самый дешевый продукт для указанного ингредиента, ищите продукт по категории
                category_products = get_products_by_name(data, ingredient, category)
                if category_products:
                    st.write("Товар", ingredient, "из категории", category, ":")
                    st.write(category_products[0]["title"])
                    st.write("Цена: " + category_products[0]["price"])
                else:
                    st.write(f"Товар {ingredient} не найден.")

        st.session_state.history.append({
            'question': user_question,
            'response': gpt_response
        })

    # история чата
    st.subheader("Chat History:")
    for entry in st.session_state.history:
        st.write("Question:", entry['question'])
        st.write("Response:", entry['response'])
        st.write("-" * 50)


if __name__ == '__main__':
    main()
