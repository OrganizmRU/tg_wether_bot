import os
import requests
import argparse
from datetime import datetime
#from typing import Optional
#import json

def get_weather_on_cmd_line(location: str='Москва') -> None:
    """Получает текущую погоду из сервиса wttr.in и выводит в консоль"""

    location: str = encode_location(location)
    location: str = validate_city_ufa(location)

    url: str = f"https://wttr.in/{location}?format=j1&lang=ru"

    try:
        print(f'[->] Запрос по адресу {url}')
        response: requests.Response = requests.get(url, timeout=10)
        response.raise_for_status()  # Проверка на ошибки HTTP, если статус 4xx/5xx → HTTPError

        try:
            data: dict = response.json()
            # Сохранение JSON в файл для отладки
            #with open(f'json_{location}.txt', 'w') as file:
            #json.dump(data, file, indent=4, ensure_ascii=False)
        except ValueError as e:
            print(f"[!] Ошибка декодирования JSON: {e}")

        current_weather: dict = data['current_condition'][0]

        temperature: str = current_weather['temp_C']
        feels_like: str = current_weather['FeelsLikeC']
        pressure: str = current_weather['pressure']
        humidity: str = current_weather['humidity']
        wind_speed: str = current_weather['windspeedKmph']
        weather_desc: str = current_weather['lang_ru'][0]['value']
        latitude: str = data['nearest_area'][0]['latitude']
        longitude: str = data['nearest_area'][0]['longitude']
        area_name: str = data['nearest_area'][0]['areaName'][0]['value']

        print(f"""[°С] Погода в городе {area_name}:
            Температура: {temperature}°C
            Ощущается как: {feels_like}°C
            Влажность: {humidity}%
            Скорость ветра: {wind_speed} км/ч
            Давление: {pressure} кРа
            Описание: {weather_desc}
            Координаты: {latitude}, {longitude}""")

    except requests.exceptions.Timeout:
        print("[!] Таймаут при запросе к серверу")
    except requests.exceptions.ConnectionError:
        print("[!] Ошибка подключения: сервер недоступен")
    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP ошибка: {e}")
    except requests.RequestException as e: # Включает в себя Timeout, ConnectionError, HTTPError и др.
        print(f"[!] Ошибка при запросе: {e}")
    except KeyError as e:   # При обработке данных JSON (dict), когда нет нужного ключа
        print(f"[!] Ошибка при обработке данных: {e}")

    #ValueError → "У меня есть эта вещь, но она неправильная". Используется при при валидации введенных пользователем данных
    #KeyError → "У меня вообще нет такой вещи". Используется при разборе JSON ответов от API

def save_weather_to_png(location: str='Москва', file_name: str | None = None) -> None:
    """Сохраняет текущую погоду из сервиса wttr.in в указанный файл PNG"""

    # Проверка имени города для запроса
    encoded_location: str = encode_location(location)
    encoded_location: str = validate_city_ufa(encoded_location)

    url: str = f'https://wttr.in/{encoded_location}_pm_lang=ru.png'

    # Текущее время
    time_now: str = get_time_now()

    # Проверка имени файла для сохранения
    file_name = file_name or f'{location}_{time_now}.png'
    if '.png' not in file_name:
        file_name += '.png'

    # Проверка на уже существующий файл
    if should_fetch_weather_data(location, time_now, folder_path='.'):
        try:
            print(f'[->] Запрос по адресу {url}')
            response: requests.Response = requests.get(url, timeout=10)
            response.raise_for_status()  # Проверка на ошибки HTTP, если статус 4xx/5xx → HTTPError

            with open(os.path.join('images', file_name), 'wb') as file:
                file.write(response.content)

            print(f"[+] Погода для города {location} сохранена в файл {file_name}")

        except requests.exceptions.Timeout:
            print("[!] Таймаут при запросе к серверу")
        except requests.exceptions.ConnectionError:
            print("[!] Ошибка подключения: сервер недоступен")
        except requests.exceptions.HTTPError as e:
            print(f"[!] HTTP ошибка: {e}")
        except requests.RequestException as e:  # Включает в себя Timeout, ConnectionError, HTTPError и др.
            print(f"[!] Ошибка при запросе: {e}")
    else:
        print(f"[i] Файл {file_name} уже существует. Пропуск запроса.")

def should_fetch_weather_data(city: str, time: str, folder_path: str = ".") -> bool:
    """Проверяет, нужно ли запрашивать новые данные о погоде на основе времени последнего сохранения файла.
    True - нужно запрашивать, тк файл не существует
    False - не нужно запрашивать, тк файл уже есть"""

    file_name = f"{city}_{time}.png"
    file_path = os.path.join(folder_path, 'images', file_name)

    return False if os.path.exists(file_path) else True

def encode_location(location: str) -> str:
    """Меняет все пробелы на '+' для URL по требованию API"""
    return location.replace(' ', '+')

def get_time_now() -> str:
    """Возвращает текущее время в формате ГГГГ.ММ.ДД_ЧЧММ"""
    return datetime.now().strftime("%Y.%m.%d_%H%M")

def validate_city_ufa(city: str) -> str:
    """Специальная валидация для города Уфа"""
    if city.strip().lower() in ['уфа', 'ufa']:
        return '54.775,56.038'  # Координаты Уфы
    return city

def validate_city_arg(city: str) -> str:
    """Проверяет, что город состоит из букв, дефисов и пробелов"""
    city = city.strip()

    # Проверка на минимальную длину
    if len(city) < 2:
        raise argparse.ArgumentTypeError(f"[!] Название города слишком короткое: '{city}'")

    # Проверка на наличие цифр
    if any(char.isdigit() for char in city):
        raise argparse.ArgumentTypeError(f"[!] Название города не должно содержать цифры: '{city}'")

    return city.title()  # Приводим к нормальному виду

def main() -> None:
    """Точка входа с парсингом аргументов из командной строки."""

    # Получаем текущее время
    print(f"[t] Текущее время: {get_time_now()}")

    # Создаем парсер и описание
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="""
    Получение и сохранение погоды из wttr.in (по умолчанию в PNG)
    Страница проекта: https://github.com/chubin/wttr.in?tab=readme-ov-file    """,
    epilog="""
    Примеры использования:
    python weather.py --city Уфа
    python weather.py --city Казань --filename Kazan_weather.png
    python weather.py --city Москва --filename Москва_погода
    python weather.py --city 'New York' --noimage    """,
    formatter_class=argparse.RawDescriptionHelpFormatter)

    # Создаем папку для изображений, если ее нет
    os.makedirs('images', exist_ok=True)

    # Добавляем аргументы
    parser.add_argument('--city',
                        type=validate_city_arg,
                        default='Москва',
                        help='Целевой город для получения погоды')
    parser.add_argument('--noimage',
                        default=False,
                        action='store_true', # булевый флаг (переключатель)
                        help='Сохранить погоду в файл (PNG)')
    parser.add_argument('--filename',
                        type=str,
                        help='Имя файла для сохранения изображения погоды в формате PNG (по умолчанию <город>_<ГГГГ.ММ.ДД>_<ЧЧММ>.png)')

    # Парсим аргументы
    args = parser.parse_args()

    # Выполняем действия в зависимости от аргументов
    if args.noimage:
        get_weather_on_cmd_line(args.city)
    else:
        save_weather_to_png(args.city, args.filename)

if __name__ == "__main__":
    main()