from configparser import ConfigParser
from functools import partial
import json, os
from random import randint
from PyQt5.QtCore import QParallelAnimationGroup, QPoint, QRect
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QScrollArea, QWidget
from PyQt5.QtGui import QCursor, QPixmap
from GalleryMan.assets.singleFolder import singleFolderView
from GalleryMan.views.directoryView import QDoublePushButton
from math import ceil
from GalleryMan.assets.QtHelpers import Animation, PopUpMessage


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

        self.main_window.resizeEvent = self.responser

        self.isshown = False

        self.scroll = scroll

        self.window = window

        self.config = config

        # Set the start value of the folders. It will keep the track of the position where the folder will be added, basically at the first of the all the folder's row
        self.folderStartValue = 580

        self.popup = PopUpMessage()

        # A label which will contain all the folders
        self.images = QLabel(self.window)

        # Change the geometry
        self.images.setGeometry(QRect(0, 0, 1980, 1080))

        # Show the label
        self.images.show()

    def addToPin(self, directory: str) -> True:
        """Adds A Folder To The `GalleryMan`'s Pinned Folder's List

        Args:
            directory (str): The path of the directory Which Needs To Be Added To The List

        Returns:
            True: Congratulations (Probably always XD)! You have successfully added the directory to the list.
        """

        # Update The Pinned Folder Directory With The New Directory
        self.folders_added_to_file.append(directory)

        # Write The New Pinned Folder's List To The File
        with open("GalleryMan/data/pinned_folders.txt", "w") as f:
            f.write(json.dumps(self.folders_added_to_file))

        # Return True
        return True

    def remove(self, directory: str) -> True:
        """Removes A Folder To The `GalleryMan`'s Pinned Folder's List

        Args:
            directory (str): The path of the directory Which Needs To Be Removed From The List

        Returns:
            True: Congratulations (Probably always XD)! You have successfully removed the directory from the list.
        """

        # Sometimes, removing the directory gives me an error, so I added it to an if statement.
        if directory in self.folders_added_to_file:
            self.folders_added_to_file.remove(directory)

        # Write the updated list to the file
        with open("GalleryMan/data/pinned_folders.txt", "w") as f:
            f.write(json.dumps(self.folders_added_to_file))

        # Return True
        return True

    def start(self, label_to_change: QLabel) -> True:
        """Creates The Ui And Renders To The MainWindow passes during __init__

        Args:
            label_to_change (QLabel): The header text, which will be changed to the "Albums"
        """

        if not self.isshown:
            self.popup.new_msg(self.window, "Welcome To GalleryMan!", 200)

            self.isshown = True

        # Initing all the variables that will be used
        self.folders_pinned = []

        with open("GalleryMan/data/pinned_folders.txt") as f:
            self.folders_added_to_file = json.loads(f.read())

        self.allFolders = []

        self.label_to_change = QLabel(text="Albums", parent=self.window)

        self.label_to_change.setGeometry(label_to_change.geometry())

        self.label_to_change.setAlignment(label_to_change.alignment())

        self.label_to_change.show()

        self.update_styling()

        # Change The Name Of The Window
        self.window.setObjectName("PyGallery")

        # Set Geometry
        self.window.setGeometry(0, 0, 1900, 1000)

        # Pinned Albums Header Text
        self.pinned = QLabel(self.window)

        # Set Stylesheet
        self.pinned.setStyleSheet(
            """color: {}; font-family: {}; font-size: {};""".format(
                self.config.get("folderPage", "pinnedText-color"),
                self.config.get("folderPage", "pinnedText-fontFamily"),
                self.config.get("folderPage", "pinnedText-size") + "px",
            )
        )

        # Set Fixed Width And Height
        self.pinned.setFixedHeight(50)

        self.pinned.setFixedWidth(200)

        # Move To The Desired Position
        self.pinned.move(QPoint(40, 150))

        # Change Text
        self.pinned.setText(
            self.config.get("folderPage", "pinnedText-icon")[1:-1] + "Pinned"
        )

        # Show The Text
        self.pinned.show()

        # Now, Folder's Header Text
        self.folderHeaderText = QLabel(self.window)

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
        self.prevented_dirs = json.loads(open("GalleryMan/data/scan_dirs.txt").read())

        # Get all the dirs in the home directory
        self.dirs = os.listdir(os.path.expanduser("~"))

        # Create x and y variables which will determine the position of the folder's card
        x, y = 40, self.folderStartValue

        # A different x and y positions for pinned Folders
        px, py = 40, 220

        colors = self.config.get("folderPage", "folders-color")

        # Get all the pinned folders
        with open("GalleryMan/data/pinned_folders.txt") as file:
            self.currPinned = json.loads(file.read())

        height, width = int(self.config.get("folderPage", "folders-height")), int(
            self.config.get("folderPage", "folders-width")
        )

        height += int(self.config.get("folderPage", "folders-borderWidth"))

        padding = int(self.config.get("folderPage", "folders-padding"))

        mode = self.config.get("folderPage", "folders-mode")[1:-1]

        colors = json.loads(self.config.get("folderPage", "folders-color"))

        color_pinned = color_rest = 0

        self.keybindings = json.loads(
            self.config.get("folderPage", "folderPage-keybindings")
        )

        # Iterate through all the dirs
        for i in self.dirs:
            # Create a complete path of the folder
            curr = "{}/{}".format(os.path.expanduser("~"), i)

            # Check if the path is a folder and it is not in the prevent dirs
            if os.path.isdir(curr) and i[0] != "." and curr not in self.prevented_dirs:
                if mode == "single":
                    color_pinned = color_rest = 0
                elif mode == "random":
                    color_pinned = randint(0, len(colors))
                    color_rest = randint(0, len(colors))
                else:
                    color_pinned = (color_pinned + 1) % len(colors)
                    color_rest = (color_rest + 1) % len(colors)

                # Now, if curr is in the pinned folders, we will use the special variables (px , py) for setting its position
                if curr in self.currPinned:
                    res = self.update(
                        curr, px, py, curr in self.currPinned, colors[color_pinned]
                    )
                else:
                    res = self.update(
                        curr, x, y, curr in self.currPinned, colors[color_rest]
                    )

                # Check if adding of the card was successful or not
                if res:
                    # If it was successful, increase the value of the position variables, and yes, keep in mind about the width of the window
                    if not curr in self.currPinned:
                        x += width + padding

                        if x > self.window.width() - 100:
                            x = 40

                            y += height + padding
                    else:
                        px += width + padding

                        if px > self.window.width() - width:
                            px = 40

                            py += height + padding

        # Display the desired message if no cards are there under the folder's header
        if self.allFolders == []:
            self.showMessage()

        if self.folders_pinned == []:
            self.pushUpward()

        # Final touches, call the responser to position the cards accurately, if it's not
        self.responser(None)

        # End of the function by returning True
        return True

    def pushUpward(self) -> True:
        """
        Pushes up the folders and the header text if no folders are pinned.

        Args:
            return_on_creation (bool): Return immediately after showing the message, means, do not move up the folders.
        """

        # Create the message label
        self.info = QLabel(
            text="  No Folders Pinned. Double Click On The Folder To Pin",
            parent=self.window,
        )

        # Set geometry
        self.info.setGeometry(QRect(100, 200, 1980, 100))

        # Set set styles
        self.info.setStyleSheet(
            """
            QLabel{
                font-size: 25px;
                color: #4C566A;
            }                        
        """
        )

        # Show the info
        self.info.show()

        # Create a parallel animation
        self.animations = QParallelAnimationGroup()

        try:
            self.animations.addAnimation(
                Animation.movingAnimation(
                    Animation,
                    self.folderHeaderText,
                    QPoint(
                        self.folderHeaderText.pos().x(),
                        self.folderHeaderText.pos().y() + 1,
                    ),
                    400,
                )
            )
        except:
            pass

        # Iterate through all the folders to move them up
        for i in self.allFolders:
            self.animations.addAnimation(
                Animation.movingAnimation(
                    Animation, i, QPoint(i.pos().x(), i.pos().y() - 200), 400
                )
            )

        # Start the parallel animation
        self.animations.start()

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

        # Get the first image available in the dir which will be used as a cover
        image = self.get_first(dir)

        # If no images exit, it wont worth to show the card, so send the response as False
        if image is None:
            return False

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

        # Set the Alignment
        imageArea.setAlignment(Qt.AlignCenter)

        # Set fixed width and height
        imageArea.setFixedHeight(height - 52)

        imageArea.setFixedWidth(width - (int(border) * 2))

        # Move a little bit aside for showing the border
        imageArea.move(QPoint(int(border), int(border)))

        imageArea.setPixmap(QPixmap(image))

        # Prevent overflowing of the pixmap
        imageArea.setScaledContents(True)

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
        folderName.setText(dir[dir.rindex("/") + 1 :])

        # Move the card yo the desired postion
        label.move(QPoint(x, y))

        # Show the card
        label.show()

        # Set a property of the card with a value as the directory, will help while pinning
        label.setProperty("directory", dir)

        # Move to the next page (which shows all the available images in a folder)
        label.clicked.connect(lambda: self.transfer_control(dir))

        # Check if the directory is in pinned folder
        if is_pinned == False:
            # If it is not, call the addToPin function on click
            label.doubleClicked.connect(partial(self.addToPinned, label))

            self.allFolders.append(label)

        else:
            self.folders_pinned.append(label)

            # Else, call the removeFromPin function
            label.doubleClicked.connect(partial(self.removeFromPin, label))

        # Return True, nothing is better than that XD
        return True

    def get_first(self, dir: str) -> str:
        """Returns the first image in the folder, or None if no image is available

        Args:
            dir (str): [description]

        Returns:
            str: [description]
        """

        # Iterate through all the files and folders in the directory
        for i in os.listdir(dir):

            # Check if the image is a supported one
            if i[-3:] in ["png", "jpeg", "jpg", "webp"] and not os.path.isdir(
                "{}/{}".format(dir, i)
            ):
                return "{}/{}".format(dir, i)

        return None

    def removeFromPin(self, dir: str) -> None:
        """Removes a directory from the pinned Folders

        Args:
            dir (str): The Path Of the directory
        """

        # Init a Parallel Animation Class
        self.remove_pinning_animation = QParallelAnimationGroup()

        self.remove_pinning_animation.addAnimation(
            Animation.movingAnimation(
                Animation, dir, QPoint(40, self.folderStartValue), 200
            )
        )

        # Start the animation
        self.remove_pinning_animation.start()

        # Remove the directory from the pinned card's list
        if dir in self.folders_pinned:
            self.folders_pinned.remove(dir)

        # Add the folder to the folder's list
        self.allFolders.append(dir)

        # Remove the directory from the written file
        self.remove(dir.property("directory"))

        # Connect to a new function
        dir.doubleClicked.disconnect()

        dir.doubleClicked.connect(partial(self.addToPinned, dir))

        # Check if the pinned folder's become empty. If yes, push all the folders up
        if self.folders_pinned == []:
            self.pushUpward()

        # Add finishing touches
        self.responser(None)

    def addToPinned(self, dir: QDoublePushButton):
        """Add a directory to the pinned Folders

        Args:
            dir (str): The Path Of the directory
        """
        # Create a parallel animation
        self.pinning_animations = QParallelAnimationGroup()

        # If there are not folder's pinned, then push down the folders inorder to create space for the pinned folders
        if self.folders_pinned == []:
            self.pushDown()
        else:
            self.hide_msg()

        self.pinning_animations.addAnimation(
            Animation.movingAnimation(Animation, dir, QPoint(40, 220), 200)
        )

        self.pinning_animations.start()

        # Remove the directory from the folder's list
        if dir in self.allFolders:
            self.allFolders.remove(dir)

        # If the folder become's empty, meaning that all the folders are pinned, display the text
        if self.allFolders == []:
            self.showMessage()

        # Add the new directory to the pinned files's list (in the data file)
        self.addToPin(dir.property("directory"))

        # Add to pinned folders
        self.folders_pinned.insert(0, dir)

        # Reconnect with a new function
        dir.doubleClicked.disconnect()

        dir.doubleClicked.connect(partial(self.removeFromPin, dir))

        try:
            self.info.hide()
        except:
            pass

        # Finishing Touches
        self.responser(None)

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

        # Otherwise hide the info
        else:
            try:
                self.info.hide()
            except:
                pass

        # Set the start value
        self.folderStartValue = 580

        # Check how many cards can fit in one line
        self.per_line = max((self.main_window.width() - 200) // card_width, 1)

        # Check if the folders and pinned folders are render, otherwise, it will not worth setting up the new postion (most probably give me an error).
        try:
            self.pinnedLength = len(self.allFolders)

            self.foldersLength = len(self.folders_pinned)
        except:
            pass

        # Get the height that the pinned folders will use
        height = ceil(len(self.folders_pinned) / self.per_line)

        # Set the folder's start value according to the height
        self.folderStartValue = (card_height + padding) * height

        # New x and y positions
        x, y = 40, 220

        # Create a parallel animation group
        self.an = QParallelAnimationGroup()

        # Iterate through all the folders and pinned folders
        for i in self.folders_pinned:
            self.an.addAnimation(
                Animation.movingAnimation(Animation, i, QPoint(x, y), 200)
            )

            # Update x and y positions
            x += card_width + padding

            if x > self.main_window.width() - 270:
                x = 40

                y += card_height + padding

        # Create a animation for the header if it is available
        try:
            self.an.addAnimation(
                Animation.movingAnimation(
                    Animation,
                    self.folderHeaderText,
                    QPoint(40, self.folderStartValue + 300),
                    100,
                )
            )

        except:
            pass

        # Create new x and y positions according to the height being used by the pinned folders
        x, y = 40, 580 + ((card_height + padding) * (height - 1))

        for i in self.allFolders:
            self.an.addAnimation(
                Animation.movingAnimation(Animation, i, QPoint(x, y), 100)
            )

            # Update x and y
            x += card_width + padding

            if x > self.main_window.width() - 250:
                x = 40

                y += card_height + padding

        # Check if the msg exists
        try:
            self.an.addAnimation(
                Animation.movingAnimation(
                    Animation, self.msg, QPoint(100, self.folderStartValue + 380), 100
                )
            )
        except:
            pass

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
            text="Nothing Here  ! Probably You Have Pinned All The Folders Or Didn't Select Any Folder",
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

        self.effects.addAnimation(
            Animation.fadingAnimation(Animation, self.pinned, 400)
        )

        self.effects.start()

        # Run second slot of animations
        self.effects.finished.connect(lambda: self.run_second(directory))

    def run_second(self, dir):
        self.folderHeaderText.hide()

        self.label_to_change.setText(dir[dir.rindex("/") + 1 :])

        Animation.fadingAnimation(Animation, self.label_to_change, 400, True).start()

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

        singleFolderView(
            self.window,
            dir,
            self.config,
            self.scroll,
            self.main_window,
            self.label_to_change,
            self.images,
            self.folderHeaderText,
            self.pinned,
            *self.args
        ).start()


# So finally, I am done adding comments and helps in this file, It was lot. I am tired! 
