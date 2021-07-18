# Import All Modules
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QDialogButtonBox, QPushButton
from functools import partial
from PyQt5.QtCore import Qt, pyqtSignal

# Main Cropper Class
class ImageCropper(QtWidgets.QGraphicsView):
    closed = pyqtSignal()
    
    # __init__ the QGraphicsView Class
    def __init__(self, main_window , name , out_widget , callback):
        super().__init__(QtWidgets.QGraphicsScene(main_window) , parent=main_window)
        
        self.callback = callback
        # Make the arguments global        
        self.out_widget = out_widget
        
        self.main_window = main_window
                
        # Change The Cursor (Use A CrossHair Pointer)
        self.main_window.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        
        # Add Pixmap 
        self.pixmap_item = self.scene().addPixmap(QtGui.QPixmap(name))
        
        # Set Geometry
        self.setGeometry(QtCore.QRect(0, 0, 1980, 1080))
        
        # Set Stylesheet
        self.setStyleSheet("background-color: #2E3440;")
        
        # Set Alignment
        self.setAlignment(QtCore.Qt.AlignCenter)
        
        # Background Role
        self.setBackgroundRole(QtGui.QPalette.Dark)
        
        # Use A PyQt's Rubber Band While Dragging.
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        
        # Connect to the function when the user expands the rubber band
        self.rubberBandChanged.connect(self.onRubberBandChanged)
        
        self.last_rect = QtCore.QPointF()

    def setPixmap(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)

    @QtCore.pyqtSlot(QtCore.QRect, QtCore.QPointF, QtCore.QPointF)
    def onRubberBandChanged(self, rubberBandRect, fromScenePoint, toScenePoint):
        if rubberBandRect.isNull():

            pixmap = self.pixmap_item.pixmap()

            rect = self.pixmap_item.mapFromScene(self.last_rect).boundingRect().toRect()

            if not rect.intersected(pixmap.rect()).isNull():

                self.crop_pixmap = pixmap.copy(rect)

                label = QtWidgets.QLabel(pixmap=self.crop_pixmap)
                
                self.dialog = QtWidgets.QDialog(self)
                
                self.buttons = QtWidgets.QDialogButtonBox(self.dialog)
                
                self.buttons.setFixedWidth(self.crop_pixmap.size().width())
                
                # Buttons
                for text in [" ReCrop" , " Continue" , "﫼 Exit"]:
                    button = QPushButton()
                    
                    button.setText(text)
                    
                    self.buttons.addButton(button , QDialogButtonBox.ActionRole)
                    
                    button.setFlat(True)
                    
                    button.clicked.connect(partial(self.parser , text))
                    
                    button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                                        
                    button.setStyleSheet('font-size: 25px')
                    
                lay = QtWidgets.QVBoxLayout(self.dialog)
                
                lay.addWidget(label)
                
                lay.setSpacing(20)
                
                lay.addWidget(self.buttons)
                
                self.dialog.exec_()

            self.last_rect = QtCore.QRectF()
        else:
            self.last_rect = QtCore.QRectF(fromScenePoint, toScenePoint)
            
    def parser(self , text):
        if(text == " ReCrop"):
            self.dialog.close()
            
        elif(text == " Continue"):
            self.dialog.close()
            
            self.crop_pixmap.save('GalleryMan/assets/processed_image.png')
            
            self.out_widget.set_pixmap(QtGui.QPixmap('GalleryMan/assets/processed_image.png'))
            
            self.out_widget.show()
            
            self.hide()     
            
            self.closed.emit()
            
            self.callback()
            
            self.main_window.setCursor(QtGui.QCursor(Qt.ArrowCursor))
               
        else:
            
            self.hide()
            
            self.callback()
            
            self.dialog.close()
            
            self.closed.emit()