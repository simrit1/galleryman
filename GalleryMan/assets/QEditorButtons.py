from PIL import Image , ImageQt
from GalleryMan.themes.filters import Filters
import json
from GalleryMan.assets.cropper import ImageCropper
from GalleryMan.assets.QtHelpers import PopUpMessage, QCustomButton
from PyQt5.QtCore import QParallelAnimationGroup, QPropertyAnimation, QRect, Qt
from PyQt5.QtGui import QCursor, QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from GalleryMan.assets.QtImageProcessor import ImageProcessor
import os

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
    def __init__(self , inst, main_window, name , out_wiget , config , callback) -> None:
        self.main_window = main_window
        self.name = name
        self.out_widget = out_wiget
        self.config = config
        self.inst = inst
        self.callback = callback
        self.layout = QHBoxLayout()
        
    def create(self):
        self.buttons_layout = QVBoxLayout()
        
        self.back = QCustomButton(" " , self.main_window).create()
        
        self.buttons_layout.addWidget(self.back)
        
        label = QLabel(self.main_window)
        
        label.setGeometry(QRect(0 , 0 , 1980 , 1080))
                                
        self.crop = ImageCropper(self.inst , label , self.name , self.out_widget , self.callback)

        self.crop.closed.connect(label.hide)
                            
        self.crop.show()
                                
        self.layout.addWidget(self.crop)
                
        label.setLayout(self.layout)
        
        label.show()
        
        return self.buttons_layout
    
    def updateSize(self , size):
        self.crop.resizeItem(size)

class PaletteView:
    def __init__(self, main_window, image, out_widget , config , callback) -> None:
        self.processors = ImageProcessor()
        
        self.callback = callback
        
        self.edited = False
        
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
        
        func = [lambda : self.blur() , lambda : self.sharp() , lambda : self.increaseBrightness(), lambda : self.increaseContrast() , lambda : self.increaseExposure() , lambda : self.remove()]
        
        for icon , color , font_size , family in choose:
            button = QCustomButton(text=icon , window=None).create()
            
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
        self.edited = True

        def callback():
            self.out_widget.set_pixmap(self.createPixmap(self.processors.blur()))
                    
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")

            Animation.unfade(Animation , self.out_widget , 0.5).start()

        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)

        self.animations.finished.connect(callback)

        self.animations.start()

    def sharp(self):        
        self.edited = True

        def callback():
            self.out_widget.set_pixmap(self.createPixmap(self.processors.sharpen()))
                    
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")

            Animation.unfade(Animation , self.out_widget , 0.5).start()

        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)

        self.animations.finished.connect(callback)

        self.animations.start()
        
    def increaseBrightness(self):
        self.edited = True

        def callback():
            self.out_widget.set_pixmap(self.createPixmap(self.processors.increaseBrightness()))
                    
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")

            Animation.unfade(Animation , self.out_widget , 0.5).start()

        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)

        self.animations.finished.connect(callback)

        self.animations.start()
        
    def increaseContrast(self):
        self.edited = True

        def callback():
            self.out_widget.set_pixmap(self.createPixmap(self.processors.increaseContrast()))
                    
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")

            Animation.unfade(Animation , self.out_widget , 0.5).start()

        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)

        self.animations.finished.connect(callback)

        self.animations.start()
        
    def increaseExposure(self):
        self.edited = True

        def callback():
            self.out_widget.set_pixmap(self.createPixmap(self.processors.increaseExposure()))
                    
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")

            Animation.unfade(Animation , self.out_widget , 0.5).start()

        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)

        self.animations.finished.connect(callback)

        self.animations.start()
    
    def remove(self):
        self.dialog = QDialog()
        
        if(self.edited):
            FilterView.show_dialog(FilterView , self.dialog , self.main_window , [self.useUpdate , self.removeUpdated])
        else:
            self.removeUpdated()
            
    def useUpdate(self):
        os.system("mv GalleryMan/assets/current_edited.png GalleryMan/assets/processed_image.png")
        
        self.removeUpdated()
        
    def removeUpdated(self):
        if(os.path.isfile("GalleryMan/assets/current_edited.png")):
            os.remove("GalleryMan/assets/current_edited.png")
        
        self.out_widget.setPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
                    
        self.dialog.hide()
        
        self.callback()
        
    def createPixmap(self , image: Image):
        if image.mode == "RGB":
            r, g, b = image.split()
            image = Image.merge("RGB", (b, g, r))
            
        elif  image.mode == "RGBA":
            r, g, b, a = image.split()
            image = Image.merge("RGBA", (b, g, r, a))
            
        elif image.mode == "L":
            image = image.convert("RGBA")

        im2 = image.convert("RGBA")
        
        data = im2.tobytes("raw", "RGBA")
        
        qim = QImage(data, image.size[0], image.size[1], QImage.Format_ARGB32)
        
        pixmap = QPixmap.fromImage(qim)
        
        return pixmap

class FilterView:
    def __init__(self, main_window, out_widget , scrollArea ,  icons , callback) -> None:
        self.original = scrollArea.width()
        self.scrollArea = scrollArea
        self.unblur = QParallelAnimationGroup()
        self.icons = icons
        self.out_widget = out_widget
        self.popup = PopUpMessage()
        self.animation = Animation()
        self.imageProcessor = Filters(Image.open("GalleryMan/assets/processed_image.png").convert("RGBA"))
        self.special_buttons = QHBoxLayout()
        self.callback = callback
        self.edited = False
        self.main_window = main_window
    
    def partial_hide(self):
        return Animation.fade(Animation , self.out_widget , 1 , 0.5)
        
    def partial_unhide(self):
        Animation.unfade(Animation , self.out_widget , 0.5).start()
    
    def shady(self):
        self.edited = True
            
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.shady())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
        
    def sepia(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.sepia())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def cherry(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.cherry())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def underwater(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.underwater())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def purple(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.purple())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def pink(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.pink())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def dark(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.dark())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)

    def clear(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.clear())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
        
    def realistic(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.realistic())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
    
    def cool_filter(self):
        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.cool())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
        
    def clear_filter(self):
        if(self.process == 'lock'):
            self.popup.new_msg("Wait while applying a filter")

        self.edited = True
        
        def callback():
            self.image = ImageQt.ImageQt(self.imageProcessor.clear())
                
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save("GalleryMan/assets/current_edited.png")
            
            self.partial_unhide()
                
        self.animation = self.partial_hide()
        
        self.animation.start()
        
        self.animation.finished.connect(callback)
        
    def show_dialog(self , dialog: QDialog , parent , functions):
        # self.dialog = QDialog(parent)
        self.dialog = dialog
        
        self.dialog.setParent(parent)
        
        layout = QVBoxLayout()
        
        label = QLabel(text="Do you want to apply the viewed filter?")
        
        label.setAlignment(Qt.AlignCenter)
        
        label.setStyleSheet("""
            QLabel{
                font-size: 20px;
                color: #D8DEE9;
                font-family: "SauceCodePro Nerd Font"
            }                    
        """)
        
        layout.addWidget(label)
        
        self.dialog.setFixedWidth(700)
        
        self.dialog.setFixedHeight(120)
                        
        self.buttons = QDialogButtonBox()
                        
        # Buttons
        for text , func in zip([" Continue Changes" , " Discard Changes"] , functions):            
            button = QPushButton()
                        
            button.clicked.connect(func)          
            
            button.setText(text)
            
            self.buttons.addButton(button , QDialogButtonBox.ActionRole)
            
            button.setFlat(True)
                        
            button.setCursor(QCursor(Qt.PointingHandCursor)) 
                                           
            button.setStyleSheet('font-size: 20px; color: #D8DEE9')
            
        layout.addWidget(self.buttons)
        
        self.dialog.setLayout(layout)
        
        self.dialog.exec_()
        
        return self.dialog
    
    def remove_self(self):
        
        if(self.edited):
            self.show_dialog(QDialog() , self.main_window , [self.useUpdate , self.removeUpdated])
        else:
            self.scrollArea.setFixedWidth(self.original)
            
            self.callback()
            
    def useUpdate(self):
        self.dialog.hide()
        
        self.callback()
                
        os.system("cp GalleryMan/assets/current_edited.png GalleryMan/assets/processed_image.png")
        
        self.out_widget.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
    def removeUpdated(self):
        self.dialog.hide()
        
        self.out_widget.setPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.callback()
        
        os.system("rm -rf GalleryMan/assets/current_edited.png")

class Beautify:
    def __init__(self) -> None:
        pass
    
    def beautify(self):
        pass