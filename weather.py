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
    print(f'[->] Запрос по адресу {url}')

    try:
        response: requests.Response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data: dict = response.json()

        # Сохранение JSON в файл для отладки
        #with open(f'json_{location}.txt', 'w') as file:
        #    json.dump(data, file, indent=4, ensure_ascii=False)

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

    except requests.RequestException as e:
        print(f"[!] Ошибка при запросе: {e}")
    except KeyError as e:
        print(f"[!] Ошибка при обработке данных: {e}")

def save_weather_to_png(location: str='Москва', file_name: str | None = None) -> None:
    """Сохраняет текущую погоду из сервиса wttr.in в указанный файл PNG"""

    encoded_location: str = encode_location(location)

    url: str = f'https://wttr.in/{encoded_location}_pm_lang=ru.png'
    print(f'[->] Запрос по адресу {url}')

    file_name = file_name or f'{location}_{get_time_now()}.png'

    if '.png' not in file_name:
        file_name += '.png'

    try:
        response: requests.Response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP

        with open(file_name, 'wb') as file:
            file.write(response.content)

        print(f"[+] Погода для города {location} сохранена в файл {file_name}")
    except requests.RequestException as e:
        print(f"[!] Ошибка при запросе: {e}")

def encode_location(location: str) -> str:
    """Меняет все пробелы на '+' для URL по требованию API"""
    return location.replace(' ', '+')

def get_time_now() -> str:
    """Возвращает текущее время в формате ГГГГ.ММ.ДД_ЧЧ:ММ"""
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

    # Создаем парсер
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="""Получение и сохранение погоды из wttr.in (по умолчанию в PNG)
                                                              Страница проекта: https://github.com/chubin/wttr.in?tab=readme-ov-file""",
                                                              epilog='Пример использования: python weather.py --city "Екатеринбург" --image --filename "Екат_2025.09.27.png"')
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
                        help='Имя файла для сохранения изображения погоды в формате PNG (по умолчанию <город>.png)')

    # Парсим аргументы
    args = parser.parse_args()

    # Выполняем действия в зависимости от аргументов
    if args.noimage:
        get_weather_on_cmd_line(args.city)
    else:
        save_weather_to_png(args.city, args.filename)

if __name__ == "__main__":
    main()