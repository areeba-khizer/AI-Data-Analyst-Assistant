import os

from utils.pdf_generator import generate_pdf


def test_pdf_generation():

    path = generate_pdf("Hello World")

    assert os.path.exists(path)