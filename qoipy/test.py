from itertools import chain
from pathlib import Path

from PIL import Image
from pytest import mark

from qoi import encode, decode

files = set([f.stem for f in Path("..", "qoi_test_images").iterdir() if f.is_file()])


@mark.parametrize("fn", files)
def test_encode(fn: Path):
    path = Path("..", "qoi_test_images") / fn
    png = Image.open(str(path) + ".png")
    qoi = open(str(path) + ".qoi", "rb").read()
    assert encode(png) == qoi


@mark.parametrize("fn", files)
def test_decode(fn: Path):
    path = Path("..", "qoi_test_images") / fn
    png = Image.open(str(path) + ".png")
    png = bytearray(chain(*png.getdata()))
    qoi = open(str(path) + ".qoi", "rb").read()
    assert decode(qoi) == png
