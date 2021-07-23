from functools import partial
from PyQt5 import QtCore
from PyQt5.QtCore import QParallelAnimationGroup, QPoint, QPropertyAnimation, QRect, QSize, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QPushButton

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
        self.x = x
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
            [self.x - 50, self.x + 50, self.x + 0],
            [self.y - 70, self.y - 70, self.y + 40],
        ):
            label = QLabel(self.window)

            label.setText("  ")
            
            label.setStyleSheet("background-color: transparent; font-family: SauceCodePro Nerd Font")
            
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
        
        timer.timeout.connect(lambda : self.remove())
        
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
        
        self.an.finished.connect(lambda: self.popup_window.hide())
        
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
    
    def fadingAnimation(self , widget , duration, reverse=False , startValue = 0, endValue = 0):
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