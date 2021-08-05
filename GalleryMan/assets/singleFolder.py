# Importing all the required modules
from GalleryMan.assets.editorButtonsHelper import QEditorHelper
from math import ceil, inf
from PIL import Image , ExifTags
import functools, gc, json , datetime , pathlib
from configparser import ConfigParser
from random import randint
from GalleryMan.utils.readers import change_with_config, read_file
from GalleryMan.assets.QtHelpers import Animation, PopUpMessage, QCustomButton, Thrower
from PyQt5.QtCore import (
    QAbstractAnimation,
    QObject,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QRunnable,
    QThread,
    QThreadPool,
    QTimer,
    QVariant,
    QVariantAnimation,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import QCursor, QKeySequence, QMouseEvent, QPixmap, QTransform
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCommonStyle,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QShortcut,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import os
from GalleryMan.assets.QEditorButtons import Cropper, FilterView, PaletteView

class FindAll(QObject):
    finished = pyqtSignal()
    
    curr = pyqtSignal(int , str)
    
    request_label = pyqtSignal(str)
    
    label = None

    def run(self , inst , dirs , card_width , card_height , padding , color_mode , colors , x , y):
        done = 0
        
        for i in dirs:     
            self.accepted = False
                        
            i = str(i)
            
            if os.path.isdir(i) or i[-3:] not in [
                "png",
                "svg",
                "jpg",
                "jpeg",
            ]:
                continue
                        
            
            done = done + 1
            
            temp = i[:50] + '...' if len(i) > 50 else i
            
            self.curr.emit(done , temp)
            
            self.request_label.emit(i)
            
            while not self.accepted:
                self.test = True
            

            self.final(inst , i , card_width , card_height , padding , color_mode , colors , x , y)
            
            x += card_width + padding
            
            if x > inst.application.size().width() - 250:
                x = 40

                y += card_height + padding
        
        inst.responser(None)
        
        self.finished.emit()
            
    def final(self , inst , i , card_width , card_height , padding , color_mode , colors , x , y):                       
        MakePixmap().run(i , card_width , card_height , self.label)
                
        if color_mode == "single":
            inst.index = 0
        elif color_mode == "random":
            inst.index = randint(0, len(colors) - 1)
        else:
            inst.index = (inst.index + 1) % len(colors)

        
        self.label.setGeometry(QRect(0, 0, card_width, card_height))
                                
        
        self.label.setCursor(QCursor(Qt.PointingHandCursor))

        self.label.setStyleSheet(
            "border: {}px solid {}".format(
                inst.config.get("singleFolder" , "card-borderWidth"),
                colors[inst.index]
            )
        )

        self.label.clicked.connect(functools.partial(inst.show_image, i))

        self.label.move(QPoint(x, y))

        inst.folders.append(self.label)

class MakePixmap(QObject):    
    finished = pyqtSignal()
        
    def run(self , dir , card_width , card_height , parent):        
        pixmap = QPixmap(dir).scaled(card_width , card_height , transformMode=Qt.SmoothTransformation)
                
        parent.setPixmap(pixmap)
        
        self.finished.emit()
        
class AddToLiked:    
    def __init__(self , parent , dir , remove=False):        
        self.dir = dir
        
        self.remove = remove
    
    def run(self):        
        with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt" , "r") as f:            
            data = f.read()
                                    
            if(data == ""): data = []
            
            else: data = json.loads(data)
            
        with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt" , "w") as f:                       
            if(self.remove):
                data.remove(self.dir)

            else:
                data.append(self.dir)
                         
            f.write(json.dumps(data))
                        
        

class CustomLabel(QLabel):
    clicked = pyqtSignal(QPoint)

    def __init__(self, parent=None , listenFor = Qt.LeftButton):
        super().__init__(parent=parent)
        
        self.listenFor = listenFor

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == self.listenFor:
            self.clicked.emit(event.pos())
            
            self.eventPos = event.pos()


class QRotateLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(QRotateLabel, self).__init__(*args, **kwargs)
        self._pixmap = QPixmap()

        self.curr = 0

        self.initial = 0

        self.init_ani()

    def init_ani(self):
        self._animation = QVariantAnimation(
            self,
            startValue=self.initial,
            endValue=self.curr,
            duration=100,
            valueChanged=self.on_valueChanged,
        )

        self.initial = self.curr

    def set_pixmap(self, pixmap):
        self._pixmap = pixmap
        self.setPixmap(self._pixmap)

    def start_animation(self, deg):
        if self._animation.state() != QAbstractAnimation.Running:
            self.curr, self.initial = deg, self.curr

            self.init_ani()

            self._animation.start()

    def get_curr_deg(self):
        return self.curr % 360

    @pyqtSlot(QVariant)
    def on_valueChanged(self, value):
        t = QTransform()
        t.rotate(value)
        self.setPixmap(self._pixmap.transformed(t))


class singleFolderView():
    def init(
        self,
        window: QWidget,
        directory: str,
        config: ConfigParser,
        scroll: QScrollArea,
        application: QMainWindow,
        app: QApplication,
        *args
    ) -> None:
        self.scaled = json.loads(config.get("singleFolder", "editor-imageScaled"))
        
        self.app = app
        
        self.scroll = scroll
        
        self.scroll.verticalScrollBar().setEnabled(True)

        self.scroll.verticalScrollBar().show()

        self.application = application

        self.window = window
        
        self.original = self.window.geometry()
        
        self.original_responser = self.application.resizeEvent
        
        self.config = config

        self.application.resizeEvent = self.responser

        self.folders = []

        self.args = args

        self.popup = PopUpMessage()

        self.name = QLabel(self.window)

        self.name.setGeometry(self.args[0].geometry())

        self.name.setText(directory[directory.rindex("/") + 1 :])

        self.name.setAlignment(Qt.AlignCenter)

        self.name.show()

        self.name.setStyleSheet(
            "color: {}; font-family: {}; font-size: {}".format(
                self.config.get("singleFolder", "headerText-color"),
                self.config.get("singleFolder", "headerText-fontFamily"),
                self.config.get("singleFolder", "headerText-fontSize") + "px",
            )
        )

        self.directory = directory
        
        self.copy = directory

        stylesheet, self.config = change_with_config(
            read_file("GalleryMan/sass/styles.txt"), section="singleFolder"
        )
        
        self.window.setStyleSheet(stylesheet)
        
        self.start()

    def remove_self(self):
        self.animation = QParallelAnimationGroup()
        
        try:
            self.main_window.hide()
            
            self.central.hide()
        except:
            pass
        
        try:
            self.name.hide()
            
            self.new_label.hide()
        except Exception as e:
            pass
        
        for i in [self.labelArea, self.name, self.go_back]:
            opacity = QGraphicsOpacityEffect()

            try:
                i.setGraphicsEffect(opacity)

                animation = QPropertyAnimation(opacity, b"opacity")

                animation.setStartValue(1)

                animation.setEndValue(0)

                animation.setDuration(200)

                self.animation.addAnimation(animation)

            except:

                pass

        for i in self.args:
            i.show()

            self.animation.addAnimation(
                Animation.fadingAnimation(Animation, i, 200, True)
            )

        self.window.setGeometry(self.original)
        
        self.scroll.setGeometry(self.original)
        
        self.scroll.verticalScrollBar().setValue(0)
        
        self.application.resizeEvent = self.original_responser
        
        self.application.resizeEvent(None)
        
        self.animation.start()

        self.animation.finished.connect(self.remove)

    def remove(self):
        self.labelArea.hide()

        self.animation = self.main_window = self.labelArea = self.name = None

        del self.animation, self.main_window, self.labelArea, self.name

        gc.collect()

    def start(self):
                
        self.go_back = QCustomButton(
            text=self.config.get("singleFolder", "back-buttonText")[1:-1],
            window=self.window,
        ).create()

        self.go_back.setStyleSheet(
            """
            font-size: {}px;
            font-family: {};    
            color: {};                 
        """.format(
                self.config.get("singleFolder", "back-buttonFontSize"),
                self.config.get("singleFolder", "back-buttonFontFamily"),
                self.config.get("singleFolder", "back-buttonColor"),
            )
        )

        self.go_back.setGeometry(
            QRect(
                int(self.config.get("singleFolder", "back-buttonTopPadding")),
                int(self.config.get("singleFolder", "back-buttonLeftPadding")),
                int(self.config.get("singleFolder", "back-buttonWidth")),
                int(self.config.get("singleFolder", "back-buttonHeight")),
            )
        )
        
        self.currDirName = QLabel(self.application)
        
        self.currDirName.setGeometry(self.args[0].geometry())
        
        self.currDirName.setText(self.directory)
        
        self.currDirName.hide()

        self.go_back.setShortcut("Alt+Left")

        self.go_back.clicked.connect(self.remove_self)

        self.go_back.show()

        self.labelArea = QLabel(self.window)
        
        self.labelArea.hide()

        self.labelArea.setGeometry(QRect(0, 150 , 1980, 1080))

        padding = int(self.config.get("singleFolder", "card-padding"))

        card_width = int(self.config.get("singleFolder", "card-width"))

        card_height = int(self.config.get("singleFolder", "card-height"))

        colors = json.loads(self.config.get("singleFolder", "card-color"))

        color_mode = json.loads(self.config.get("singleFolder", "card-mode"))

        self.index = 0

        from pathlib import Path

        self.application.setCursor(Qt.BusyCursor)

        x, y = 40, 100
        
        if(self.copy == "/home/strawhat54/.config/galleryman/data/likedPhotos.txt"):
            with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt" , "r") as file:
                dirs = json.loads(file.read())
        else:
            dirs = Path(self.copy).rglob("*")
            
        self.loader = QLabel(self.application)
        
        self.loader.setGeometry(self.application.geometry())
        
        self.loader.setText("Loaded 0 images \n\n Starting")
        
        self.loader.setStyleSheet("""
            QLabel{
                color: #88C0D0;
                font-family: "SauceCodePro Nerd Font";
                font-size: 30px;
            }                      
            """)
        
        self.loader.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        self.loader.show()
        
        self.thread = QThread(self.application)
        
        self.worker = FindAll()
        
        self.worker.moveToThread(self.thread)
        
        self.worker.curr.connect(self.update)
                
        self.thread.started.connect(functools.partial(self.worker.run , self , dirs , card_width , card_height , padding , color_mode , colors , x , y))
        
        self.worker.request_label.connect(self.sendLabel)
        
        self.worker.finished.connect(self.thread.quit)
        
        self.worker.finished.connect(self.lolcat)
        
        self.thread.start()
                    
        self.responser(None)
        
        self.application.setCursor(Qt.ArrowCursor)

        gc.collect()
    
    def lolcat(self):
        self.loader.setText("   DONE")
        
        self.animations = QParallelAnimationGroup()
        
        self.animations.addAnimation(Animation.fadingAnimation(Animation , self.loader , 200))
        
        self.animations.addAnimation(Animation.fadingAnimation(Animation , self.labelArea , 200 , True))
        
        self.animations.finished.connect(self.labelArea.show)
        
        self.animations.finished.connect(self.loader.hide)
        
        self.animations.finished.connect(functools.partial(self.responser , None))
                
        self.animations.start()
        
    def update(self , num , s):
        self.loader.setText("Loaded {} images \n\n Loading {}".format(num , s))
        
    def sendLabel(self , dir):                
        label = CustomLabel(self.labelArea)
        
        label.clicked.connect(functools.partial(self.show_image , dir))
        
        self.worker.label = label
        
        self.worker.accepted = True
        

    def show_image(self, name , pos):
        self.origin = name

        self.directory_name = name

        """Editor Box

        Args:
            self.directory_name (str): The file location
        """

        #  ___________________________
        # |                           |
        # | Center Pixmap Adjustments |
        # |___________________________|
        #

        # Center Area (Main)
        self.main_window = QLabel(self.application)

        # Set Geometry
        self.main_window.setGeometry(QRect(0, 100, 1980, 1000))

        # QLabel for image
        self.image = QRotateLabel(self.main_window)

        self.dimension = json.loads(
            self.config.get("singleFolder", "editor-imagePadding")
        )

        self.geometry = [
            *self.dimension[:2],
            self.application.size().width() - self.dimension[0] - self.dimension[2],
            self.application.size().height() - self.dimension[1] - self.dimension[3],
        ]

        # Set The Geometry
        self.image.setGeometry(QRect(*self.geometry))

        self.image.setStyleSheet("background-color: transparent")

        # Set The Pixmap
        os.system('cp "{}" GalleryMan/assets/processed_image.png'.format(self.directory_name))

        self.pixmap = QPixmap("GalleryMan/assets/processed_image.png")

        self.image.set_pixmap(self.pixmap)

        # Again, Scaled Contents are cool :)
        self.image.setScaledContents(self.scaled)

        self.central = QLabel(self.application)

        self.central.setGeometry(QRect(450, 850, 1010, 140))

        self.central.show()

        layout = QVBoxLayout(self.central)

        self.scrollArea = QScrollArea(self.central)

        layout.addWidget(self.scrollArea)

        self.buttons = QWidget(self.main_window)

        self.buttons.setGeometry(QRect(0, 850, 900, 100))

        self.scrollArea.setWidget(self.buttons)

        second_layout = QHBoxLayout(self.buttons)

        self.buttons.setLayout(second_layout)

        # Set fixed spacing between the elements
        second_layout.setSpacing(1)

        #  ___________________________
        # |                           |
        # |    Editor Buttons         |
        # |___________________________|
        #

        self.icons = json.loads(self.config.get("singleFolder", "editorButtons-icons"))

        i = 0
        
        self.functional = QEditorHelper(self.app , self.application , self.central , self.config , self.scrollArea , self.image)

        functions = [
            lambda : self.functional.copyToClipboard(self.origin),
            lambda : self.functional.showEditButtons(self.origin),
            lambda : self.functional.addtoLiked(self.directory_name , self),
            lambda : self.functional.moveToThrash(self.origin),
            lambda : self.functional.moreInfo(self.directory_name),
        ]
        
        self.heartWidget = 2
        
        with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt") as file:
            dirs = json.loads(file.read())

        # 3. Crop Image
        for icon, icon_color, icon_font_size, icon_family in self.icons:

            item = QCustomButton(icon, self.application, True).create()
            
            item.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    icon_color, icon_font_size, icon_family
                )
            )

            item.clicked.connect(functions[i])

            i += 1

            second_layout.addWidget(item)
            
            if(type(self.heartWidget) == QPushButton):
                item.setStyleSheet(
                    "color: {}; font-size: {}px; font-family: {}".format(
                        "#BF616A", icon_font_size, icon_family
                    )
                )
            
            else:
                
                if(self.heartWidget == 0):
                    self.heartWidget = item
                    
                    self.iconStyles = [icon_color , icon_font_size , icon_family]
                
                else:
                    
                    self.heartWidget -= 1
                    

        self.directory_name = "GalleryMan/assets/processed_image.png"

        del icon, icon_color, icon_family, icon_font_size, self.pixmap

        self.new_layout = second_layout
                
        gc.collect()

        self.main_window.show()

        self.responser(None)
        
    def show_info(self, dir):        
        info = QLabel(self.main_window)
        
        info.setGeometry(self.image.geometry())
                
        layout = QVBoxLayout()
        
        path = QLabel(text=f'Path: {dir}')
        
        path.setStyleSheet("background-color: transparent; color: #D8DEE9; font-size: 23px")

        path.setAlignment(Qt.AlignCenter)
        
        name = dir[dir.rindex('/') + 1:]
        
        layout.addWidget(path)
        
        path = QLabel(text=f'File Name: {name}')
        
        path.setStyleSheet("background-color: transparent; color: #D8DEE9; font-size: 23px")

        path.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(path)
        
        reso = list(Image.open(dir).size)
        
        path = QLabel(text=f'Resolution: {reso[0]} * {reso[1]}')
        
        path.setStyleSheet("background-color: transparent; color: #D8DEE9; font-size: 23px")

        path.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(path)
        
        size = os.path.getsize(dir)
        
        path = QLabel(text=f"Size: {size} bytes ({round(size / 1e+6 , 2)} MB)")
        
        path.setStyleSheet("background-color: transparent; color: #D8DEE9; font-size: 23px")

        path.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(path)
        
        info.setLayout(layout)
        
        rgb = tuple([int("2E3440"[i : i + 2], 16) for i in (0, 2, 4)] + [0.7])
        
        info.setStyleSheet(f"background-color: rgba{rgb}")
        
        self.animation = Animation.fadingAnimation(Animation , info , 200 , True)
        
        self.animation.start()
        
        self.animation.finished.connect(info.show)
        
        self.cross = QCustomButton("" , info).create()
        
        self.cross.setStyleSheet('color: #D8DEE9; background-color: transparent; font-size: 27px')
                
        self.cross.clicked.connect(info.hide)
        
        self.cross.setGeometry(QRect(
            (95 / 100) * info.width(),
            (92 / 100) * info.height(),
            (5 / 100) * info.width(),
            (5 / 100) * info.height(), 
        ))
        
        self.cross.show()
    
    def rename(self , dir):
        self.test = QLineEdit(self.application)
        
        self.test.setGeometry(QRect(
            (self.application.width() // 2) - 400,
            (self.application.height() // 2) - 25,
            800,
            50
        ))
                
        self.test.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
                                
        self.test.setStyleSheet("color: #D8DEE9; font-size: 25px; border: 1px solid #3B4252; font-family: 'Comfortaa'; padding-left: 10px")
        
        self.test.setText("New file name...")
        
        self.keybordShort = QShortcut(QKeySequence("Return"), self.application)
        
        self.escape = QShortcut(QKeySequence("Esc") , self.application)
        
        self.escape.activated.connect(self.test.hide)
        
        self.escape.activated.connect(lambda: self.escape.setKey(QKeySequence()))
        
        
        
        self.keybordShort.activated.connect(lambda : self.fileRename(dir))
                
        self.animation = Animation.fadingAnimation(Animation , self.test , 200 , True)
        
        self.animation.finished.connect(self.test.show)
        
        self.animation.start()
    
    def fileRename(self , file):
        text = self.test.text().replace('\n' , '')
        
        self.test.setText(text)
        
        try:
            filename , extension = text[:text.rindex('.')] , text[text.rindex('.') + 1:]
            
            text = file[:file.rindex('/')] + '/' + filename
            
            path = os.path.join(file[:file.rindex('/')], filename) + '.' + extension
            
            Image.open(file).convert("RGB").save("GalleryMan/assets/temp." + extension , quality=90)
            
            os.replace("GalleryMan/assets/temp." + extension , path)
            
            self.animation = Animation.fadingAnimation(Animation , self.test , 200)
            
            self.animation.start()
            
            self.animation.finished.connect(self.test.hide)
            
            self.keybordShort.setKey(QKeySequence())
            
            self.popup.new_msg(self.application , "Image renamed" , 200)
            
        except:
            
            self.popup.new_msg(self.application , "Invalid File Extension" , 200)
            
        
        
    def addToLiked(self):
        with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt") as file:
            dirs = json.loads(file.read())
                    
        if(self.origin in dirs):
            AddToLiked(self.application , self.origin , True).run()
            
            self.popup.new_msg(self.application , "Image Removed From Liked Images" , 400)
            
            self.heartWidget.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    self.icons[0][1] , self.icons[0][2], self.icons[0][3]
                )
            )
            
            
        else:
            
            AddToLiked(self.application , self.origin).run()
                    
            self.popup.new_msg(self.application , "Image Added To Liked Images" , 400)
            
            self.heartWidget.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    "#BF616A", self.icons[0][2], self.icons[0][3]
                )
            )
            
            self.application.style().unpolish(self.application)

            self.application.style().polish(self.application)

            self.application.update()
            
            Thrower(self.central.pos().x() + self.heartWidget.pos().x() + 13, self.central.pos().y() - self.heartWidget.pos().y() - 10, self.application).throw()
            
        

    def save_edited(self, dir):
        parent = dir[: dir.rindex("/")]

        name = dir[dir.rindex("/") + 1 : -4] + "_edited.png"

        os.system(
            "mv GalleryMan/assets/processed_image.png  {}".format(
                "{}/{}".format(parent, name)
            )
        )

        self.popup.new_msg(self.application, "Image saved as {}".format(name), 200)

        parent = name = None

        del parent, name

        self.closeEditor()

        gc.collect()

    def closeEditor(self):
        self.animatui = QParallelAnimationGroup()

        self.animatui.addAnimation(
            Animation.fadingAnimation(Animation, self.main_window, 250)
        )

        self.animatui.addAnimation(
            Animation.fadingAnimation(Animation, self.buttons, 250)
        )

        try:
            self.animatui.addAnimation(
                Animation.fadingAnimation(Animation, self.central, 250)
            )
        except:
            pass

        def callback():
            self.main_window.hide()

            try:
                self.central.hide()
            except:
                pass

        self.animatui.start()

        self.animatui.finished.connect(callback)

    def rotate_image(self):
        self.image.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.new_label = QWidget(self.application)

        width = int(self.config.get("singleFolder", "slider-width"))

        input_width = int(self.config.get("singleFolder", "input-width"))

        padding = int(self.config.get("singleFolder", "item-padding"))

        self.new_label.setGeometry(
            QRect(
                int(self.config.get("singleFolder", "item-leftPadding")),
                310,
                width + padding + input_width + padding,
                100,
            )
        )

        self.scrollArea.takeWidget()

        self.scrollArea.setWidget(self.new_label)

        self.new_label.setStyleSheet("background-color: transparent;")

        self.layout = QHBoxLayout()

        self.layout.setSpacing(padding)

        self.slider = QSlider(Qt.Horizontal)

        self.slider.setMaximum(360)

        self.slider.setMinimum(0)

        self.slider.setFixedSize(
            width,
            int(self.config.get("singleFolder", "slider-height")),
        )

        self.slider.setStyleSheet(
            """
            QSlider::groove:horizontal{{
                background-color: {};
                border-radius: {}px; 
                border: {}px solid {}     
            }}
            QSlider::handle:horizontal{{
                width: {}px;
                height: {}px;
                color: {};
                border-radius: {}px;
                border: {}px solid {};
            }}
            """.format(
                self.config.get("singleFolder", "slider-backgroundColor"),
                self.config.get("singleFolder", "slider-borderRadius"),
                self.config.get("singleFolder", "slider-borderWidth"),
                self.config.get("singleFolder", "slider-borderColor"),
                self.config.get("singleFolder", "slider-holderWidth"),
                self.config.get("singleFolder", "slider-holderHeight"),
                self.config.get("singleFolder", "slider-holderColor"),
                self.config.get("singleFolder", "slider-holderRadius"),
                self.config.get("singleFolder", "slider-holderBorderWidth"),
                self.config.get("singleFolder", "slider-holderColor"),
            )
        )
        
        self.slider.valueChanged.connect(lambda : self.show(self.slider.value()))

        self.textBox = QLineEdit()

        self.textBox.setPlaceholderText("Image Degree")

        self.textBox.setStyleSheet(
            """
            width: {}px;
            height: {}px;
            background-color: {};
            font-size: {}px;
            font-family: {};
            color: {};
            border-radius: {}px;
            border: {}px solid {};                           
        """.format(
                input_width,
                self.config.get("singleFolder", "input-height"),
                self.config.get("singleFolder", "input-backgroundColor"),
                self.config.get("singleFolder", "input-fontSize"),
                self.config.get("singleFolder", "input-fontFamily"),
                self.config.get("singleFolder", "input-textColor"),
                self.config.get("singleFolder", "input-borderRadius"),
                self.config.get("singleFolder", "input-borderWidth"),
                self.config.get("singleFolder", "input-borderColor"),
            )
        )

        self.textBox.textChanged.connect(self.update_text)

        self.layout.addWidget(self.slider)

        self.new_label.setLayout(self.layout)

        self.layout.addWidget(self.textBox)

        self.popup.new_msg(self.application, "Press Enter To Rotate The Image", 200)

        self.shortcut = QShortcut(QKeySequence("Return"), self.application)

        self.shortcut.activated.connect(self.removecropper)

        del self.new_label, width, input_width, padding

        gc.collect()

    def removecropper(self):
        self.shortcut.setKey(QKeySequence())

        value = -int(self.textBox.text())
                
        image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")
        
        image = image.rotate(value , expand=1 , fillcolor=(255, 0, 0, 0))
                    
        image.save("GalleryMan/assets/processed_image.png")

        self.parallel = QParallelAnimationGroup()

        anim = Animation.fadingAnimation(Animation, self.buttons, 400, True)

        self.parallel.addAnimation(anim)

        self.parallel.start()

        self.image.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.parallel.finished.connect(self.switch_to_home)

    def switch_to_home(self):
        self.scrollArea.takeWidget()
        
        self.scrollArea.setWidget(self.buttons)

    def update_text(self):
        curr = self.textBox.text()

        try:
            curr = int(curr)
        except:

            return

        self.slider.setValue(int(curr))

        self.image.start_animation(curr)

    def show(self, deg):
        self.image.start_animation(deg)

        self.textBox.setText(str(deg))

    def switch_to_cropper(self, name):
        try:

            self.main_window.hide()
        except:

            pass

        self.cropper = Cropper(
            self , self.application, name, self.image, self.config, self.callback_2
        )
        
        self.cropper.create()
        
    

    def callback_2(self):
        self.window.setCursor(QCursor(Qt.ArrowCursor))

        try:         
            self.main_window.show()
        except:
            pass

        self.image.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))

    def switch_to_filters(self, name):
        self.new_label = QWidget(self.application)

        self.new_label.setGeometry(QRect(0, 850, 3000, 100))
        
        self.scrollArea.takeWidget()

        self.scrollArea.setWidget(self.new_label)

        # self.new_label.setStyleSheet("background-color: transparent;")

        buttons = FilterView(
            self.application,
            self.window,
            name,
            self.image,
            self.new_label,
            json.loads(self.config.get("singleFolder", "filters-colorIcons")),
            self.callback,
        ).create()

        self.new_label.setLayout(buttons)

        self.responser(None)

    def switch_to_palette(self, name):
        self.new_label = QWidget(self.application)

        self.scrollArea.takeWidget()

        self.scrollArea.setWidget(self.new_label)

        self.new_label.setGeometry(self.buttons.geometry())

        self.new_label.setStyleSheet("background-color: transparent")

        buttons = PaletteView(
            self.application, name, self.image, self.config, self.callback
        ).create()

        self.new_label.setLayout(buttons)

    def callback(self):
        def finish():
            self.scrollArea.takeWidget()

            self.scrollArea.setWidget(self.buttons)

        self.ani = QParallelAnimationGroup()

        self.ani.addAnimation(Animation.fadingAnimation(Animation, self.new_label, 200))

        self.ani.addAnimation(
            Animation.fadingAnimation(Animation, self.buttons, 200, True)
        )

        self.ani.start()

        self.ani.finished.connect(finish)

    def responser(self, _):        
        self.width = self.application.size().width()

        card_width = int(self.config.get("singleFolder", "card-width"))

        card_height = int(self.config.get("singleFolder", "card-height"))

        card_padding = int(self.config.get("singleFolder", "card-padding"))

        x, y = 40, 100

        self.animations = QParallelAnimationGroup()

        for i in self.folders:
            ani = QPropertyAnimation(i, b"pos")

            ani.setStartValue(i.pos())

            ani.setEndValue(QPoint(x, y))

            ani.setDuration(100)

            x += card_width + card_padding

            self.animations.addAnimation(ani)

            if x > self.width - card_width:
                x = 40

                y += card_height + card_padding

        self.perline = max((self.width - card_width) // card_width , 1)

        try:
            self.new_width = (50 / 100) * self.width

            self.central.setGeometry(
                QRect(
                    self.new_width // 2,
                    self.central.y(),
                    self.new_width,
                    self.central.height(),
                )
            )

        except:
            pass
        
        try:
            self.cropper.updateSize(self.application.size())
        except:
            pass
        
        try:
            self.new_width = (50 / 100) * self.width

            self.new_label.setGeometry(
                QRect(
                    self.new_width // 2,
                    self.new_label.y(),
                    self.new_width,
                    self.new_label.height(),
                )
            )

            self.scrollArea.show()
        except:

            pass

        self.height = 300 + (card_height + card_padding) * (ceil(len(self.folders) / self.perline))

        self.window.setFixedHeight(self.height)
        
        try:
            self.labelArea.setFixedHeight(self.height)
        except:
            pass    
        
        try:
            self.geometry = [
                *self.dimension[:2],
                self.application.size().width() - self.dimension[0] - self.dimension[2],
                self.application.size().height()
                - self.dimension[1]
                - self.dimension[3],
            ]

            # Set The Geometry
            self.image.setGeometry(QRect(*self.geometry))

        except:

            pass
        
        self.name.setFixedWidth(self.width)

        self.name.setAlignment(Qt.AlignCenter)

        self.animations.start()

    def get_first(self, dir: str) -> str:
        """Returns the first image in the folder, or None if no image is available

        Args:
            dir (str): [description]

        Returns:
            str: [description]
        """

        # Iterate through all the files and folders in the directory
        for i in os.listdir(dir):

            # Check if the image is a supported one
            if i[i.rindex('.'):] in ["png", "jpeg", "jpg", "webp"] and not os.path.isdir(
                "{}/{}".format(dir, i)
            ):
                return "{}/{}".format(dir, i)

        return None
