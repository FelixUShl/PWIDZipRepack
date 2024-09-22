import logging
from log_conf import configure_logging

from IDServerUI import *
from createPDF import create_pdf
from createCSV import create_csv

logger = logging.getLogger(__name__)
qr_nums = 35


def get_file_name(qrs_list: list[dict]) -> str:
    qrs_names_list = sorted([qr['name'] for qr in qrs_list])
    return f'{qrs_names_list[0].rstrip(".png")[-6:]}-{qrs_names_list[-1].rstrip(".png")[-6:]}'


def zip_repack(qr_nums: int):

    buffer = io.BytesIO()
    result = ZipFile(buffer, "w")
    result.mkdir('images')
    try:
        qrs = get_images_from_server(qr_nums)
        file_name = get_file_name(qrs)
        logger.info(f'Выпущены запрошенные идентификаторы диапазон {file_name}')
    except QRServerError as e:
        return e
    pdf = create_pdf(qrs)
    logger.info(f'Создан файл {file_name}.pdf')
    csv = create_csv(qrs)
    logger.info(f'Создан файл {file_name}.csv')

    for qr in qrs:
        result.writestr(f'images/{qr["name"]}', qr['data'])
    result.writestr(f'{file_name}.pdf', pdf)
    result.writestr(f'{file_name}.csv', csv)
    result.close()
    logger.info(f'Архив {file_name}.zip создан')
    with open(f'{file_name}.zip', 'wb') as f:
        buffer.seek(0)
        f.write(buffer.read())
    return buffer.getvalue(), file_name


if __name__ == '__main__':
    configure_logging()
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    choice = True
    while choice:
        choice = input(
                       '1 - получить идентификаторы\n'
                       '2 - получить остаток\n'
                       '3 - найти идентификатор\n'
                       '0 - выйти\n'
                       'Выберите действие: ')
        if choice == '1':
            qr_nums = int(input('Введите количество идентификаторов: '))
            zip_repack(qr_nums)
        elif choice == '2':
            print(get_qr_nums())
        elif choice == '3':
            qr_id = input('Введите искомый id: ')
            print(get_status_id(qr_id))
        elif choice == '0':
            print('Выход')
            choice = False
        else:
            print('Неверный выбор\n')
            input(
                       '1 - получить идентификаторы\n'
                       '2 - получить остаток\n'
                       '3 - найти идентификатор\n'
                       '0 - выйти\n'
                       'Выберите действие: ')
