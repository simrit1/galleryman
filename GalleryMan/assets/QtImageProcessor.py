from PIL.ImageQt import ImageQt
from PIL import Image
from PIL.ImageFilter import *
from PIL import ImageEnhance


class ImageProcessor:
    def __init__(self) -> None:
        self.deg = 0

    def add_image(self, image):
        self.image = Image.open(image)

    def rotate(self):
        self.deg = self.deg + 90

        self.image = self.image.rotate(self.deg)

        return ImageQt(self.image)

    def blur(self):
        self.image = self.image.filter(BLUR)

        return ImageQt(self.image)

    def sharpen(self):
        self.image = self.image.filter(SHARPEN)

        return ImageQt(self.image)

    def increaseBrightness(self):
        enhancer = ImageEnhance.Brightness(self.image)

        self.image = enhancer.enhance(1.1)

        return ImageQt(self.image)

    def increaseContrast(self):
        enhancer = ImageEnhance.Contrast(self.image)

        self.image = enhancer.enhance(1.1)

        return ImageQt(self.image)

    def increaseExposure(self, intensity=200):
        color = Image.new("RGB", self.image.size, (255, 255, 255))
            
        intensity = abs(intensity)

        mask = Image.new("RGBA", self.image.size, (0, 0, 0, intensity))

        self.image = Image.composite(self.image, color, mask).convert("RGB")

        return ImageQt(self.image)