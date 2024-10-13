import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Запуск браузера
browser = webdriver.Chrome()

# Открытие страницы
url = "https://www.codewars.com/kata/search/python?q=&r%5B%5D=-7&beta=false&order_by=rank_id%20asc"
browser.get(url)


def scroll_to_bottom(browser, pause_time=2):
    """Функция для прокрутки страницы до конца."""
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Прокрутить страницу до низа
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Ждать паузу для подгрузки контента
        time.sleep(pause_time)

        # Получить новую высоту страницы после прокрутки
        new_height = browser.execute_script("return document.body.scrollHeight")

        # Если высота страницы не изменилась, выйти из цикла
        if new_height == last_height:
            break

        last_height = new_height


# Прокрутить страницу до конца
scroll_to_bottom(browser)

# После прокрутки получить HTML-код страницы
html_source = browser.page_source

list_card_url = []
# Передать HTML-код страницы в BeautifulSoup
soup = BeautifulSoup(html_source, 'lxml')
data = soup.find_all('div', class_="list-item-kata bg-ui-section p-4 rounded-lg shadow-md")

# Сбор данных
for i in data:
    card_url = "https://www.codewars.com" + i.find('a').get('href')
    list_card_url.append(card_url)

def scrape_details(link):
    """Функция для сбора деталей задачи и записи их в файл."""
    try:
        browser.get(link)

        # Ждем, пока появится нужный элемент с описанием задачи
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "markdown"))
        )

        detail_html = browser.page_source
        detail_soup = BeautifulSoup(detail_html, 'lxml')

        # Найти описание задачи
        task = detail_soup.find('div', {'class': 'markdown'})
        if task:
            task_text = task.text.strip()

            # Открыть файл для записи (режим 'a' - добавление)
            with open('tasks2.txt', 'a', encoding='utf-8') as file:
                file.write(f"URL: {link}\n")  # Записать ссылку
                file.write(f"Задача:\n{task_text}\n")  # Записать задачу
                file.write("="*40 + "\n")  # Разделитель для каждой задачи

            print(f"Задача с {link} записана.")
        else:
            print(f"Не удалось найти описание для {link}")
    except Exception as e:
        print(f"Ошибка при обработке {link}: {e}")

# Используем многопоточность для обработки ссылок
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(scrape_details, list_card_url)

# Закрыть браузер
browser.quit()



