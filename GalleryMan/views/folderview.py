from configparser import ConfigParser
import json, os
import pathlib
from random import randint
from PyQt5.QtCore import QObject, QParallelAnimationGroup, QPoint, QRect, QThread, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QScrollArea, QWidget
from PyQt5.QtGui import QColor, QCursor, QMovie, QPixmap
from GalleryMan.assets.singleFolder import singleFolderView
from GalleryMan.views.directoryView import QDoublePushButton
from math import ceil
from GalleryMan.assets.QtHelpers import Animation, PopUpMessage

class PixmapHeaderMaker(QObject):
    finished = pyqtSignal()
    
    def run(self , inst , parent , imageArea: QLabel , border , width , height , dir):
        path = imagesFolder.get_first(dir)
                
        if(path == None):
            parent.hide()
        else:
            print(path)            
            imageArea.setPixmap(
                QPixmap(path).scaled(
                    width - (int(border) * 2),
                    height - 52,
                    transformMode=Qt.SmoothTransformation,
                )
            )
            
            inst.addFolder(parent)
            
            inst.responser(None)
            
        self.finished.emit()

class Loader(QObject):
    finished = pyqtSignal()
    
    def run(self , parent):
        self.movie = QMovie(parent)
        
        self.movie.setFileName("GalleryMan/assets/loader.gif")
        
        parent.setMovie(self.movie)
            
        self.movie.start()     
        
        self.finished.emit() 
        
class Worker(QObject):
    finished = pyqtSignal()
    
    def run(self , inst , mode , colors , x , y , width , height , padding):
        LIKED_FOLDERS = ".config/galleryman/data/likedPhotos.txt"
        
        color_rest = 0
                
        # Iterate through all the dirs
        for i in [LIKED_FOLDERS] + inst.dirs:            
            # Create a complete path of the folder
            curr = "{}/{}".format(os.path.expanduser("~"), i)

            # Check if the path is a folder and it is not in the prevent dirs
            if i == LIKED_FOLDERS or (os.path.isdir(curr) and i[0] != "." and curr not in inst.prevented_dirs):
                if mode == "single":
                    color_rest = 0
                elif mode == "random":
                    color_rest = randint(0, len(colors))
                else:
                    color_rest = (color_rest + 1) % len(colors)

                res = inst.update(curr, x, y, False, colors[color_rest])

                if res:
                    inst.no += 1

                    x += width + padding

                    if x > inst.window.width() - width:
                        x = 40

                        y += height + padding
                        
        self.finished.emit()

class imagesFolder:
    """Creates The UI"""

    def __init__(
        self,
        window: QWidget,
        main_window: QMainWindow,
        scroll: QScrollArea,
        config: ConfigParser,
    ) -> None:
        # Make the QMainWindow global]
        self.main_window = main_window


        self.isshown = False

        self.scroll = scroll

        self.scroll.horizontalScrollBar().setValue(0)

        self.scroll.horizontalScrollBar().valueChanged.connect(
            lambda: self.scroll.horizontalScrollBar().setValue(0)
        )

        self.window = window

        self.config = config

        # Set the start value of the folders. It will keep the track of the position where the folder will be added, basically at the first of the all the folder's row
        self.folderStartValue = 250

        self.popup = PopUpMessage()

        # A label which will contain all the folders
        self.images = QLabel(self.window)

        # Change the geometry
        self.images.setGeometry(QRect(0, 0, 1980, 1080))
        
        self.images.show()
        
        self.allFolders = []
        
    def start(self, label_to_change: QLabel) -> True:
        LIKED_FOLDERS = ".config/galleryman/data/likedPhotos.txt"
        
        """Creates The Ui And Renders To The MainWindow passes during __init__

        Args:
            label_to_change (QLabel): The header text, which will be changed to the "Albums"
        """

        self.scroll.verticalScrollBar().setEnabled(True)

        self.scroll.verticalScrollBar().show()

        if not self.isshown:
            self.popup.new_msg(self.window, "Welcome To GalleryMan!", 200)

            self.isshown = True

        # Initing all the variables that will be used
        self.folders_pinned = []

        self.allFolders = []

        self.dirs = os.listdir(os.path.expanduser("~"))

        self.label_to_change = QLabel(text="Albums", parent=self.window)

        self.label_to_change.setGeometry(label_to_change.geometry())

        self.label_to_change.setAlignment(label_to_change.alignment())

        self.label_to_change.show()

        self.update_styling()

        # Change The Name Of The Window
        self.window.setObjectName("PyGallery")

        # Set Geometry
        self.window.setGeometry(0, 0, 1900, 1000)

        # Now, Folder's Header Text
        self.folderHeaderText = QLabel(self.images)

        # Change StyleSheet
        self.folderHeaderText.setStyleSheet(
            """color: {}; font-family: {}; font-size: {};""".format(
                self.config.get("folderPage", "restFolders-folderNameColor"),
                self.config.get("folderPage", "restFolders-folderNameFontFamily"),
                self.config.get("folderPage", "restFolders-folderNameSize") + "px",
            )
        )
        
        

        # Set Fixed Width And Height
        self.folderHeaderText.setFixedHeight(50)

        self.folderHeaderText.setFixedWidth(200)

        # Move To Desired Position
        self.folderHeaderText.move(QPoint(40, 500))

        # Change Text
        self.folderHeaderText.setText(
            self.config.get("folderPage", "restFolders-icon")[1:-1] + "Folders"
        )

        # Show The Text
        self.folderHeaderText.show()

        # Get all the prevented directory selected during the startup
        self.prevented_dirs = json.loads(
            open("/home/strawhat54/.config/galleryman/data/scan_dirs.txt").read()
        )

        # Create x and y variables which will determine the position of the folder's card
        x, y = 40, self.folderStartValue

        colors = self.config.get("folderPage", "folders-color")

        height, width = int(self.config.get("folderPage", "folders-height")), int(
            self.config.get("folderPage", "folders-width")
        )

        height += int(self.config.get("folderPage", "folders-borderWidth"))

        padding = int(self.config.get("folderPage", "folders-padding"))

        mode = self.config.get("folderPage", "folders-mode")[1:-1]

        colors = json.loads(self.config.get("folderPage", "folders-color"))

        self.keybindings = json.loads(
            self.config.get("folderPage", "folderPage-keybindings")
        )

        self.no = 0
        
        self.thread = QThread()
        
        self.worker = Worker()
        
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(lambda : self.worker.run(self , mode , colors , x , y , width , height, padding))
        
        self.worker.finished.connect(self.thread.quit)
        
        self.thread.start()
     
        perline = (self.main_window.size().width() - 100) // width

        self.width = (
            self.label_to_change.height()
            + ((width + padding) * self.no // perline)
            - padding
        )
                
        self.width = max(self.width, self.main_window.size().height() - 100)

        self.window.setFixedHeight(self.width)

        self.images.setFixedHeight(self.width)

        # Display the desired message if no cards are there under the folder's header
        if self.allFolders == []:
            self.showMessage()
            
        self.main_window.resizeEvent = self.responser
        
        self.main_window.show()
        
        

        # Final touches, call the responser to position the cards accurately, if it's not
        self.responser(None)

        # End of the function by returning True
        return True

    def update(self, dir: str, x: int, y: int, is_pinned: bool, color: str) -> bool:
        """
        Creates the card of the folder

        # Args:

        dir (str): The path of the folder whose card needs to be created

        x (int): the x position where the card will be visible

        y (int): the y position where the card will be visible

        is_pinned (bool): Is the folder pinned?

        # Return

        bool: Whether creating the folder will worth
        """

        # Create a Button For The Card
        label = QDoublePushButton("", self.images)

        if dir in self.keybindings:
            label.setShortcut(self.keybindings[dir])

        # Set PointingHand Cursor 
        label.setCursor(QCursor(Qt.PointingHandCursor))

        if dir in self.keybindings:
            label.setShortcut(self.keybindings[dir])
        elif dir[:-1] in self.keybindings:
            label.setShortcut(self.keybindings[dir[:-1]])
        elif dir + "/" in self.keybindings:
            label.setShortcut(self.keybindings[dir + "/"])

        # Set a special property, so as to prevent intraction of the label at the time of setting the border
        label.setProperty("class", "image")

        border = self.config.get("folderPage", "folders-borderWidth")

        # Set the stylesheet
        label.setStyleSheet(
            """                    
            QPushButton[class="image"]{{
                border: {}px solid {};
            }}
        """.format(
                border, color
            )
        )

        height, width = int(self.config.get("folderPage", "folders-height")), int(
            self.config.get("folderPage", "folders-width")
        )

        # Set Fixed Width And Height
        label.setFixedHeight(height + int(border))

        label.setFixedWidth(width)

        # Create A Label for showing the first picture
        imageArea = QLabel(label)
        
        imageArea.setPixmap(QPixmap("GalleryMan/assets/loader.png").scaled(width , height))

        # Set the Alignment
        imageArea.setAlignment(Qt.AlignCenter)

        # Set fixed width and height
        imageArea.setFixedHeight(height - 52)

        imageArea.setFixedWidth(width - (int(border) * 2))

        # Move a little bit aside for showing the border
        imageArea.move(QPoint(int(border), int(border)))
        
        worker = PixmapHeaderMaker()
    
        self.another = QThread(self.window)
        
        self.another.started.connect(lambda : worker.run(self , label , imageArea , border , width , height , dir))
        
        self.worker.finished.connect(self.another.quit)
        
        self.worker.finished.connect(lambda : self.responser(None))

        worker.moveToThread(self.another)
        
        self.another.start()

        # A Label to show the name of the directory
        folderName = QLabel(label)

        # Set fixed width and height
        folderName.setFixedHeight(50)

        folderName.setFixedWidth(width - (int(border) * 2))

        folderName.move(QPoint(int(border), height - 52))

        folderName.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        # Set some styles
        folderName.setStyleSheet(
            "color: {}; font-family: {}; font-size: {}px; padding-top: {}px".format(
                self.config.get("folderPage", "folderName-color"),
                self.config.get("folderPage", "folderName-fontFamily"),
                self.config.get("folderPage", "folderName-fontSize"),
                self.config.get("folderPage", "folderName-topPadding"),
            )
        )

        # Set alignment
        folderName.setAlignment(Qt.AlignCenter)

        # Change the text of the label with the folder's name
        if(dir != "/home/strawhat54/.config/galleryman/data/likedPhotos.txt"):
            folderName.setText(dir[dir.rindex("/") + 1 :])
        else:
            folderName.setText("Liked Photos")

        # Move the card yo the desired postion
        label.move(QPoint(x, y))

        # Set a property of the card with a value as the directory, will help while pinning
        label.setProperty("directory", dir)

        # Move to the next page (which shows all the available images in a folder)
        label.clicked.connect(lambda: self.transfer_control(dir))
        
        label.show()
        
        # Return True, nothing is better than that XD
        return True
    
    def addFolder(self , folder):
        self.allFolders.append(folder)

    def get_first(dir: str) -> str:
        """Returns the first image in the folder, or None if no image is available

        Args:
            dir (str): [description]

        Returns:
            str: [description]
        """        
        if(dir == "/home/strawhat54/.config/galleryman/data/likedPhotos.txt"):
            with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt" , 'r') as f:
                dirs = json.loads(f.read())
            
            return dirs[0] if dirs else None

        # Iterate through all the files and folders in the directory
        for i in pathlib.Path(dir).rglob("*"):
            i = str(i)
            
            # Check if the image is a supported one
            if i[-3:] in ["png", "jpeg", "jpg", "webp"] and not os.path.isdir(
                "{}/{}".format(dir, i)
            ):
                return i

        return None

    def responser(self, event=None):
        """Sets the geometry of the widgets according to the new width of the window

        Args:
            event (QEvent): Event passed during the resizing, not used
        """

        # Get the necessary items from config
        card_height, card_width, padding = (
            int(self.config.get("folderPage", "folders-height")),
            int(self.config.get("folderPage", "folders-width")),
            int(self.config.get("folderPage", "folders-padding")),
        )

        # Hide the messages if the folders is not empty
        if self.allFolders != []:
            self.hide_msg()

        # Check how many cards can fit in one line
        self.per_line = max((self.main_window.width() - padding - 50) // card_width, 1)

        # New x and y positions
        x, y = 40, 220

        # Create a parallel animation group
        self.an = QParallelAnimationGroup()

        # Create a animation for the header if it is available
        try:
            self.an.addAnimation(
                Animation.movingAnimation(
                    Animation,
                    self.folderHeaderText,
                    QPoint(40, self.folderStartValue - 80),
                    100,
                )
            )

        except:
            pass

        # Create new x and y positions according to the height being used by the pinned folders
        height = self.main_window.size().height()

        x, y = 40, self.folderStartValue

        for i in self.allFolders:
            self.an.addAnimation(
                Animation.movingAnimation(Animation, i, QPoint(x, y), 100)
            )

            # Update x and y
            x += card_width + padding

            if x > self.main_window.width() - 260:
                x = 40

                y += card_height + padding

        # Check if the msg exists
        try:
            self.an.addAnimation(
                Animation.movingAnimation(
                    Animation, self.msg, QPoint(100, self.folderStartValue + 310), 100
                )
            )
        except:
            pass

        perline = (self.main_window.size().width() - 100) // card_width

        self.width = (
            self.label_to_change.height()
            + ((card_width + padding) * self.no // perline)
            - padding
        )

        self.width = max(self.width, self.main_window.size().height())

        self.window.setFixedHeight(self.width)

        self.images.setFixedHeight(self.width)

        self.label_to_change.setFixedWidth(self.main_window.size().width())

        self.label_to_change.setAlignment(Qt.AlignCenter)

        # Start the animation
        self.an.start()

    def pushDown(self):
        # Pushing down effect of the info
        self.anim = QParallelAnimationGroup()

        try:
            self.anim.addAnimation(Animation.fadingAnimation(Animation, self.info, 200))
        except:
            pass

        self.anim.addAnimation(
            Animation.movingAnimation(
                Animation,
                self.folderHeaderText,
                QPoint(40, self.folderHeaderText.pos().y() + 400),
                200,
            )
        )

        # Start the animation
        self.anim.start()

        # Hide the info on being animated
        self.anim.finished.connect(lambda: self.info.hide())

    def showMessage(self):
        # Create a msg label
        self.msg = QLabel(
            parent=self.window,
            text="Oops! Your unselected folders do no contain any image!",
        )

        # Set perfect geometry
        self.msg.setGeometry(QRect(4000, 100, 1980, 100))

        # Some styling
        self.msg.setStyleSheet(
            """
            QLabel{
                font-size: 25px;
                color: #4C566A;
            }                     
            """
        )

        try:
            Animation.fadingAnimation(Animation, self.msg, 400).start()
        except:
            pass

        self.msg.show()

    def hide_msg(self):
        # Hides message
        try:
            self.ani = Animation.fadingAnimation(Animation, self.msg, 200, True)

            self.ani.start()

            self.ani.finished.connect(lambda: self.msg.hide())
        except:
            pass

    def update_styling(self):
        """
        Updates The Styling Of The Main Window After Adding A Property
        """

        self.window.style().unpolish(self.window)

        self.window.style().polish(self.window)

        self.window.update()

    def transfer_control(self, directory):
        """Transfers control to the singleFolderPage"""

        # Parallel Animation Group
        self.effects = QParallelAnimationGroup()

        self.effects.addAnimation(
            Animation.fadingAnimation(Animation, self.images, 400)
        )

        self.effects.addAnimation(
            Animation.fadingAnimation(Animation, self.label_to_change, 400)
        )

        self.effects.start()

        # Run second slot of animations
        self.effects.finished.connect(lambda: self.run_second(directory))

    def run_second(self, dir):
        print("Sending dir -> " , dir)
        
        self.folderHeaderText.hide()

        self.args = []

        try:
            if not self.msg.isHidden():
                self.args.append(self.msg)

            self.msg.hide()

        except:

            pass

        try:
            if not self.info.isHidden():
                self.args.append(self.info)

            self.info.hide()

        except:

            pass

        self.label_to_change.hide()

        singleFolderView(
            self.window,
            dir,
            self.config,
            self.scroll,
            self.main_window,
            self.label_to_change,
            self.images,
            self.folderHeaderText,
            *self.args
        ).start()
