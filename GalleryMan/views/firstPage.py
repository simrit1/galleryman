import cgitb
from configparser import ConfigParser
cgitb.enable(format = 'text')

# Import All The Required Modules
import json, os
from functools import partial
from GalleryMan.assets.QtHelpers import QContinueButton
from PyQt5.QtCore import (
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QWidget,
)
from GalleryMan.views.folderview import imagesFolder

class QDoublePushButton(QPushButton):
    """A Subclass Of QPushButton, But With A Listener of `Double Click`

    Args:
        parent (QWidget, optional): Parent Widget. Defaults to None.
    """
    doubleClicked = pyqtSignal()
    
    clicked       = pyqtSignal()

    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clicked.emit)
        super().clicked.connect(self.checkDoubleClick)

    @pyqtSlot()
    def checkDoubleClick(self):
        if self.timer.isActive():
            self.doubleClicked.emit()
            self.timer.stop()
        else:
            self.timer.start(250)


class FirstPage:
    """
        Main UI's First And Second Page
        
        # First Page:
        It contains welcome text and a button to move to second page.
        
        # Second Page:
        It asks the user for all the directories that needs to be scanned and stores them at `GalleryMan/data/scan_dirs.txt`
    """
    
    def __init__(self, window: QWidget , application: QMainWindow , scrollArea: QScrollArea , config: ConfigParser) -> None:
        
        self.application = application
        
        self.scrollarea = scrollArea
        
        self.config = config
        
        # Defining All The Variables
        self.original_window_size = 0

        self.window               = window 
        
        # self.window.setMaximumHeight(970)
        
        application.resizeEvent   = self.responser
        
        self.frame                = QLabel()

        self.main_layout          = QHBoxLayout()
        
        self.isdir_open           = False
        
        self.height               = 0
    
        self.scans                = set()
        
        self.frame.setGeometry(QRect(0, 0, 1980, 500))

        self.main_layout.setSpacing(4)
        
    def start(self):
        """Starts Creating The UI

        Args:
            window (QMainWindow): The Main Window In Which The Content Will Be Rendered
        """
        #  ___________________________
        # |                           |
        # |    Main Window Settings   |
        # |___________________________|
        #
        
        # Change Window Name
        self.window.setObjectName("GalleryMan StartUp")
        
        # A Push Button To Go To Next Page
        self.next = QPushButton(self.window)
        
        # GalleryMan Welcome Text
        self.header_text = QLabel(text="Welcome To GalleryMan!", parent=self.window)

        self.header_text.setAlignment(Qt.AlignCenter)
        
        self.header_text.setGeometry(QRect(140, 450, 640, 100))

        # Set The Text
        self.next.setFlat(True)

        self.next.setText("Let's Go  ")

        self.next.setGeometry(QRect(240, 550, 500, 100))

        self.next.setCursor(QCursor(Qt.PointingHandCursor))

        # self.box.addWidget(self.next , alignment=Qt.AlignCenter)

        self.next.setStyleSheet(
            """
            QPushButton{
                color: #88C;
                font-family: "Comfortaa";
                font-size: 40px !important;  
            }
        """
        )

        self.next.clicked.connect(self.go_to_next)

    def go_to_next(self):
        self.dirs = [".."] + sorted(os.listdir(os.path.expanduser("~")))[3:]
        
        self.window.setMinimumHeight(14 * len(self.dirs))
        
        self.isdir_open = True

        self.next.hide()

        self.animations = QParallelAnimationGroup()

        self.effect = QGraphicsOpacityEffect()

        self.header_text.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")

        self.animation.setDuration(500)

        self.animation.setStartValue(1)

        self.animation.setEndValue(0)

        self.animations.addAnimation(self.animation)

        self.animations.start()

        self.animations.finished.connect(self.next_animation)

    def next_animation(self):
        # Second Set
        self.header_text.setText("Choose The Directories Which Should Not Be Scanned")

        self.header_text.setStyleSheet("font-size: 35px")

        self.more_text = QLabel(
            text="(Preventing Directories Which Doesn't Contain Images Makes The App Faster)",
            parent=self.window,
        )

        self.more_text.setGeometry(QRect(550, 100, 1980, 100))

        self.more_text.setStyleSheet("font-size: 20px")

        self.more_text.show()

        self.animations = QParallelAnimationGroup()

        self.effect = QGraphicsOpacityEffect()

        self.header_text.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")

        self.animation.setDuration(500)

        self.animation.setStartValue(0)

        self.animation.setEndValue(1)

        self.animations.addAnimation(self.animation)

        # Second Set
        self.moving = QPropertyAnimation(self.header_text, b"pos")

        self.moving.setDuration(500)

        self.moving.setStartValue(QPoint(0, 80))

        self.moving.setEndValue(QPoint(0, 20))

        self.animations.addAnimation(self.moving)

        self.effect = QGraphicsOpacityEffect()

        self.next.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")

        self.animation.setDuration(200)

        self.animation.setStartValue(1)

        self.animation.setEndValue(0)

        self.animations.addAnimation(self.animation)

        self.animations.start()

        self.directories = QLabel(self.window)
        
        self.directories.setGeometry(QRect(0, 0, 1980, 5000))

        y = 100
        
        # self.window.setMinimumHeight(5000)
        self.window.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )
                
        self.scrollarea.verticalScrollBar().setEnabled(True)
        
        self.scrollarea.verticalScrollBar().show()
    
        for dir in self.dirs:            
            if (dir[0] != "." or dir == "..") and os.path.isdir(os.path.expanduser("~") + '/' + dir):
                name = QDoublePushButton(self.directories)

                name.setCursor(QCursor(Qt.PointingHandCursor))

                name.setFlat(True)

                name.setStyleSheet("font-size: 22px; font-family: SauceCodePro Nerd Font")
                
                name.move(QPoint(0 , y))
                
                if("download" in dir.lower()):
                    text = "  " + dir
                elif("desktop" in dir.lower()):
                    text = "  " + dir
                elif("google" in dir.lower() and "drive" in dir.lower()):
                    text = "  " + dir
                elif("picture" in dir.lower()):
                    text = "  " + dir
                elif(os.path.islink(dir)):
                    text = "  " + dir
                else:
                    text = "  " + dir
                
                name.setText(text)

                name.doubleClicked.connect(
                    partial(self.update_dirs, os.path.expanduser("~") + "/" + dir)
                )
                
                if(dir != ".."):
                    name.clicked.connect(
                        partial(self.select, os.path.expanduser("~") + "/" + dir, name)
                    )
                
                y += 70
                    
        self.continue_to_next = QContinueButton(self.window).start()

        self.continue_to_next.show()

        self.continue_to_next.setStyleSheet(
            "font-size: 20px; background-color: #2E3440;"
        )
        
        self.continue_to_next.move(QPoint(self.window.size().width() + 100, self.window.size().height() + 100))

        self.continue_to_next.setGeometry(QRect(1640, 880, 200, 100))

        self.continue_to_next.clicked.connect(self.transfer_control)

        self.update_sizes(self.window.geometry())
        
        self.directories.show()
        
        # self.layout.addWidget(self.scroll)

    def transfer_control(self):
        with open("GalleryMan/data/scan_dirs.txt", "w") as file:
            file.write(json.dumps(list(self.scans)))

        self.directories.destroy(True, True)

        self.directories.hide()
        
        self.header_text.hide()

        self.continue_to_next.hide()

        self.more_text.hide()
        
        self.scrollarea.verticalScrollBar().setValue(0)

        imagesFolder(self.window , self.application , self.scrollarea , self.config).start(self.header_text)

    def update_dirs(self, directory):
        try:
            self.new_dirs.hide()
        except:
            pass

        self.directories.hide()

        self.new_dirs = QLabel(self.window)

        self.new_dirs.setGeometry(self.directories.geometry())

        y = 100

        for dir in [".."] + os.listdir(directory):
            if not os.path.isdir(directory + "/" + dir) or (
                dir[0] == "." and dir != ".."
            ):
                continue

            name = QDoublePushButton(self.new_dirs)

            name.setCursor(QCursor(Qt.PointingHandCursor))

            name.setFlat(True)

            name.setStyleSheet("font-size: 20px")

            name.setText("   " + dir)

            if os.path.normpath(directory + "/" + dir) in self.scans:
                self.opacity = QGraphicsOpacityEffect()

                self.opacity.setOpacity(0.5)

                name.setGraphicsEffect(self.opacity)

            name.doubleClicked.connect(partial(self.update_dirs, directory + "/" + dir))

            if dir != "..":
                name.clicked.connect(partial(self.select, directory + "/" + dir, name))

            # self.boxLayout.addWidget(name, alignment=Qt.AlignLeft)

            name.move(QPoint(0, y))

            name.show()

            y += 65

        self.new_dirs.show()

    def select(self, directory, label):
        directory = os.path.normpath(directory)

        if directory in self.scans:
            self.effect = QGraphicsOpacityEffect()

            label.setGraphicsEffect(self.effect)

            self.animation = QPropertyAnimation(self.effect, b"opacity")

            self.animation.setDuration(200)

            self.animation.setStartValue(0.5)

            self.animation.setEndValue(1)

            self.animation.start()

            self.scans.remove(directory)

        else:

            self.effect = QGraphicsOpacityEffect()

            label.setGraphicsEffect(self.effect)

            self.animation = QPropertyAnimation(self.effect, b"opacity")

            self.animation.setDuration(200)

            self.animation.setStartValue(1)

            self.animation.setEndValue(0.5)

            self.animation.start()

            self.scans.add(directory)

    def reset(self):
        self.window.style().unpolish(self.window)

        self.window.style().polish(self.window)

        return True

    def responser(self , event):        
        try:
            curr = self.application.geometry()
            
            self.window.setGeometry(curr)

            if (
                curr.size().width() != self.original_window_size
                or curr.size().height() != self.height
            ):
                self.height = curr.size().height()

                self.original_window_size = curr.size().width()

                self.update_sizes(curr.size())

        except:
            
            exit()

    def update_sizes(self, point: QSize):
        width = point.width()

        height = point.height()

        self.header_text.setGeometry(0, (height // 2) - 100, width, 100)

        self.next.setGeometry(QRect(0, height // 2, width, 100))

        if self.isdir_open:
            self.header_text.setGeometry(0, 10, width, 100)

            self.directories.setGeometry((width // 2) - 100, 200, 400 , self.directories.height())
            
            self.more_text.setFixedWidth(width)
            
            self.more_text.move(QPoint(0 , 100))
            
            self.more_text.setAlignment(Qt.AlignCenter)
            
            self.continue_to_next.move(QPoint(self.window.size().width() - 200, self.window.size().height() - 100))

    def update_layout(self, name):
        # self.layout = layout

        label = QLabel()

        label.setFixedHeight(120)

        label.setFixedWidth(220)

        label.setPixmap(QPixmap(name))

        label.setScaledContents(True)

        self.main_layout.addWidget(label)

    def finished(self):
        self.frame.setLayout(self.main_layout)