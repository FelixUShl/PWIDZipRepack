from fpdf import FPDF
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


def new_page(pdf: FPDF):
    pdf.add_page()
    pdf.set_x(20)
    pdf.image("https://proxway-ble.ru/images/logo.svg", w=50)
    pdf.set_xy(140, 10)
    pdf.set_font("Helvetica", size=16)
    pdf.multi_cell(w=60, text="https://proxway-ble.ru\n8 800 700-19-57\ninfo@proxway-ble.ru")
    pdf.set_font("Helvetica", size=6.3)


def draw_cell(pdf: FPDF, x: int, y: int, qr: dict):
    pdf.set_xy(x, y)
    pdf.image(qr['data'], w=30)
    text = f'HEX 8b:{hex8b(qr["name"])}\n'
    text += f"DEC 3b: {dec3b(qr['name'])}\n"
    text += f"FC 3b: {fac_code(qr['name'])}"
    pdf.multi_cell(w=31, text=text)


def generate_table(pdf: FPDF, data: list[dict]):
    step_y = 30  # стартовый отступ от верхнего края
    step_x = 20  # стартовый отступ от бокового края
    step = 1  # считаем до 5х - кол-во столбцов
    for elem in data:
        draw_cell(pdf, step_x, step_y, elem)
        if step != 5:
            step_x += 37
            step += 1
        else:
            if (data.index(elem) + 1) % 30 == 0 and (data.index(elem) + 1) != len(data):
                new_page(pdf)
                step_y = 30  # стартовый отступ от верхнего края
                step_x = 20  # стартовый отступ от бокового края
            else:
                step_x = 20
                step_y += 42
            step = 1


def create_pdf(qrs_list: list[dict]) -> bytearray:
    pdf = FPDF("P", "mm", "A4")
    new_page(pdf)
    generate_table(pdf, qrs_list)
    return pdf.output()
