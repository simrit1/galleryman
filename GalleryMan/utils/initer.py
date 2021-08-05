import subprocess
import sys
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Initer:
    def __init__(self) -> None:
        pass
    
    def init(self):
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "::" + bcolors.ENDC , bcolors.OKGREEN + "Welcome To GalleryMan!" + bcolors.ENDC))
        
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Initing GalleryMan... Please Wait" + bcolors.ENDC))
        
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Checking if all modules are installed..." + bcolors.ENDC))
        
        for module in ["pyqt5" , "pillow" , "numpy"]:
            self.tryToDownload(module)
        
    def tryToDownload(self , module):
        try:
            __import__(module)
            
            print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "{} is downloaded".format(module) + bcolors.ENDC))
        except:
            res = input("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.WARNING + "You havn't installed {} yet. Do you want to install (Y/n)? ".format(module) + bcolors.ENDC))
            
            if(res.lower() in ["yes" , "yeah" , "y" , "yup" , ""]):
                print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.WARNING + "Installing {}. Please Wait (It may take some time depending upon the speed)".format(module) + bcolors.ENDC))

                subprocess.check_call([sys.executable, "-m", "pip", "install", module] , stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)