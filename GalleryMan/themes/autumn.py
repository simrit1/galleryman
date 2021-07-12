from GalleryMan.themes.coloreplacer import ColorReplacer
from PIL import ImageQt


def autumn(img):
    x = ColorReplacer(img, (237, 197, 150))

    image = x.convert()

    return ImageQt.ImageQt(image)


def nostalgia(img):

    x = ColorReplacer(img, (217, 198, 198))

    image = x.convert()

    return ImageQt.ImageQt(image)


def deep(img):
    x = ColorReplacer(img, (54, 69, 79))

    image = x.convert()

    return ImageQt.ImageQt(image)


def cream(img):
    x = ColorReplacer(img, (247, 219, 236))

    image = x.convert()

    return ImageQt.ImageQt(image)


def cozy(img):
    x = ColorReplacer(img, (151, 148, 200))

    image = x.convert()

    return ImageQt.ImageQt(image)


def blossom(img):
    x = ColorReplacer(img, (243, 206, 245))

    image = x.convert()

    return ImageQt.ImageQt(image)


def breeze(img):
    x = ColorReplacer(img, (0, 139, 186))

    image = x.convert()

    return ImageQt.ImageQt(image)


def evergreen(img):
    x = ColorReplacer(img, (194, 213, 168))

    image = x.convert()

    return ImageQt.ImageQt(image)