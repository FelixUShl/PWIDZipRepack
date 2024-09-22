import os
from zipfile import ZipFile
import io
import logging
import datetime

import dotenv
import requests

logger = logging.getLogger(__name__)
class QRServerError(Exception):
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        return f'{self.message}'


def get_images_from_server(qr_nums: int) -> list[dict]:
    """images = list()
    test_data = io.BytesIO(requests.get('http://big-b.xyz:40001/f04c2bde059f4c13b69dd6176e7e592c_0.zip').content)
    with ZipFile(test_data, "r") as archive:
        for name in archive.namelist():
            images.append({'name': name.split('/')[1], 'data': archive.read(name)})
    """
    logger.info(f'Получен запрос на выпуск {qr_nums} идентификаторов')
    dotenv.load_dotenv('.env')
    url = os.getenv('URL')
    passwrd = os.getenv('PASS')
    login = os.getenv('LOGIN')

    with requests.Session() as session:
        fields = {
            ('email', (None, login)),
            ('password', (None, passwrd))
        }
        session.post(f"{url}/perform/login", files=fields)
        fields.add(('labels_number', (None, qr_nums)))
        resp = session.post(f"{url}/perform/labels/list/produce", files=fields)
        result = resp.content.decode("utf-8")
        f = True
        images = list()
        for i in result.split('"'):
            if i.startswith('/download'):
                f = False
                with ZipFile(io.BytesIO(session.get(f"{url}{i}").content), "r") as archive:
                    logger.info(f'{qr_nums} идентификаторов выпущено')
                    for name in archive.namelist():
                        images.append({'name': name.split('/')[1], 'data': archive.read(name)})
                break
        if f:
            for i in result.split('<div'):
                if 'color: #f00' in i:
                    e = i.split('>')[1].split('<')[0]
                    logger.error(f'Ошибка при выпуске идентификаторов: {e}')
                    raise QRServerError(e)
    return sorted(images, key=lambda x: x['name'])


def get_qr_nums() -> int:
    dotenv.load_dotenv('.env')
    url = os.getenv('URL')
    passwrd = os.getenv('PASS')
    login = os.getenv('LOGIN')
    logger.info(f'Получен запрос на определение количества идентификаторов')
    with requests.Session() as session:
        fields = {
            ('email', (None, login)),
            ('password', (None, passwrd))
        }
        resp = session.post(f"{url}/perform/login", files=fields).content.decode("utf-8")
        for i in resp.split('>'):
            if 'лимит на выпуск идентификаторов:' in i:
                result = int(i.split(':')[1].split('<')[0].strip())
                logger.info(f'Ответ на запрос отправлен. Осталось {result}')
                return result


def get_qrs_list(from_date="2023-05-17", to_date="today") -> list[{}]:
    """
    Функция получения списка выпущенных идентификаторов, по умолчанию за все время. Получает на вход токен сессии и даты
    начала и конца периода сбора инфы
    :param session: ID сессии
    :param from_date: начало списка
    :param to_date: конец списка
    :return: список с параметрами найденных идентификаторов
    """
    dotenv.load_dotenv('.env')
    url = os.getenv('URL')
    passwrd = os.getenv('PASS')
    login = os.getenv('LOGIN')
    logger.info(f'Начинается формирование списка выпущенных идентификаторов')
    if to_date == "today":
        to_date = datetime.date.today()

    with requests.Session() as session:
        fields = {
            ('email', (None, login)),
            ('password', (None, passwrd))
        }
        session.post(f"{url}/perform/login", files=fields)

        datas = {"from_date": from_date,
                 "to_date": to_date}
        response = session.get(f"{url}/request/history/produced/by/period/l", data=datas)
    res = list()
    for table_row in response.text.split("<tr>"):
        if "<td>" in table_row:
            table_row = table_row.split("<td>")
            res.append({
                "date_time": table_row[1].split("</td>")[0],
                "id": table_row[2].split("</td>")[0],
                "name": table_row[3].split("</td>")[0],
                "s_name": table_row[4].split("</td>")[0],
                "email": table_row[5].split("</td>")[0],
                "status": table_row[6].split("</td>")[0]})

    return res


def get_status_id(qr_id) -> str:
    """
    Функция получения статуса идентификатора. На вход получает полный код идентификатора и ID сессии, возвращает статус
    идентификатора, или ошибку не найдено
    :param qr_id: номер идетификатора
    :param session: ID сессии
    :return: статус или ошибка не найдено
    """
    if isinstance(qr_id, int):
        qr_id = str(qr_id)
    qr_id= qr_id.lower()
    logger.info(f'Получен запрос на определение статуса идентификатора {qr_id}')
    for i in get_qrs_list():
        if qr_id == i["id"]:
            logger.info(f'Статус идентификатора {qr_id}: {i["status"].upper()}')
            return i["status"].upper()
    else:
        logger.error(f'Идентификатор {qr_id} не найден')
        return "NotFound"
