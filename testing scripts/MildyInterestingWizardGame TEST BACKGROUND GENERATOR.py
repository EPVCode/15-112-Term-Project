# information referenced from https://pillow.readthedocs.io/en/stable/index.html

def ptc(x,y):
    print(f'{x}: {y}')

gradient = 3

def ground():
    from PIL import Image, ImageDraw, ImageFont
    boxSize = 50
    windowWidth = 2000
    windowHeight = boxSize * 7
    backgroundWidth = windowWidth
    backgroundHeight = windowHeight
    background_1 = Image.new("L", (backgroundWidth,backgroundHeight),75)
    background_2 = ImageDraw.Draw(background_1)
    rows = int(backgroundHeight//boxSize)
    ptc('rows', rows)
    cols = int(backgroundWidth//boxSize)
    ptc('cols', cols)
    box_X = 0
    box_Y = 0
    fill = 0
    for row in range(0,rows):
        if(row%2 == 0):
            boxOffset=  boxSize
        else:
            boxOffset = 0
        for col in range(0,cols,2):
            background_2.rectangle([(box_X+boxOffset),box_Y,
                                    (box_X+boxOffset+boxSize),
                                    (box_Y+boxSize)],fill=fill, 
                                    outline=None, width=1)
            box_X+=(boxSize*2)
            fill += gradient
        fill = 0
        box_X = 0    
        box_Y+=boxSize
    box_X = 0
    box_Y = 0
    font = ImageFont.truetype('arial', boxSize/3)
    for row in range(0,rows,2):
        y = int(boxSize/2)+row*boxSize
        for col in range(0,cols):
            x = int((col*boxSize)+boxSize/2)
            background_2.text((x,y), f'{row}-{col}', fill=150, font = font, anchor = 'mm')
    background_1.show()
    background_1.save('images/ground/TEST_ground_1.png')
    background_1.close

def background():
    from PIL import Image, ImageDraw, ImageFont
    boxSize = 125
    windowWidth = boxSize * 20
    windowHeight = boxSize * 11
    backgroundWidth = windowWidth
    backgroundHeight = windowHeight
    background_1 = Image.new("L", (backgroundWidth,backgroundHeight),255)
    background_2 = ImageDraw.Draw(background_1)
    rows = int(backgroundHeight//boxSize)
    ptc('rows', rows)
    cols = int(backgroundWidth//boxSize)
    ptc('cols', cols)
    box_X = 0
    box_Y = 0
    fill = 0
    for row in range(0,rows):
        if(row%2 == 0):
            boxOffset=  boxSize
        else:
            boxOffset = 0
        for col in range(0,cols,2):
            background_2.rectangle([(box_X+boxOffset),box_Y,
                                    (box_X+boxOffset+boxSize),
                                    (box_Y+boxSize)],fill=fill, 
                                    outline=None, width=1)
            fill += gradient
            box_X+=(boxSize*2)
        fill = 0
        box_X = 0    
        box_Y+=boxSize
    box_X = 0
    box_Y = 0
    font = ImageFont.truetype('arial', boxSize/3)
    for row in range(0,rows,2):
        y = int(boxSize/2)+row*boxSize
        for col in range(0,cols):
            x = int((col*boxSize)+boxSize/2)
            background_2.text((x,y), f'{row}-{col}', fill=150, font = font, anchor = 'mm')
    background_1.show()
    background_1.save('images/background/TEST_background_1.png')
    background_1.close

def midground():
    from PIL import Image, ImageDraw, ImageFont
    boxSize = 75
    windowWidth = boxSize * 24
    windowHeight = boxSize * 8
    backgroundWidth = windowWidth
    backgroundHeight = windowHeight
    background_1 = Image.new("L", (backgroundWidth,backgroundHeight),125)
    background_2 = ImageDraw.Draw(background_1)
    rows = int(backgroundHeight//boxSize)
    ptc('rows', rows)
    cols = int(backgroundWidth//boxSize)
    ptc('cols', cols)
    box_X = 0
    box_Y = 0
    fill = 0
    for row in range(0,rows):
        if(row%2 == 0):
            boxOffset=  boxSize
        else:
            boxOffset = 0
        for col in range(0,cols,2):
            background_2.rectangle([(box_X+boxOffset),box_Y,
                                    (box_X+boxOffset+boxSize),
                                    (box_Y+boxSize)],fill=fill, 
                                    outline=None, width=1)
            box_X+=(boxSize*2)
            fill+=gradient
        fill = 0
        box_X = 0    
        box_Y+=boxSize
    box_X = 0
    box_Y = 0
    font = ImageFont.truetype('arial', boxSize/3)
    for row in range(0,rows,2):
        y = int(boxSize/2)+row*boxSize
        for col in range(0,cols):
            x = int((col*boxSize)+boxSize/2)
            background_2.text((x,y), f'{row}-{col}', fill=150, font = font, anchor = 'mm')
    background_1.show()
    background_1.save('images/midground/TEST_midground_1.png')
    background_1.close

# ground()
background()
# midground()
