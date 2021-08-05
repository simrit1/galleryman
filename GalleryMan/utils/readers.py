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

def getFontNameFromFile(path):
    font = ttLib.TTFont(path)

    FONT_SPECIFIER_NAME_ID = 4
    
    FONT_SPECIFIER_FAMILY_ID = 1
    
    name = ""
    
    family = ""
    
    for record in font['name'].names:
        if b'\x00' in record.string:
            name_str = record.string.decode('utf-16-be')
        else:   
            name_str = record.string.decode('latin-1')
        if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
            name = name_str
        elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family: 
            family = name_str
        if name and family: break
    
    return name, family
