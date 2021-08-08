# Import All Modules
from GalleryMan.utils.helpers import ResizableRubberBand
from GalleryMan.assets.QtHelpers import Animation, QContinueButton
from PIL import Image
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QLabel, QMainWindow
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal

# Main Cropper Class
class ImageCropper(QtWidgets.QGraphicsView):
    # Signals
    closed = pyqtSignal()

    # __init__ the QGraphicsView Class
    def __init__(self, inst, main_window: QMainWindow, name, out_widget, callback):
        super().__init__(main_window)
        
        # Get the original responser so that it could be replaced on removing
        self.originalResponser = main_window.resizeEvent
        
        # Use custom responser
        main_window.resizeEvent = self.resizeEvent
        
        # Create a scene which will contain all the images and rest
        self.graphicsScene = QGraphicsScene(self)

        self.setGeometry(QRect(0, 0, 1980, 1080))

        self.setScene(self.graphicsScene)

        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.pixmap = self.graphicsScene.addPixmap(
            QtGui.QPixmap("GalleryMan/assets/processed_image.png")
        )

        self.cropper = ResizableRubberBand()

        self.scene().addWidget(self.cropper)

        self.cropper.setGeometry(QRect(50, 50, 300, 300))

        self.cropper.show()

        self.continueCrop = QContinueButton(self).start()

        self.continueCrop.setStyleSheet(
            """
            color: #D8DEE9;
            font-size: 20px;                         
            background-color: transparent;         
        """
        )
        
        self.outWidget = out_widget

        self.continueCrop.enterEvent(None)

        self.continueCrop.setGeometry(QRect(
            main_window.width() - 300,
            main_window.height() - 150,
            250,
            100
        ))

        self.continueCrop.clicked.connect(self.continueCropping)
        
        self.continueCrop.show()
        

    def continueCropping(self):
        def next():
            self.hide()
            
            self.outWidget.set_pixmap(QtGui.QPixmap('GalleryMan/assets/processed_image.png'))
            
        image = Image.open("GalleryMan/assets/processed_image.png")

        x, y, width, height = (
            self.cropper.geometry().x(),
            self.cropper.geometry().y(),
            self.cropper.geometry().width(),
            self.cropper.geometry().height(),
        )

        image = image.crop((x, y, width + x, height + y))

        image.save("GalleryMan/assets/processed_image.png")
        
        self.animation = Animation.fadingAnimation(Animation , self , 300)
        
        self.animation.finished.connect(next)
        
        self.animation.start()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        try:
            self.continueCrop.move(
                QPoint(
                    event.size().width() - 300,
                    event.size().height() - 170,
                )
            )
        except:
            self.continueCrop.move(
                QPoint(
                    event.width() - 300,
                    event.height() - 170,
                )
            )
