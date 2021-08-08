from functools import partial
from PyQt5 import QtCore
from PyQt5.QtCore import QParallelAnimationGroup, QPoint, QPropertyAnimation, QRect, QSize, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsEffect, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QLayout, QPushButton, QScrollArea, QVBoxLayout, QWidget

class QtCrossButton:
    def __init__(self, window) -> None:
        self.window = window

    def button(self) -> QPushButton:
        pushbutton = QPushButton(self.window)

        pushbutton.setText("  ")

        pushbutton.setFlat(True)

        pushbutton.setCursor(QCursor(Qt.PointingHandCursor))

        pushbutton.setShortcut("Esc")

        return pushbutton


class QLikeButton:
    """
    Creates A Heart Button With A Heart Throwing Effect!
    """

    def __init__(self, location, window: QLabel) -> None:
        self.location = location
        self.window = window

    def start(self):

        likeButton = QPushButton(parent=self.window)

        likeButton.setText("  ")

        likeButton.setIconSize(QtCore.QSize(50, 50))

        likeButton.setProperty("class", "like")

        likeButton.setCursor(QCursor(Qt.PointingHandCursor))

        likeButton.setFlat(True)

        return likeButton


class QToolPushButton:
    def __init__(self, window) -> None:
        self.window = window

    def create(self):
        button = QPushButton(self.window)

        button.setText("")

        button.move(QPoint(400, 850))

        button.setFlat(True)

        button.setCursor(QCursor(Qt.PointingHandCursor))

        return button


class Exposure:
    def __init__(self, window) -> None:
        self.window = window

    def create(self):
        button = QPushButton(self.window)

        button.setText("+")

        button.move(QPoint(600, 850))

        button.setFlat(True)

        button.setCursor(QCursor(Qt.PointingHandCursor))

        return button


class Thrower:
    def __init__(self, x, y, window) -> None:
        self.x = x - 10
        self.y = y
        self.window = window

    def fade(self, widget):
        self.effect = QGraphicsOpacityEffect()

        widget.setGraphicsEffect(self.effect)

        self.animation = QtCore.QPropertyAnimation(self.effect, b"opacity")

        self.animation.setDuration(500)

        self.animation.setStartValue(1)

        self.animation.setEndValue(0)

        return self.animation

    def throw(self):

        animations = QParallelAnimationGroup()

        self.labels = []

        self.blurs = QParallelAnimationGroup()
        
        for left, right in zip(
            [self.x - 40, self.x + 40, self.x ],
            [self.y - 65, self.y - 65, self.y + 35],
        ):
            label = QLabel(self.window)

            label.setText("  ")
            
            label.setStyleSheet("background-color: transparent; font-family: SauceCodePro Nerd Font; color: #BF616A")
            
            label.setFixedHeight(200)

            animation = QPropertyAnimation(label, b"pos")

            animation.setStartValue(QPoint(self.x, self.y))

            animation.setEndValue(QPoint(left, right))

            animation.setDuration(500)

            animations.addAnimation(animation)

            blur_animation = self.fade(label)

            self.blurs.addAnimation(blur_animation)

            label.show()

            self.labels.append(label)

        q = QPushButton(self.window)

        q.clicked.connect(partial(self.start, animations))

        q.click()

    def start(self, animations: QParallelAnimationGroup):
        animations.start()
        
        def callback():
            for i in self.labels:
                i.hide()
        
        animations.finished.connect(callback)

        self.blurs.start()


class QCustomButton:
    """Creates A Push Button With Some Tunings"""

    def __init__(self, text, window , setStyle = False , addtext = None) -> None:
        self.text = text
        
        self.window = window
        
        self.setStyle = setStyle
    
    def create(self):        
        self.button = QPushButton(self.window)
                
        if(self.setStyle):
            self.button.setStyleSheet('font-size: 80px')

        self.button.setFlat(True)

        self.button.setText(self.text)

        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        
        return self.button

class PopUpMessage:            
    def new_msg(self , window , msg , duration):        
        self.window = window
        
        try:
            self.popup_window.hide()
        except:
            pass
        
        self.popup_window = QLabel(self.window)
                
        self.popup_window.setFixedWidth(len(msg) * 20)
                
        self.popup_window.setFixedHeight(60)
        
        self.popup_window.setAlignment(Qt.AlignCenter)
                
        self.popup_window.setText(msg)
        
        self.popup_window.setStyleSheet(
            """
                QLabel{
                    background-color: #4C566A;
                    font-size: 20px;
                    font-family: "Comfortaa"
                }
            """    
        )
        
        self.animation = QPropertyAnimation(self.popup_window, b"pos")

        self.animation.setStartValue(QPoint(20, 1200))

        self.animation.setEndValue(QPoint(20, 900))

        self.animation.setDuration(duration)
    
        self.popup_window.show()
        
        timer = QTimer(self.window)
        
        timer.timeout.connect(self.remove)
        
        timer.start(2000)
        
        self.start()
        
        
    def start(self):
        self.animation.start()
        
    def updateText(self , text):
        self.popup_window.setText(text)
        
    def remove(self):
        self.an = QPropertyAnimation(self.popup_window, b"pos")

        self.an.setStartValue(self.popup_window.pos())

        self.an.setEndValue(QPoint(20, 1000))

        self.an.setDuration(200)
            
        self.an.start()
        
        self.an.finished.connect(self.popup_window.hide)
        
class QContinueButton:
    def __init__(self , window) -> None:
        self.window = window
    
    def start(self , text="Continue"):
        self.button = QPushButton(self.window)
        
        self.button.setFlat(True)
        
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        
        self.layout = QHBoxLayout()
        
        first_text = QLabel(text)
        
        second_text = QLabel(text="  ")
        
        animation = QPropertyAnimation(second_text , b"pos")

        animation.setDuration(200)
        
        animation.setStartValue(QPoint(self.button.pos().x() + 110 , self.button.y() + 10))
        
        animation.setEndValue(QPoint(self.button.pos().y() + 130 , self.button.pos().x() + 10))
        
        leave_ani = QPropertyAnimation(second_text , b"pos")
        
        leave_ani.setDuration(200)
        
        leave_ani.setEndValue(QPoint(self.button.pos().x() + 110 , self.button.y() + 10))
        
        leave_ani.setStartValue(QPoint(self.button.pos().y() + 130 , self.button.pos().x() + 10))
        
        self.layout.addWidget(first_text)
        
        self.layout.addWidget(second_text)
        
        self.button.setLayout(self.layout)
        
        onhover = lambda x : animation.start()
        
        leave = lambda x: leave_ani.start()
        
        self.button.enterEvent = onhover
        
        self.button.leaveEvent = leave
        
        return self.button

class Animation:
    def movingAnimation(self , widget , endValue , duration):
        animation = QPropertyAnimation(widget , b"pos")
        
        animation.setStartValue(widget.pos())
        
        animation.setEndValue(endValue)
        
        animation.setDuration(duration)
        
        return animation
    
    def fadingAnimation(self , widget: QWidget , duration, reverse=False , startValue = 0, endValue = 0):
        opacity = widget.graphicsEffect()
                
        if(opacity == None):
            opacity = QGraphicsOpacityEffect()
                 
            widget.setGraphicsEffect(opacity)
        
        animation = QPropertyAnimation(opacity , b"opacity")
        
        if(not reverse):
            animation.setStartValue(1)
            
            animation.setEndValue(endValue)
        else:
            animation.setStartValue(startValue)
        
            animation.setEndValue(1)
        
        animation.setDuration(duration)
        
        return animation

class QBalloonToopTip:
    def __init__(self , parent , geo: QRect) -> None:
        self.parent = parent
        
        self.geo = geo
        
        self.text = ""
        
    def setText(self , text):
        self.text = text
    
    def show(self):
        tool = QLabel(self.parent)
        
        tool.setText(self.text)
        
        tool.setGeometry(QRect(
            self.geo.left(),
            self.geo.top() + self.geo.height() + 20,
            self.geo.width(),
            30
        ))
        
        tool.show()
        
class QLayoutMaker:
    def __init__(self , icons: list[list[str]] , functions: list) -> None:
        self.icons = icons
        self.functions = functions
        
    def make(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        
        i = 0
        
        for icon, icon_color, icon_font_size, icon_family in self.icons:
            item = QCustomButton(icon, None).create()
            
            item.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    icon_color, icon_font_size, icon_family
                )
            )

            item.clicked.connect(self.functions[i])

            i += 1

            layout.addWidget(item)
        
        return layout

class QSliderMenu(QLabel):
    def __init__(self , parent) -> None:
        super().__init__(parent)
        
        self.head = parent
        
        self.setGeometry(QRect(2000, 0, 400, 1000))

        self.show()

        layout = QVBoxLayout(self)

        self.scrollArea = QScrollArea(self)

        layout.addWidget(self.scrollArea)

        self.buttons = QWidget(self)

        self.buttons.setGeometry(QRect(100, 0, 400, 1000))

        self.scrollArea.setWidget(self.buttons)

        self.second_layout = QVBoxLayout(self.buttons)

        self.buttons.setLayout(self.second_layout)

        
    def addMenu(self , name , widget , addAsLayout = False):
        childLayout = QVBoxLayout()
        
        print(widget)
        
        if(name != ""):
            nameLabel = QLabel()
            
            nameLabel.setText(name)
            
            nameLabel.setGeometry(self.geometry())
            
            nameLabel.setStyleSheet("color: white; font-size: 20px; font-family: Comfortaa")
        
            childLayout.addWidget(nameLabel)
        
        if(addAsLayout):
            childLayout.addLayout(widget)
        else:
            childLayout.addWidget(widget)
        
        widget.setGeometry(self.geometry())
        
        self.second_layout.addLayout(childLayout)