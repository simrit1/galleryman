# Import All Modules
from configparser import ConfigParser
from PyQt5.QtGui import QPaintEvent, QPainter, QPixmap, QPolygonF, QResizeEvent, QTransform
from GalleryMan.utils.helpers import ResizableRubberBand
from GalleryMan.assets.QtHelpers import Animation, QContinueButton
from PIL import Image
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QLabel, QMainWindow
from PyQt5.QtCore import QAbstractAnimation, QPoint, QPointF, QRect, QRectF, QVariant, QVariantAnimation, Qt, pyqtSignal, pyqtSlot


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


# Main Cropper Class
class ImageCropper(QGraphicsView):
    # Signals
    closed = pyqtSignal()

    # call the __init__ function of the QGraphicsView Class
    def __init__(self, mainWindow: QMainWindow, outWidget: QRotateLabel , config: ConfigParser):
        super().__init__(mainWindow)
        
        # Get the original responser so that it could be replaced on removing
        self.originalResponser = mainWindow.resizeEvent
        
        # Create a scene which will contain all the images and rest
        self.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.myScene = QGraphicsScene()
        
        self.myScene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.setScene(self.myScene)
        
        # Create a resizable label for cropping
        self.cropper = ResizableRubberBand()
        
    
        # Add to scene
        self.scene().addWidget(self.cropper)
        
        # Set geometry
        self.cropper.setGeometry(QRect(50, 50, 300, 300))
        
        # Show the cropper
        self.cropper.show()
        
        # A button to save the cropped image
        self.continueCrop = QContinueButton(self).start()

        self.continueCrop.setStyleSheet(
            """ResizableRubberBand
            color: #D8DEE9;
            font-size: 20px;                         
            background-color: transparent;         
        """
        )
        
        self.outWidget = outWidget

        self.continueCrop.enterEvent(None)

        self.continueCrop.setGeometry(QRect(
            mainWindow.width() - 300,
            mainWindow.height() - 150,
            250,
            100
        ))

        self.continueCrop.clicked.connect(self.continueCropping)
        
        self.continueCrop.show()
        

    def continueCropping(self):
        """Saves the cropped image"""
        
        #  A function which will do additional changes when the animation is over
        def next():
            
            # Hide the graphics
            self.hide()

            # Set the updated image as the preview
            self.outWidget.set_pixmap(QPixmap('GalleryMan/assets/processed_image.png'))
        
        # Open the image using PIL
        image = Image.open("GalleryMan/assets/processed_image.png")
        
        # Get cropping coordinates
        x, y, width, height = (
            self.cropper.geometry().x(),
            self.cropper.geometry().y(),
            self.cropper.geometry().width(),
            self.cropper.geometry().height(),
        )
        
        # Crop
        image = image.crop((x, y, width + x, height + y))
        
        # Save
        image.save("GalleryMan/assets/processed_image.png")
        
        # Animation
        self.animation = Animation.fadingAnimation(Animation , self , 300)
        
        self.animation.finished.connect(next)
        
        self.animation.start()

    def resizeEvent(self, event: QResizeEvent) -> None:
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
            
    def paintEvent(self, event: QPaintEvent) -> None:
        # qp = QPainter()
        
        # qp.begin(self)

        # polygon = QPolygonF()
        
        # for points in [QPoint(500 , 50) , QPoint(500 , 100) , QPoint(500 - 65 , 100) , QPoint(500 - 65 - 10 , 95) , QPoint(500 - 65 , 75) , QPoint(75 , 100) , QPoint(75 , 50)]:
        #     polygon.append(QPointF(points))
            
        # qp.drawPolygon(polygon)

        # qp.end()
        
        return super().paintEvent(event)
        