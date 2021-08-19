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
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Welcome to GalleryMan!" + bcolors.ENDC))
                
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Initing GalleryMan... Please Wait" + bcolors.ENDC))
            
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Creating files..." + bcolors.ENDC))
                
        with open(os.path.join(os.path.expanduser("~") , ".config" , "galleryman" , "config.ini") , "w") as f:
            with open(os.path.join("GalleryMan" , "config.ini")) as sample:    
                f.write(sample.read())
        
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.HEADER + "Config file is located at {}".format(os.path.join(os.path.expanduser("~") , ".config" , "galleryman" , "config.ini")) + bcolors.ENDC))
        
        
        for files in [os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "trashLogs.txt")]:
            with open(files , "w") as file:
                pass
        
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Completed! Run `galleryman` to start the application" + bcolors.ENDC))
    