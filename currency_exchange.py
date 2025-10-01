import os
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv
#from typing import Optional
#import json

valid_currencies: list = ['RUB', 'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', \
                          'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTN', 'BWP', 'BYN', 'BZD', 'CAD', 'CDF', 'CHF', 'CLP', 'CNY', 'COP', \
                          'CRC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'FOK', 'GBP', \
                          'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', \
                          'INR', 'IQD', 'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KID', 'KMF', 'KRW', 'KWD', 'KYD', \
                          'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRU', 'MUR', \
                          'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', \
                          'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLE', 'SLL', \
                          'SOS', 'SRD', 'SSP', 'STN', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY', 'TTD', 'TVD', 'TWD', 'TZS', \
                          'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VES', 'VND', 'VUV', 'WST', 'XAF', 'XCD', 'XCG', 'XDR', 'XOF', 'XPF', 'YER', \
                          'ZAR', 'ZMW', 'ZWL']

# Инфа по ошибкам https://www.exchangerate-api.com/docs/pair-conversion-requests
# Инфа по ошибкам https://www.exchangerate-api.com/docs/historical-data-requests
error_api: dict = {
    "no-data-available": "Нет курсов обмена валют на указанную дату",
    "unsupported-code": "Неподдерживаемый код валюты",
    "malformed-request": "Запрос не соответствует структуре",
    "invalid-key": "Ключ API недействителен",
    "inactive-account": "Адрес электронной почты не был подтвержден",
    "quota-reached": "Достигнут лимит запросов",
    "plan-upgrade-required": "Уровень подписки не поддерживает этот тип запроса"}

def get_current_exchange_rate(api_key: str, base_code: str='USD', target_code: str='RUB') -> float:
    """Получает текущий курс валют
    1 - Отправляем запрос на сервер. Можем получить ошибки:
     1.1 - requests.exceptions.Timeout
     1.2 - requests.exceptions.ConnectionError
    2 - Пытаемся прочитать JSON, даже при ошибках HTTP. При ошибке декодирования получим ValueError
    3 - Если получили JSON и там:
     3.1 - ошибка API, то расшифровываем полученную ошибку
     3.2 - нет ошибки API, проверяем на ошибки HTTP, если статус 4xx/5xx → HTTPError
    4 - если нет ошибки API и нет ошибки HTTP, обрабатываем результат (статус 200-399)"""

    url = f'https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_code}/{target_code}'

    try:
        print(f'[->] Запрос по адресу {url}')
        response: requests.Response = requests.get(url, timeout=10)

        # Всегда пытаемся прочитать JSON, даже при ошибках HTTP. При ошибке получим ValueError
        try:
            data: dict = response.json()
        except ValueError as e:
            print(f"[!] Ошибка декодирования JSON: {e}")
            return 0.0

        # Если получили JSON и там ошибка API, то расшифровываем полученную ошибку
        if data and data.get("result") == "error":
            error_type = data.get("error-type")
            print(f"[!] Ошибка API: {error_api[error_type]}")
            return 0.0

        # Проверка на ошибки HTTP, если статус 4xx/5xx → HTTPError
        response.raise_for_status()

        # Если нет ошибки API и нет ошибки HTTP, обрабатываем результат (статус 200-399)
        if data and data.get("result") == "success":
            print(f"[ok] Курс валюты: 1 {base_code} стоит {data["conversion_rate"]} {target_code}")
            return data["conversion_rate"]

    except requests.exceptions.Timeout:
        print("[!] Таймаут при запросе к серверу")
        return 0.0
    except requests.exceptions.ConnectionError:
        print("[!] Ошибка подключения: сервер недоступен")
        return 0.0
    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP ошибка: {e}")
        return 0.0
    except requests.RequestException as e:  # Включает в себя Timeout, ConnectionError, HTTPError и др.
        print(f"[!] Ошибка при запросе: {e}")
        return 0.0
    except KeyError as e:   # Если отсутствует ключ в полученных данных JSON'а
        print(f"[!] Ошибка при обработке данных: отсутствует ключ {e}")
        return 0.0

def get_history_exchange_rate(api_key: str, base_code: str='USD', target_code: str='RUB',
                              yyyy: str='2025', mm: str='01', dd: str='01', amount: str=1.0) -> float | None:
    """Получает исторический курс валют на день запроса
    1 - Отправляем запрос на сервер. Можем получить ошибки:
     1.1 - requests.exceptions.Timeout
     1.2 - requests.exceptions.ConnectionError
    2 - Пытаемся прочитать JSON, даже при ошибках HTTP. При ошибке декодирования получим ValueError
    3 - Если получили JSON и там:
     3.1 - ошибка API, то расшифровываем полученную ошибку
     3.2 - нет ошибки API, проверяем на ошибки HTTP, если статус 4xx/5xx → HTTPError
    4 - если нет ошибки API и нет ошибки HTTP, обрабатываем результат (статус 200-399)"""

    url = f'https://v6.exchangerate-api.com/v6/{api_key}/history/{base_code}/{yyyy}/{mm}/{dd}/{amount}'

    try:
        print(f'[->] Запрос по адресу {url}')
        response: requests.Response = requests.get(url, timeout=10)

        # Всегда пытаемся прочитать JSON, даже при ошибках HTTP. При ошибке получим ValueError
        try:
            data: dict = response.json()
        except ValueError as e:
            print(f"[!] Ошибка декодирования JSON: {e}")
            return None

        # Если получили JSON и там ошибка API, то расшифровываем полученную ошибку
        if data and data.get("result") == "error":
            error_type = data.get("error-type")
            print(f"[!] Ошибка API: {error_api[error_type]}")
            return None

        # Проверка на ошибки HTTP, если статус 4xx/5xx → HTTPError
        response.raise_for_status()

        # Если нет ошибки API и нет ошибки HTTP, обрабатываем результат (статус 200-399)
        if data and data.get("result") == "success":
            print(f"[ok] Курс валюты на {yyyy}.{mm}.{dd}: 1 {base_code} стоит {data["conversion_rate"][target_code]} {target_code}")
            return data["conversion_rate"][target_code]

    except requests.exceptions.Timeout:
        print("[!] Таймаут при запросе к серверу")
        return None
    except requests.exceptions.ConnectionError:
        print("[!] Ошибка подключения: сервер недоступен")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP ошибка: {e}")
        return None
    except requests.RequestException as e: # Включает в себя Timeout, ConnectionError, HTTPError и др.
        print(f"[!] Ошибка при запросе: {e}")
        return None
    except KeyError as e:   # Если отсутствует ключ в полученных данных JSON'а
        print(f"[!] Ошибка при обработке данных: отсутствует ключ {e}")
        return None

def get_time_now() -> str:
    """Возвращает текущее время в формате ГГГГ.ММ.ДД_ЧЧ:ММ"""
    return datetime.now().strftime("%Y.%m.%d_%H:%M")

def validate_currency_arg(currency: str) -> str:
    """Проверяет, что валютный код существует и корректен."""
    currency = currency.strip().upper()

    # Проверка на корректность кода валюты
    if currency not in valid_currencies:
        raise argparse.ArgumentTypeError(f"[!] Название валюты не существует: '{currency}'")

    return currency

def validate_date(yyyy: str, mm: str, dd: str) -> bool:
    """Проверяет валидность даты"""
    try:
        # Пробуем создать дату
        date = datetime(int(yyyy), int(mm), int(dd))

        # Дополнительная проверка - дата не должна быть в будущем
        if date > datetime.now():
            print("[!] Дата не может быть в будущем")
            return False

        return True
    except ValueError as e:
        print(f"[!] Некорректная дата: {e}")
        return False

def main() -> None:
    """Точка входа с парсингом аргументов из командной строки."""

    load_dotenv()  # Загружаем переменные окружения из файла .env

    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise RuntimeError("API_KEY не задан")

    # Создаем парсер
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="""
    Получение курса валют из сервиса exchangerate-api.com
    Страница документации: https://www.exchangerate-api.com/docs/overview""",
    epilog="""
    Примеры использования:
    python currency_exchange.py current
    python currency_exchange.py --base CAD --target RUB current
    python currency_exchange.py --base CAD --target RUB convert 123.45
    python currency_exchange.py --base CAD --target EUR history -y 2023 -m 10 -d 05 -a 100""",
    formatter_class=argparse.RawDescriptionHelpFormatter)

    # Добавляем аргументы
    parser.add_argument('-bc', '--base',
                        type=validate_currency_arg,
                        default='USD',
                        help='Базовая валюта')

    parser.add_argument('-tc', '--target',
                        type=validate_currency_arg,
                        default='RUB',
                        help='Целевая валюта')

    subparser = parser.add_subparsers(dest='command', required=True, help='Доступные команды')

    current_subparser = subparser.add_parser('current', help='Текущий курс валюты')

    history_subparser = subparser.add_parser('history', help='Исторический курс валюты')
    history_subparser.add_argument('-y', '--yyyy', required=True, help='Год')
    history_subparser.add_argument('-m', '--mm', required=True, help='Месяц')
    history_subparser.add_argument('-d', '--dd', required=True, help='День')
    history_subparser.add_argument('-a', '--amount', type=float, default=1.0, help='Сумма для конвертации') # Не обязательно, по умолчанию 1.0

    convert_subparser = subparser.add_parser('convert', help='Конвертация валюты по текущему курсу')
    convert_subparser.add_argument('amount', type=float, help='Сумма для конвертации')

    # Парсим аргументы
    args = parser.parse_args()

    # Получаем текущее время
    print(f"[t] Текущее время: {get_time_now()}")

    if args.command == 'current':
        get_current_exchange_rate(API_KEY, args.base, args.target)
    elif args.command == 'history':
        if validate_date(args.yyyy, args.mm, args.dd):  # Проверяем валидность даты
            get_history_exchange_rate(API_KEY, args.base, args.target, args.yyyy, args.mm, args.dd, args.amount)
    elif args.command == 'convert':
        rate = get_current_exchange_rate(API_KEY, args.base, args.target)
        if rate != 0.0:
            print(f"[ok] {args.amount} {args.base} стоит {args.amount * rate:.2f} {args.target}")

if __name__ == "__main__":
    main()