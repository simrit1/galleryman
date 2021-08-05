from PyQt5.QtGui import QKeyEvent, QKeySequence, QPixmap
from GalleryMan.assets.QtHelpers import Animation, PopUpMessage
import os
from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QLineEdit, QShortcut, QVBoxLayout


class getMoreInfo:
    def __init__(self , scrollArea , renderArea , directory , application) -> None:
        self.renderArea = renderArea
        
        self.scrollArea = scrollArea
        
        self.directory = directory
        
        self.application = application
        
        self.message = PopUpMessage()
        
        self.image = Image.open("GalleryMan/assets/processed_image.png")
        
    def getInfo(self):
        try:
            self.animation = Animation.fadingAnimation(Animation , self.parent , 100)
            
            self.animation.finished.connect(self.parent.hide)
            
            self.animation.start()
            
        except Exception as e:
            pass
        
        try:
            
            self.animation = Animation.fadingAnimation(Animation , self.renameParent , 100)
            
            self.animation.finished.connect(self.renameParent.hide)
            
            self.animation.start()
            
        except:
            
            pass
        
        self.parent = QLabel(self.renderArea)
        
        self.parent.setProperty("class" , "need")
        
        self.parent.setGeometry(self.renderArea.geometry())
        
        self.parent.setStyleSheet("""
            QLabel[class="need"]{{
                background-color: #2E3440; 
            }}
        """)
                
        layout = QVBoxLayout()
        
        filePath = QLabel()

        filePath.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)

        filePath.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        filePath.setText("File Path: {}".format(self.directory))
        
        layout.addWidget(filePath)
        
        filePath = QLabel()

        filePath.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)

        filePath.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        filePath.setText("File Name: {}".format(self.directory[self.directory.rindex("/") + 1:]))
        
        layout.addWidget(filePath)
        
        width , height = Image.open(self.directory).size
        
        filePath = QLabel()

        filePath.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)

        filePath.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        filePath.setText("Resolution: {} x {}".format(width , height))
        
        layout.addWidget(filePath)
                
        bytesSize = os.path.getsize(self.directory)
        
        filePath = QLabel()

        filePath.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)

        filePath.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        filePath.setText("File Size: {} bytes ({} MB)".format(bytesSize , round(bytesSize / 1e+6 , 2)))
        
        layout.addWidget(filePath)
        
        self.parent.setLayout(layout)
        
        self.parent.show()
    
    def castToScreen(self):
        pass
    
    def searchGoogle(self):
        pass
    
    def showInFullScreen(self):
        imageInFull = QLabel(self.application)
        
        imageInFull.setGeometry(self.application.geometry())
        
        imageInFull.setPixmap(QPixmap("GalleryMan/assets/processed_image.png").scaled(self.application.geometry().width() , self.application.geometry().height() , transformMode=Qt.SmoothTransformation))
        
        imageInFull.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        imageInFull.show()
    
    def rename(self):
        try:
            
            self.animation = Animation.fadingAnimation(Animation , self.renameParent , 100)
            
            self.animation.finished.connect(self.renameParent.hide)
            
            self.animation.start()
            
        except:
            
            pass
        
        try:
            
            self.animation = Animation.fadingAnimation(Animation , self.renameParent , 100)
            
            self.animation.finished.connect(self.parent.hide)
            
            self.animation.start()
            
        except:
            
            pass
        
        self.renameParent = QLabel(self.renderArea)
        
        self.renameParent.setProperty("class" , "need")
        
        self.message.new_msg(self.application , "Press Enter To Rename File" , 300)
        
        key = QShortcut(QKeySequence("Return") , self.renameParent)
        
        key.activated.connect(self.saveWithNew)
        
        self.renameParent.setGeometry(self.renderArea.geometry())
        
        self.renameParent.setStyleSheet("""
            QLabel[class="need"]{{
                background-color: #2E344050;
            }}
        """)
        
        layout = QVBoxLayout()
        
        self.inputBox = QLineEdit()
        
        self.inputBox.setFixedHeight(50)
        
        self.inputBox.setFixedWidth(1000)
        
        self.inputBox.setPlaceholderText("New file name: ")
        
        self.inputBox.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
            font-family: Comfortaa                       
        """)
        
        self.inputBox.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        layout.addWidget(self.inputBox , alignment=Qt.AlignCenter | Qt.AlignCenter)
        
        self.renameParent.setLayout(layout)
        
        self.renameParent.show()
    
    def callback(self):
        pass
    
    def saveWithNew(self):
        try:
            self.image.save(self.inputBox.text())
            
            self.animation = Animation.fadingAnimation(Animation , self.renameParent , 300)
            
            self.animation.start()
            
        except:
            self.message.new_msg(self.application , "Invalid File Extension" , 400)