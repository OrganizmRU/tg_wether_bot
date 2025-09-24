import requests

def get_json_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP

        # Парсим JSON
        json_data = response.json()
        return json_data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return None

# Пример использования

if __name__ == "__main__":
    url = "https://vpnetwork.site/"
    data = get_json_from_url(url)

    if data:
        print("Успешно получен JSON:")
        #print(data)

    print(f'Версия: {data['cobalt']['version']}')
