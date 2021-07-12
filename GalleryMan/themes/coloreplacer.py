from PIL import Image

class ColorReplacer:
    def __init__(self , image , rgb) -> None:
        self.image = image
        self.rgb = rgb
        
    def create_new(self , r , g , b):
        return (g , r , b)
                
    def convert(self):
        self.rgb = tuple(list(self.rgb) + [85])
        
        first = Image.open(self.image)
        
        second = Image.new("RGBA" , size=first.size , color=self.rgb)
        
        first.paste(second , (0 , 0) , second.convert("RGBA"))
    
        return first

# colors = [
#     "2E3440",
#     "3B4252",
#     "434C5E",
#     "4C566A",
#     "D8DEE9",
#     "E5E9F0",
#     "ECEFF4",
#     "8FBCBB",
#     "88C0D0",
#     "81A1C1",
#     "5E81AC",
#     "BF616A",
#     "D08770",
#     "EBCB8B",
#     "A3BE8C",
#     "B48EAD",
# ]

        

# colors = [
#     "2E3440",
#     "3B4252",
#     "434C5E",
#     "4C566A",
#     "D8DEE9",
#     "E5E9F0",
#     "ECEFF4",
#     "8FBCBB",
#     "88C0D0",
#     "81A1C1",
#     "5E81AC",
#     "BF616A",
#     "D08770",
#     "EBCB8B",
#     "A3BE8C",
#     "B48EAD",
# ]
