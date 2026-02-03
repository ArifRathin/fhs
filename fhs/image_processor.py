from PIL import Image
from io import BytesIO
from django.core.files import File


def processImage(photo):
    image = Image.open(photo)
    width = image.width
    height = image.height
    if width >= height:
        factor = round(width/height, 2)
        if width >=1500 and width <= 3000:
            width = width//2
        elif width > 3000 and width <=5000:
            width = width//3
        elif width > 5000:
            width = width//4
        height = width//factor
    else:
        factor = round(height/width, 2)
        if height >= 1500 and height <=3000:
            height = height//2
        elif height > 3000 and height <= 5000:
            height = height//3
        elif height > 5000:
            height = height//4
        width = height//factor
    size = (width, height)
    image = image.resize(size)
    io = BytesIO()
    image.save(io, 'JPEG', quality=23)
    image_file = File(io, name=photo.name)

    return image_file