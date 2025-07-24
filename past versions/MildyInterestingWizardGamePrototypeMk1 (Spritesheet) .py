from cmu_graphics import *
from PIL import Image
import pyautogui as pygui
import os

#sets the first player sprite image to be displayed
app.playerSpriteIndex = [0,0]
app.previousPlayerSpriteIndex = [-1,-1]

app.blah = 0

#test debuggy thing
app.playerImageFileNumber = 1

#getting screen size of device
screenWidth, screenHeight = pygui.size()
windowScale = 0.5 # set to 0.5 for debugging purposes, but will be set to 1 
                  # by default for the final version

# My beloved print to console function (shortened to ptc)
def ptc(x,y):
    print(f'{x}: {y}')

#establishing screen width
app.windowWidth = int(screenWidth*windowScale)
app.windowHeight = int(screenHeight*windowScale)

def updatePlayerImage(app):

    # to prevent needlessly running slow PIL image processing procedures
    # the player sprite will only be changed if a different player sprite
    # index is called for
    if(app.playerSpriteIndex != app.previousPlayerSpriteIndex):

        ptc("playerSpriteIndex",app.playerSpriteIndex)

        # size of the sprite images in the spritesheet5
        playerSpriteWidth = 500
        playerSpriteHeight = 500
        playerScale = 0.25
        playerWidth = int(playerSpriteWidth*playerScale)
        playerHeight = int(playerSpriteHeight*playerScale)
        
        #using PIL to open the spritesheet image
        spritesheetDirectory = 'images/player/WizardSpritesheetMk1.png'
        playerSpritesheet = Image.open(spritesheetDirectory, 'r')

        # the currently desired sprite image within the spritesheet will be 
        # indicated using the list spriteIndex = [x,y] where x represents the 
        # column of the spritesheet in which our desired image resides, and y 
        # representes the row of the spritesheet in which our desired image
        # resides. Rows and columns START AT 0  

        # topleft coordinate of desired sprite image in the spritesheet 
        playerSpriteX = app.playerSpriteIndex[0]*playerSpriteWidth
        playerSpriteY = app.playerSpriteIndex[1]*playerSpriteHeight

        # setting the current player image to display by using PIL to crop
        # it from the larger spritesheet 
        playerImage = playerSpritesheet.crop((playerSpriteX,playerSpriteY,(playerSpriteX+playerSpriteWidth)
                                            ,(playerSpriteY+playerSpriteHeight)))
        playerSpritesheet.close
        # resizing image using pillow. Resampling method is NEAREST NEIGHBOR
        # because it is the fastest.
        playerImage = playerImage.resize((playerWidth,playerHeight),
                                        Image.Resampling.NEAREST)
        
        # I need to continuously change the name of the file that I am saving
        # to make sure that it updates and redrawAll displays the new file
        playerImage.save(f'images/PlayerImage{app.playerImageFileNumber}.png')
        playerImage.close()


        #updates what player image to show
        app.playerImage = f'images/PlayerImage{app.playerImageFileNumber}.png'
        # gives the player the coordinates to place them in the middle of the screen
        app.playerX = (app.windowWidth-playerWidth)/2
        app.playerY =  (app.windowHeight-playerHeight)/2
        # updates the previous player sprite index
        app.previousPlayerSpriteIndex = app.playerSpriteIndex
        # making sure that app.playerImageFileNumber doesnt endlessly increase
        # and making sure that can keep creating new image files
        if(app.playerImageFileNumber == 2):
            if os.path.exists('images/PlayerImage1.png'):
                os.remove('images/PlayerImage1.png')
            app.playerImageFileNumber = 1
        else:
            if os.path.exists('images/PlayerImage2.png'):
                os.remove('images/PlayerImage2.png')
            app.playerImageFileNumber = 2

        # ok it's 4:00 AM and I going to bed but here's the problem I have yet
        # to solve: It seems that redrawALL has persistenent memory. If I ask 
        # it to draw 'playerImage1' it will always draw the very first thing
        # it acessed using 'playerImage1' regardless of whether or not 
        # 'playerImage1' has been updated or not. I tried telling it to draw 
        # 'playerImage1', and then draw 'playerImage2' and delete 'playerImage1'
        # then resave a new picture as 'playerImage1', and draw that new 
        # picture for 'playerImage1', but it doesn't change what it draws. 
        # it always draws the first thing it drew when asked to draw 
        # 'playerImage1'. I don't know if this is a problem with python itself?
        # I mean it seems if I literally delete playerImage1 and resave it
        # then it MUST be updated??? Maybe it's just an issue with how 
        # cmu_graphics works. If that is the case, and it's not some silly 
        # file state issue im running into, then it seems the only way I can 
        # display a bunch of different images is by saving every single sprite
        # as a seperate image, instead of parsing through my sprite sheet. 
        # that would suck, and I don't want to do that. 
        # Could I perhaps just circumvent the whole "needing to save my images"
        # thing overall, and just pass image data directly into cmu_graphics
        # to be drawn instead of having to give it the file directory???
        # Alternatively, maybe I could use the whole sprite thing that
        # cmu_graphics has. It seems that that supports animations better
        # than just having to pass different images in all the time. 
        # I really wanted to use the whole sprite sheet idea :(
        
    # heyo, 4:55 Eddy here, after thinking about it I realized that the process 
    # of: opening the spritesheet file, cropping the image, saving the cropped
    # image as a seperate file, and then displaying that saved image, all just
    # completely negate the benefit of using a spritesheet in the first place. 
    # the reason a spritesheet is good is because it lets you display a bunch 
    # of different sprites without having to open a new file for every image
    # because it doesnt seem like I can dynamically crop an image using 
    # redrawAll, I am stuck accessing a new image for every diferent sprite
    # i want to display. It effectively makes using a spritesheet impossible. 
    # or at least it does to my knowledge. That said, my method of going through
    # the sprite sheet to find an image, resaving it, and then displaying that
    # new saved image is defininitely not worth the added time and complexity.
    # I am just going to save every individual sprite as a different file and 
    # access those instead. No need for costly PIL image editing. 
    
updatePlayerImage(app) #runs once prior to starting just to make sure that
                       #redrawAll does not break


def onMousePress(app, mouseX, mouseY, button): #little test thing to see if updatePlayerImage works
    print('kablooie')
    app.blah +=1
    app.playerSpriteIndex = [app.blah, 0]

def onStep(app):
    updatePlayerImage(app)

def redrawAll(app):
    drawImage(app.playerImage,app.playerX,app.playerY)

runApp(width = app.windowWidth, height = app.windowHeight)

# Eduardo Phelan-Vidal
# Last Updated: 5:05 AM - 6/29/2025