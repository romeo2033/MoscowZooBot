from PIL import Image, ImageDraw, ImageFont
from config import pics

# for _ in pics.values():
#     img = Image.open(f'pics/{_}.jpg')
#     text = 'TG: @totemAnimal_2024bot'
#     fontP = "ALSMendeleev-Black.otf"
#     draw = ImageDraw.Draw(img)
#     font = ImageFont.truetype("ALSMendeleev-Black.otf", 30)
#     W = 1000
#     w = draw.textlength(text,font_size=30, font=font)
#     draw.text(((W-w)/2, 25),text,(41,100,86),font=font)
#     img.save(f'pics/{_}.jpg')
