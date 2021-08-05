# Import All Modules
from GalleryMan.utils.helpers import ResizableRubberBand
from GalleryMan.assets.QtHelpers import QContinueButton
from PIL import Image 
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QLabel, QMainWindow
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal

class Resizable(QLabel):
    def __init__(self , parent):
        super().__init__(parent)
        
        self.setGeometry(QRect(10 , 10 , 100 , 100))
        
        self.setStyleSheet("background-color: rgb(255 , 0 , 0)")
        
    def createHandles(self):
        for pos in [Qt.AlignTop | Qt.AlignLeft , Qt.AlignTop | Qt.AlignRight , Qt.AlignBottom | Qt.AlignLeft , Qt.AlignBottom | Qt.AlignRight]:
            label = QLabel(self)
            
            label.setFixedSize(QSize(10 , 10))
            
            label.setStyleSheet("border: 1px solid white")
            
            label.setAlignment(pos)
            
            label.show()
            
# Main Cropper Class
class ImageCropper(QtWidgets.QGraphicsView):
    # Signals
    closed = pyqtSignal()
        
    # __init__ the QGraphicsView Class
    def __init__(self, inst , main_window: QMainWindow, name , out_widget , callback):                
        super().__init__(main_window)
        
        self.originalResponser = main_window.resizeEvent
        
        main_window.resizeEvent = self.resizeEvent
        
        self.graphicsScene = QGraphicsScene(self)
        
        self.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.setScene(self.graphicsScene)
        
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                
        self.pixmap = self.graphicsScene.addPixmap(QtGui.QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.cropper = ResizableRubberBand()
        
        self.scene().addWidget(self.cropper)
        
        self.cropper.setGeometry(QRect(50 , 50 , 300 , 300))
        
        self.cropper.show()
        
        self.continueCrop = QContinueButton(self).start()
        
        self.continueCrop.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;                         
            background-color: transparent;         
        """)
        
        self.continueCrop.enterEvent(None)
        
        self.continueCrop.setGeometry(QRect(50 , 50 , 500 , 100))
        
        self.continueCrop.clicked.connect(self.continueCropping)
        
        self.resizeEvent(main_window.size())
        

    def continueCropping(self):
        image = Image.open("GalleryMan/assets/processed_image.png")
        
        x , y , width , height = self.cropper.geometry().x() , self.cropper.geometry().y() ,  self.cropper.geometry().width() ,  self.cropper.geometry().height()
        
        image = image.crop((x , y , width + x , height + y))
        
        image.save("new_image.png")
        
    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        try:
            self.continueCrop.move(QPoint(
                event.size().width() - 200,
                event.size().height() - 100,
            ))
        except:
            self.continueCrop.move(QPoint(
                event.width() - 200,
                event.height() - 100,
            ))