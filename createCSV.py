import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import logging

logger = logging.getLogger(__name__)

def hex8b(qr_name: str) -> str:
    return qr_name[:-4].upper()


def dec3b(qr_name: str) -> str:
    return str(int(qr_name[-10:-4], 16))


def fac_code(qr_name: str) -> str:
    fc = str(int(hex8b(qr_name)[-6:-4], 16))
    code = str(int(hex8b(qr_name)[-4:], 16))
    return f"{fc},{code}"


def qr_read(image):
    nparr = np.fromstring(image, np.uint8)
    image_m = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    decoded_objects = pyzbar.decode(image_m)
    return decoded_objects[0].data.decode('utf-8')


def create_csv(images: list[dict]) -> str:
    csv_str = 'qr_url;hex8b;dec3b;fac_code\n'
    for image in images:
        qr_url = qr_read(image['data'])
        csv_str += f"{qr_url};{hex8b(image['name'])};{dec3b(image['name'])};{fac_code(image['name'])}\n"
    return csv_str.rstrip('\n')
