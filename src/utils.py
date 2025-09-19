from PIL import Image, ImageDraw, ImageFont
from functools import wraps
from app_config import Config

config = Config()

romanNumeralMap = (
    ('M', 1000),
    ('CM', 900),
    ('D', 500),
    ('CD', 400),
    ('C', 100),
    ('XC', 90),
    ('L', 50),
    ('XL', 40),
    ('X', 10),
    ('IX', 9),
    ('V', 5),
    ('IV', 4),
    ('I', 1)
)

def toRoman(n: int):
    """convert integer to Roman numeral"""
    n = int(n)

    limit_reached = False
    if not -1 < n < 5000:
        n = 4999
        limit_reached = True

    # special case
    if n == 0:
        return 'N'

    result = ""
    for numeral, integer in romanNumeralMap:
        while n >= integer:
            result += numeral
            n -= integer
    return result + ('+' if limit_reached else '')

def get_text_width(text: str) -> float:
    image = Image.new('RGB', (1,1))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(config.current_lang['font'], 50)
        
    text_width = 0
        
    for char in text:
        text_width += draw.textlength(char, font=font)
        
    return text_width 