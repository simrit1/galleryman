from genericpath import isdir
from .initer import bcolors
import os
import inquirer
import shutil


class stickerManager:
    def __init__(self):
        pass
    
    def createNew(self):
        print(bcolors.OKCYAN + "\n:: Enter the name of the new sticker pack: " , end="")
        
        name = input()
        
        newDir = os.path.join(os.path.expanduser("~") , ".galleryman" , "stickers" , name)
        
        os.makedirs(newDir)
        
        print(bcolors.OKCYAN + "\n::" , bcolors.HEADER + "Created an empty sticker set at {}".format(newDir) )
        
    def addToExisting(self , path):
        dirs = []
        
        stickerDir = os.path.join(os.path.expanduser("~") , ".galleryman" , "stickers")
        
        for dir in os.listdir(stickerDir):
            if(os.path.isdir(os.path.join(stickerDir , dir))):
                dirs.append(dir)
         
        sticker = [inquirer.List(
            "dir",
            bcolors.OKCYAN + bcolors.HEADER + "Select A Sticker Set" ,
            dirs)]
    
        res = inquirer.prompt(sticker)["dir"]
        
        print(bcolors.OKCYAN , "::" , bcolors.HEADER , "Adding sticker to the pack {}".format(res))
        
        shutil.copyfile(os.path.join(os.getcwd() , path) , os.path.join(os.path.expanduser("~") , ".galleryman" , "stickers" , res , path))
        
        print(bcolors.OKCYAN , "\n ::" , bcolors.OKGREEN , "Successfully added to the pack!")
        
    def deletePack(self):
        
        stickerDir = os.path.join(os.path.expanduser("~") , ".galleryman" , "stickers")
        
        dirs = []
        
        for dir in os.listdir(stickerDir):
            if(os.path.isdir(os.path.join(stickerDir , dir))):
                dirs.append(dir)
         
        sticker = [inquirer.List(
            "dir",
            bcolors.OKCYAN + bcolors.HEADER + "Select A Sticker Set To Remove" ,
            dirs)]
    
        dir = inquirer.prompt(sticker)["dir"]
        
        print(bcolors.OKCYAN , "\n ::" , bcolors.WARNING , "Are you sure (Y/n): " , end="")
        
        res = input()
        
        if(res in ["" , "y" , "yeah" , "yes" , "indeed"]): 
            shutil.rmtree(os.path.join(os.path.expanduser("~") , ".galleryman" , "stickers" , dir))
            
            print(bcolors.OKCYAN , "\n ::" , bcolors.OKGREEN , "Successfully deleted the sticker pack ({})".format(dir) , end="")
            
        else:
            
            print(bcolors.OKCYAN , "\n ::" , bcolors.FAIL , "Cancelled by the user, Aborting...." , end="")