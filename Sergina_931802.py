from datetime import datetime
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
import pytz
import json
import requests


def web_app(environment, response):
    status = "200 OK"

    method = environment['REQUEST_METHOD']
    query_string = environment['QUERY_STRING']
    parsed_query_string = parse_qs(query_string)

    path_info = environment['PATH_INFO']

    some = int(environment.get('CONTENT_LENGTH')) if environment.get('CONTENT_LENGTH') else 0
    body = environment['wsgi.input'].read(some) if some > 0 else ''

    answer = str(datetime.now().time())

    # Пункт 1
    # Если нет QUERY_STRING, т.е. пользователь делает запрос 127.0.0.1:8000 без параметров
    if query_string == "" and method == "GET":
        print("Пункт 1: Верни время сервера")
        answer = str(datetime.now().time())
        headers = [('Content-type', 'text/html; charset=utf-8')]
        response(status, headers)

    # Пункт 2
    # Если пользователь указывает временную зону в QUERY_STRING, например 127.0.0.1:8000/?tz=Europe\London
    elif query_string != "" and method == "GET":
        print("Пункт 2: Верни время временной зоны")
        # достаем из словаря значение параметра tz, т.е. например Europe\Berlin
        tz_string = parsed_query_string['tz'][0]
        # конвертируем string в объект типа pytz.timezone
        tz = pytz.timezone(tz_string)
        # конвертируем время сервера используя временную зону указанную пользователем
        answer = str(datetime.now(tz).time())
        headers = [('Content-type', 'text/html; charset=utf-8')]
        response(status, headers)

    # Пункт 3,4
    # Если нет QUERY_STRING, т.е. пользователь делает запрос 127.0.0.1:8000/api/v1/time или 127.0.0.1:8000/api/v1/date
    elif query_string == "" and method == "POST" and body == "":
        print("Пункт 3,4: Верни время/дату сервера")
        if "time" in path_info:
            answer = str(datetime.now().time())
        if "date" in path_info:
            answer = str(datetime.now().date())
        headers = [('Content-type', 'text/json; charset=utf-8')]
        response(status, headers)

    # Если пользователь указывает временную зону в QUERY_STRING, например 127.0.0.1:8000/api/v1/time/?tz=Europe\Berlin
    # или 127.0.0.1:8000/api/v1/date/?tz=Europe\Berlin
    elif query_string != "" and method == "POST":
        print("Пункт 3,4: Верни время/дату временной зоны")
        tz_string = parsed_query_string['tz'][0]
        tz = pytz.timezone(tz_string)
        if "time" in path_info:
            answer = str(datetime.now(tz).time())
        if "date" in path_info:
            answer = str(datetime.now(tz).date())
        headers = [('Content-type', 'text/json; charset=utf-8')]
        response(status, headers)

    # Пункт 5
    # Если пользователь делает запрос 127.0.0.1:8000/api/v1/datediff
    elif query_string == "" and method == "POST" and body != "":
        print("Пункт 5: Верни разницу между датами временных зон")
        body = body.decode().split('\r\n')
        json_string_start = body[0]
        start = json.loads(json_string_start)
        json_string_end = body[1]
        end = json.loads(json_string_end)

        start_date = start['date']
        end_date = end['date']

        datetime_start = get_date(start_date)
        datetime_end = get_date(end_date)

        answer = str(datetime_end - datetime_start)
        headers = [('Content-type', 'text/json; charset=utf-8')]
        response(status, headers)

    else:
        answer = "Не знаю как обработать запрос"

    if method == "GET":
        print("Я получил GET запрос!")
    elif method == "POST":
        print("Я получил POST запрос!")
    else:
        print("Я не имею понятия, что это за запрос")

    print("Тип запроса, который я получил это ---->" + method)
    print("QUERY_STRING, который я получил это ---->" + query_string)
    print(answer)

    return [answer.encode()]


def run_tests():
    print("Checking request 1:")
    response = requests.get("https://127.0.0.1:8000/")
    print(response)

    print("Checking request 2:")
    response = requests.get("https://127.0.0.1:8000/?tz=Europe/Berlin")
    print(response)

    print("Checking request 3:")
    response = requests.post("https://127.0.0.1:8000/api/v1/date")
    print(response)

    print("Checking request 4:")
    response = requests.post("https://127.0.0.1:8000/api/v1/time")
    print(response)


def get_date(date_string):

    try:
        datetime_start = datetime.strptime(date_string, '%m.%d.%Y %H:%M:%S')
        return datetime_start

    except ValueError:
        print("first date format don't match!")

    try:
        datetime_end = datetime.strptime(date_string, '%I:%M%p %Y-%m-%d')
        return datetime_end

    except ValueError:
        print("second date format don't match!")

    return datetime.now()


with make_server('', 8000, web_app) as server:
    print("Serving on port 8000...\nVisit 127.0.0.1:8000\nTo kill the server enter Ctrl+C")
    server.serve_forever()
