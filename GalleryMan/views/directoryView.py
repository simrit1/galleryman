from functools import partial
import json
import os
from os import listdir
from PyQt5.QtCore import QPoint, QPropertyAnimation, QRect, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCursor
from PyQt5 import Qt
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QLabel, QPushButton, QVBoxLayout
from GalleryMan.assets.QtHelpers import QCustomButton

class QDoublePushButton(QPushButton):
    doubleClicked = pyqtSignal()
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
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


class DirectoryView:
    def __init__(self , files) -> None:

        self.files = files

        self.ori = 0

        self.scans = []

    def start(self, window):
        """Starts Creating The UI

        Args:
            window (QMainWindow): The Main Window In Which The Content Will Be Rendered
        """
        #  ___________________________
        # |                           |
        # |    Main Window Settings   |
        # |___________________________|
        #
        self.window = window

        self.next = QLabel(self.window)

        self.directory_list = QLabel(self.window)

        self.directory_list.setGeometry(QRect(600, 260, 500, 700))

        self.header_text = QLabel(self.window)

        self.layout = QVBoxLayout()

        self.layout.setSpacing(20)

        self.directory_list.setLayout(self.layout)
        
        self.window.resizeEvent = self.reponser
        
        #  Set The Name
        self.window.setObjectName("GalleryMan StartUp")

        # Set The Geomtery
        self.header_text.setGeometry(0, 140, 900, 500)

        self.header_text.setMinimumWidth(100)

        # Center Alignment Looks Cool, Doesn't It?
        self.header_text.setAlignment(Qt.AlignCenter)

        # Set The Text
        self.header_text.setText("Your Directories")

        self.next.setText("Choose The Directory Which Will Be Scanned")

        self.next.setAlignment(Qt.AlignCenter)

        self.next.show()

        self.next.setStyleSheet(
            """
                QLabel{
                    font-family: "Comfortaa";
                    font-size: 26px !important;  
                }
        """
        )

        for root in listdir(os.path.expanduser('~')):
            for dir in [".."] + os.listdir(root):
                icon = "   "

                if dir[0] != "." or dir == "..":
                    label = QDoublePushButton()

                    label.setStyleSheet("font-size: 20px")

                    label.setFlat(True)

                    label.setCursor(QCursor(Qt.PointingHandCursor))
                    
                    if os.path.isdir(os.path.expanduser("~") + "/" + dir) :
                        if dir != "..":
                            label.setText(icon + dir + self.count_images(os.path.expanduser("~") + "/" + dir))

                            label.clicked.connect(partial(self.add, os.path.expanduser("~") + "/" + dir, label))

                        label.doubleClicked.connect(
                            partial(
                                self.updateList, os.path.expanduser("~") + "/" + dir
                            )
                        )
                        
                        self.layout.addWidget(label)

            break
        
        self.continue_button = QCustomButton("Continue  " , self.window).create()
        
        self.continue_button.setFixedWidth(200)
                
        self.continue_button.move(QPoint(1600 , 900))
        
        self.continue_button.setStyleSheet('font-size: 20px')
        
        self.continue_button.clicked.connect(self.continue_forward)
        
    def count_images(self , path):
        count = 0

        for i in os.listdir(path):
            if(i[-3:] in ['png' , 'jpg' , 'jpeg']):
                count += 1
        
        return " [ {} images]".format(count)
        
    def continue_forward(self):
        with open('/home/strawhat54/.config/galleryman/data/scan_dirs.txt' , 'w') as f:
            f.write(json.dumps(self.scans))

    def add(self, dir, label: QPushButton):        
        if dir not in self.scans:
            self.effect = QGraphicsOpacityEffect()
            
            label.setGraphicsEffect(self.effect)

            self.animation = QPropertyAnimation(self.effect, b"opacity")
            
            self.animation.setDuration(200)
            
            self.animation.setStartValue(1)
            
            self.animation.setEndValue(0.5)
            
            self.animation.start()
            
            self.scans.append(os.path.normpath(dir))
        
        else:
            self.scans.remove(os.path.normpath(dir))
            
            self.effect = QGraphicsOpacityEffect()
            
            label.setGraphicsEffect(self.effect)

            self.animation = QPropertyAnimation(self.effect, b"opacity")
            
            self.animation.setDuration(300)
            
            self.animation.setStartValue(0.5)
            
            self.animation.setEndValue(1)
            
            self.animation.start()

    def updateList(self, directory):
        try:
            self.new_label.hide()
        except:
            pass

        self.directory_list.hide()

        self.new_label = QLabel(self.window)

        self.new_label.setGeometry(QRect(600, 260, 500, 700))

        self.header_text = QLabel(self.window)

        self.layout = QVBoxLayout()

        self.new_label.setLayout(self.layout)

        count = 0

        for dir in [".."] + os.listdir(directory):
            count += 1
            if dir[0] != "." or dir == "..":
                label = QDoublePushButton()

                label.setStyleSheet("font-size: 20px")

                label.setCursor(QCursor(Qt.PointingHandCursor))

                label.setFlat(True)

                if os.path.isdir(directory + "/" + dir):
                    label.setText("   " + dir + self.count_images(directory + "/" + dir))

                    if ".." not in dir:
                        label.clicked.connect(partial(self.add, directory + '/' + dir , label))

                    label.doubleClicked.connect(
                        partial(self.updateList, directory + "/" + dir)
                    )
                    self.layout.addWidget(label)
                                        
                    if(os.path.expanduser("~") + "/" + dir in self.scans):
                        self.opacity = QGraphicsOpacityEffect()
                        
                        self.opacity.setOpacity(0.5)
                        
                        label.setGraphicsEffect(self.opacity)
                        
        self.directory_list.setFixedHeight(10 * count)

        self.new_label.show()

    def reponser(self):
        while 1: 
            curr = self.window.geometry()

            if curr.size().width() != self.ori:
                self.ori = curr.size().width()

                self.update_sizes(self.ori)

    def update_sizes(self, width):
        self.header_text.setGeometry(0, 0, width, 100)

        self.next.setGeometry(QRect(0, 80, width, 100))
