import sys
from fontTools import ttLib
from configparser import ConfigParser

def read_file(file_loc):
    
    with open(file_loc) as file:
        return file.read()
    
def change_with_config(stylesheet , config: ConfigParser = None , section: str = "folderPage"):
    
    if(config == None):
        config = ConfigParser()
        
        config.read("GalleryMan/config.ini")
        
    stylesheet = stylesheet.format(
        backgroundColor=config.get(section , "background-color"),
        lolcat=config.get(section , "headerText-color"),
        headerFontFamily=config.get(section , "headerText-fontFamily"),
        headerFontSize=config.get(section , "headerText-fontSize") + "px"
    )
    
    return [stylesheet , config]
