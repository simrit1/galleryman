from PIL import Image , ImageQt
from GalleryMan.themes.filters import Filters
import json
from GalleryMan.assets.cropper import ImageCropper
from GalleryMan.assets.QtHelpers import PopUpMessage, QCustomButton, Thrower
from PyQt5.QtCore import QParallelAnimationGroup, QPropertyAnimation, QRect
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QVBoxLayout
from GalleryMan.assets.QtImageProcessor import ImageProcessor

class Animation:
    def fade(self, widget , start=1 , end=0):
        self.effect = QGraphicsOpacityEffect()
        
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        
        self.animation.setDuration(200)
        
        self.animation.setStartValue(start)
        
        self.animation.setEndValue(end)
        
        return self.animation

    def unfade(self, widget , start=0 , end=1):
        self.effect = QGraphicsOpacityEffect()
        
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        
        self.animation.setDuration(200)
        
        self.animation.setStartValue(start)
        
        self.animation.setEndValue(end)
        
        return self.animation



class Cropper:    
    def __init__(self , main_window, name , out_wiget , config , callback) -> None:
        self.main_window = main_window
        self.name = name
        self.out_widget = out_wiget
        self.config = config
        self.callback = callback
        self.layout = QHBoxLayout()
        
    def create(self):
        self.buttons_layout = QVBoxLayout()
        
        self.back = QCustomButton(" " , self.main_window).create()
        
        self.buttons_layout.addWidget(self.back)
        
        label = QLabel(self.main_window)
        
        label.setGeometry(QRect(0 , 0 , 1980 , 1080))
                                
        self.crop = ImageCropper(label , self.name , self.out_widget , self.callback)
        
        self.crop.closed.connect(label.hide)
                
        self.crop.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.crop.show()
                                
        self.layout.addWidget(self.crop)
                
        label.setLayout(self.layout)
        
        label.show()
        
        return self.buttons_layout

class PaletteView:
    def __init__(self, main_window, image, out_widget , config , callback) -> None:
        self.processors = ImageProcessor()
        
        self.callback = callback
        
        self.processors.add_image(image)
        
        self.config = config
        
        self.sliderView = QLabel(main_window)
        
        self.unblur = QParallelAnimationGroup()
        
        self.out_widget = out_widget
        
        self.animation = Animation()
        
        self.special_buttons = QHBoxLayout()
        
        self.main_window = main_window

    def create(self):
        lay = QVBoxLayout()

        self.sliderView.setLayout(lay)
        
        i = 0
        
        choose = json.loads(self.config.get("singleFolder" , "filter-icons"))
        
        func = [lambda : self.blur() , lambda : self.sharp() , lambda : self.increaseBrightness(), lambda : self.increaseContrast() , lambda : self.increaseExposure() , lambda : self.callback()]
        
        for icon , color , font_size , family in choose:
            button = QCustomButton(icon , self.main_window).create()
            
            button.setStyleSheet("""
                color: {};
                font-size: {}px;
                font-family: {};
            """.format(color , font_size , family))
            
            button.clicked.connect(func[i])
            
            i += 1
            
            self.unblur.addAnimation(self.animation.unfade(button))
            
            self.special_buttons.addWidget(button)


        self.sliderView.show()

        return self.special_buttons

    def blur(self):
        self.out_widget.setPixmap(QPixmap.fromImage(self.processors.blur()))
        self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")

    def sharp(self):        
        self.out_widget.setPixmap(QPixmap.fromImage(self.processors.sharpen()))
        self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
        
    def increaseBrightness(self):
        self.out_widget.setPixmap(QPixmap.fromImage(self.processors.increaseBrightness()))
        self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
        
    def increaseContrast(self):
        self.out_widget.setPixmap(QPixmap.fromImage(self.processors.increaseContrast()))
        self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
        
    def increaseExposure(self):
        self.out_widget.setPixmap(QPixmap.fromImage(self.processors.increaseExposure()))
        self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")

class FilterView:
    def __init__(self, main_window, image, out_widget , scrollArea ,  icons , callback) -> None:
        self.image = image
        self.scrollArea = scrollArea
        self.original = scrollArea.width()
        self.unblur = QParallelAnimationGroup()
        self.icons = icons
        self.process = 'unlock'
        self.out_widget = out_widget
        self.popup = PopUpMessage()
        self.animation = Animation()
        self.imageProcessor = Filters(Image.open(self.image).convert("RGBA"))
        self.special_buttons = QHBoxLayout()
        self.callback = callback
        self.main_window = main_window

    def create(self):
        # 3. Blur Image
        func = [
            lambda : self.shady(),
            lambda : self.sepia(),
            lambda : self.cherry(),
            lambda : self.underwater(),
            lambda : self.purple(),
            lambda : self.pink(),
            lambda : self.dark(),
            lambda : self.clear(),
            lambda : self.realistic(),
            lambda : self.cool_filter(),
            lambda : self.remove_self()
        ]
                
        i = 0
        
        for icon , icon_color , icon_font_size , icon_font_family , help_msg in self.icons:
            self.button = QCustomButton("{}\n{}".format(icon , help_msg), self.main_window).create()
            
            self.button.setStyleSheet("color: {}; font-family: {}; font-size: {}px;".format(icon_color , icon_font_family , icon_font_size))
            
            # Add the function
            self.button.clicked.connect(func[i])

            # Add the widget
            self.special_buttons.addWidget(self.button)

            self.unblur.addAnimation(self.animation.unfade(self.button))
            
            i += 1

        self.scrollArea.setFixedWidth(1000)
        
        return self.special_buttons
    
    def partial_hide(self):
        return Animation.fade(Animation , self.out_widget , 1 , 0.5)
        
    def partial_unhide(self):
        Animation.unfade(Animation , self.out_widget , 0.5).start()
    
    def shady(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.shady())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
        
    def sepia(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.sepia())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def cherry(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.cherry())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def underwater(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.underwater())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def purple(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.purple())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def pink(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.pink())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def dark(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.dark())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def clear(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.clear())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
        
    def realistic(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.realistic())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
    
    def cool_filter(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.cool())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
        
    def clear_filter(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying is filter")
        
        self.process = 'lock'
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.clear())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/processed_image.png")
            
            self.partial_unhide()
            
            self.process = 'unlock'
        
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
    
    def remove_self(self):
        self.scrollArea.setFixedWidth(self.original)
        
        self.callback()