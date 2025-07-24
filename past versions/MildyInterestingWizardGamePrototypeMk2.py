# Name: Eduardo Phelan-Vidal
# AndrewID: esphelan
# Section: A

# INCORPORATE CLORB (CASTING LASER ORB) (spells generate from there)
# after you beat the boss you get the golden golf cart to ride around

from cmu_graphics import *
# I only use os to delete files, or detect if a file exists
import os  
# I only use sys for the sys.exit() feature, which I have found to be a clean 
# way to exit the program after an error occurs
import sys 
# I use PIL for image cropping and resizing
from PIL import Image
import math

# My beloved PrintToConsole function (shortened to ptc)
def ptc(x,y):
    print(f'{x}: {y}')

# small list rotation helper function
def rotateList(list,rotations):
    return list[rotations:]+list[0:rotations]

def playerAnimationAltitudeCheck(app):
    if(app.yOffset['ground'] > 0):
        return 'air'
    else: 
        return 'ground'

# helper function to detect two numbers are the same sign
def sameSign(a,b):
    if(a >= 0):
        signA = 1
    else:
        signA = -1
    if(b >= 0):
        signB = 1
    else:
        signB = -1
    return(signA == signB)

# reporting errors to console and ending the program
def reportError(process, errorName, function, faultType, fault, 
                additionalMessage):
    print('')
    print(f'⚠  Error encoutered while {process}')
    print(f'⚠  Error: {errorName}')
    print(f'⚠  Function: {function}')
    print(f'⚠  {faultType}: {fault}')
    if(additionalMessage != None):
        print(f'⚠  {additionalMessage}')
    print('')
    # making the program crash after error is found, avoiding logical errors
    sys.exit()  

def interpretPlayerImageIndex(app,indexToInterpret):

    # PLAYER IMAGE ENCODING KEY
    # The desired player image will be indicated according to the following 
    # list: app.playerImageIndex = [a,b,c] with following distinctions:
    # --- a ---
    # a indicates the DIRECTION that the player is facing 
    # a = 0 indicates that the player is facing RIGHT
    # a = 1 indicates that the player is facing LEFT
    # --- b ---
    # b indicates the current MOTION that the player is engaging in
    # b = 0 indicates that the player is STANDING
    # b = 1 indicates that the player is RUNNING
    # b = 2 indicates that the player is SLIDING
    # (this list will be UPDATED as more movements are added)
    # --- c ---
    # c indicates the CURRENT FRAME OF ANIMATION that the player is on
    # c = -1 indicates that the player is NOT on a frame of an animation
    # c = 0 indicates that the player is on the FIRST frame of an animation
    # c = 1 indicates that the player is on the SECOND frame of an animation
    # and so on...

    # Dropdown to hide everything but the
    if(indexToInterpret == 0):
        if(app.playerImageIndex[0] == 0):
            return 'right' # FACING should NOT be capitalized
        elif(app.playerImageIndex[0] == 1):
            return 'left'
        else:
            reportError('interpreting playerFacing value', 
                        'INVALID VALUE RECIEVED','interpretPLayerImageIndex', 
                        'Value', app.playerImageIndex[0],None)
    elif(indexToInterpret == 1):
        if(app.playerImageIndex[1] == 0):
            return 'Stand' # MOTION SHOULD be capitalized
        elif(app.playerImageIndex[1] == 1):
            return 'Run'
        elif(app.playerImageIndex[1] == 2):
            return 'Slide'
        else:
            reportError('interpreting playerMotion value', 
                        'INVALID VALUE RECIEVED', 'interpretPLayerImageIndex', 
                        'Value', app.playerImageIndex[1],None)
    elif(indexToInterpret == 2):
        if(app.playerImageIndex[2] == -1):
            return '' # FRAME should be a number or an empty string
        elif(app.playerImageIndex[2] > -1):
            return (f'_{app.playerImageIndex[2]}')
        else:
            reportError('interpreting playerAnimationFrame value', 
                        'INVALID VALUE RECIEVED', 'interpretPLayerImageIndex', 
                        'Value', app.playerImageIndex[2], None)
    else:
        reportError('interpreting playerImageIndex', 
                        'INVALID INDEX', 'interpretPLayerImageIndex', 
                        'app.playerImageIndex has no index', 
                        f'[{indexToInterpret}]', None)

def interpretPlayerState(app):
        # 'Locking' animations, which are those for which the direction cannot
        # be immediately changed by pressing the arrow keys, take priority
        # over directional indication
    if(app.playerState == 'slide'):
        app.playerAnimationCounter += 1
        # print(app.playerAnimationCounter)
        # the number 5 here is an adjustable timing constant that is tuned by 
        # hand such that the slide animation plays at an appropriate speed
        if((app.playerAnimationCounter % 3) == 0):
            app.playerImageIndex[2] += 1
            if(app.playerImageIndex[2] == 3): 
                # there are only three frames of the sliding animation
                app.playerState = playerAnimationAltitudeCheck(app)
                # print('slide animation over')
                # ptc('app.playerState',app.playerState)
    else:
        app.playerState = playerAnimationAltitudeCheck(app)
    if(app.playerFacing == 'right'):
        app.playerImageIndex[0] = 0
    else:
        app.playerImageIndex[0] = 1
    if(app.playerState == 'ground'):
        app.playerWingCounter = 0
        app.gravity = 0

        if(abs(app.currentPlayerXVelocity) > 1):
            if((not sameSign(app.currentPlayerXVelocity,
                              app.currentPlayerXThrust)) and 
                              (app.currentPlayerXThrust != 0)): 
                               # 90% of max velocity
                app.playerState = 'slide'
                # print('in slide mode')
                app.playerAnimationCounter = 0
                app.playerImageIndex[1] = 2
                app.playerImageIndex[2] = 0
            elif(app.playerImageIndex[1] == 1):
                if(app.playerAnimationCounter > 100000):
                    app.playerAnimationCounter = 0  
                # print(21-int(abs((app.currentPlayerXVelocity))))
                # ptc('app.playerAnimationCounter',app.playerAnimationCounter)
                if((app.playerAnimationCounter % 
                    (abs((int(abs(app.currentMaxPlayerXVelocity)))-
                         int(abs((app.currentPlayerXVelocity))))+1) == 0)):
                    app.playerImageIndex[2] += 1
                    # ptc('app.playerImageIndex[2]',app.playerImageIndex[2])
                    if(app.playerImageIndex[2] == 5): # six frames in animation
                        app.playerImageIndex[2] = 0
                app.playerAnimationCounter += 1
            else:
                app.playerAnimationCounter = 0
                app.playerImageIndex[1] = 1
                app.playerImageIndex[2] = 0 
        else:
            app.playerAnimationCounter = 0
            app.playerImageIndex[2] = -1
            app.playerImageIndex[1] = 0
    if(app.playerState == 'air'):
        app.playerImageIndex[2] = -1
        app.playerImageIndex[1] = 0
        app.gravity = app.setGravity

def updatePlayerImage2(app):
    # ---- FROM MK1 (Spritesheet) ----
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
    # ---------------------------------------------------------------------        
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
    
    playerSpriteWidth = 500 # width of actual player sprite image
    playerSpriteHeight = 500 # height of actual player sprite image
    playerScale = 0.25
    app.playerWidth = int(playerSpriteWidth*playerScale)
    app.playerHeight = int(playerSpriteHeight*playerScale)
    app.playerX = (app.windowWidth-app.playerWidth)/2
    app.playerY =  (app.windowHeight-app.playerHeight)/2

    interpretPlayerState(app)
    
    playerFacing = interpretPlayerImageIndex(app,0)
    playerMotion = interpretPlayerImageIndex(app,1)
    playerAnimationFrame = interpretPlayerImageIndex(app,2)
        
    #setting Player Image Path
    playerImageName = (f'{playerFacing}{playerMotion}{playerAnimationFrame}')
    testPlayerImagePath = (f'images/player/{playerImageName}.png')
    
    # Assigning Player Image Path and returning an error if it is invalid
    if os.path.exists(testPlayerImagePath):
        app.playerImage = (f'images/player/{playerImageName}.png')
    else:
        reportError('accessing desired player image file', 
                    'IMAGE COULD NOT BE FOUND', 'UpdatePlayerImage2', 
                    'File name', (f'images/{playerImageName}.png'), None)
  
def updatePlayerVelocity(app):

    if(abs(app.currentPlayerXVelocity) < 0.01):
        app.previousPlayerXVelocity = 0
    app.currentPlayerXAcceleration = ((app.currentPlayerXThrust + 
                      ((app.playerXFrictionConstant) * 
                       (app.previousPlayerXVelocity))) / 
                       ((app.playerMass) - (app.playerXFrictionConstant)))
    app.currentPlayerXVelocity = ((app.currentPlayerXAcceleration) + 
                                  (app.previousPlayerXVelocity))
    app.previousPlayerXVelocity = app.currentPlayerXVelocity
    app.currentPlayerXFrictionForce = ((app.playerXFrictionConstant)*
                                       (app.currentPlayerXVelocity))
    app.currentMaxPlayerXVelocity = (((app.currentPlayerXThrust)*
                                      (1-((app.playerMass)/
                                          (app.playerXFrictionConstant))))/
                                          ((app.playerMass)-
                                           (app.playerXFrictionConstant)))
    if(((app.currentPlayerXVelocity - app.currentMaxPlayerXVelocity) < 0.01) and
        (abs(app.currentPlayerXAcceleration) < 0.01)):
            app.previousPlayerXVelocity = app.currentMaxPlayerXVelocity

    if((app.yOffset['ground'] > 0) or app.currentPlayerYThrust > 0):
        app.playerState = 'air'
        app.gravity = app.setGravity
        app.currentPlayerYAcceleration = ((app.currentPlayerYThrust + 
                                           app.gravity + 
                                           ((app.playerYFrictionConstant) * 
                                            (app.previousPlayerYVelocity))) / 
                                            ((app.playerMass) - 
                                             (app.playerYFrictionConstant)))
        app.currentPlayerYVelocity = ((app.currentPlayerYAcceleration) + 
                                    (app.previousPlayerYVelocity))
        app.previousPlayerYVelocity = app.currentPlayerYVelocity
        app.currentPlayerYFrictionForce = ((app.playerYFrictionConstant)*
                                        (app.currentPlayerYVelocity))
        app.currentMaxPlayerYVelocity = (((app.currentPlayerYThrust)*
                                        (1-((app.playerMass)/
                                            (app.playerYFrictionConstant))))/
                                            ((app.playerMass)-
                                            (app.playerYFrictionConstant)))
    else:
        app.currentPlayerYThrust = 0
        app.playerWingCounter = 0
        app.gravity = 0
        app.currentPlayerYVelocity = 0
        app.currentPlayerYAcceleration = 0
        app.previousPlayerYVelocity = 0
        app.currentPlayerYFrictionForce = 0
        for tileableImageName in ['background','midground','ground']:
            app.yOffset[tileableImageName] = 0

    speedMultiplier = 6 #temporary adjustment value
    for tileableImageName in ['background','midground','ground']:
        app.xOffset[tileableImageName] += ((app.currentPlayerXVelocity)*
                                           speedMultiplier)
    for tileableImageName in ['background','midground','ground']:
        app.yOffset[tileableImageName] += ((app.currentPlayerYVelocity)*
                                           speedMultiplier)
        
def updateTiles(app,tileableImage,tileWidth,tileableImageName,xOffset,
parallaxCoefficient):
    #applying parallax
    xOffset = int(xOffset/parallaxCoefficient)
    # ptc('parallaxCoefficient',parallaxCoefficient)
    # ptc('xOffset',xOffset)

    tileableImageWidth, tileableImageHeight = getImageSize(tileableImage)
    rows = int(tileableImageWidth/tileWidth)
    # setting the initial position of the image to be displayed
    if(tileableImageName == 'ground'): # the ground is displayed off center
        tileableImageX = (app.windowWidth-tileableImageWidth)/2
        tileableImageY = (((app.windowHeight-tileableImageHeight)/2)+
        (app.windowHeight)/2.3)
    elif(tileableImageName == 'midground'): # the midground is displayed off 
                                            # center
        tileableImageX = (app.windowWidth-tileableImageWidth)/2
        tileableImageY = (((app.windowHeight-tileableImageHeight)/2)+
        (app.windowHeight)/6)
    elif(tileableImageName == 'background'): # the background is displayed off 
                                           # center
        tileableImageX = (app.windowWidth-tileableImageWidth)/2
        tileableImageY = (((app.windowHeight-tileableImageHeight)/2)-
        (app.windowHeight)/2.75)
    else: # center the image to be displayed in the screen
        tileableImageX = (app.windowWidth-tileableImageWidth)/2
        tileableImageY = (app.windowHeight-tileableImageHeight)/2
       
    # turning the integer rows into a list of the individual row valuesddd
    rowsList = []
    for row in range(rows):
        rowsList.append(row)

    # calculating if a tile needs to be swapped to the other side of the screen
    if(xOffset > 0):
        sign = 1
    else:
        sign = -1
    rowOffset = math.floor(abs(xOffset)/tileWidth)*sign
    # ptc('rowOffset',rowOffset)
    
    if(rowOffset > rows):
        rowOffset -= rows
        xOffset -= tileableImageWidth
    elif(rowOffset < -rows):
        rowOffset += rows
        xOffset += tileableImageWidth

    # rotating the list appropriately to scroll the tiles
    rowsList = rotateList(rowsList,rowOffset)

    applicableXOffset = xOffset-(rowOffset*tileWidth)
    initialTileXPosition = tileableImageX - applicableXOffset
    initialTileYPosition = tileableImageY + int(app.yOffset[tileableImageName]
                                         /parallaxCoefficient)

    # converting xOffset back to normal before returning it
    xOffset = xOffset*parallaxCoefficient

    app.rowsList[tileableImageName] = rowsList
    app.initialTileXPosition[tileableImageName] = initialTileXPosition
    app.initialTileYPosition[tileableImageName] = initialTileYPosition
    app.tileWidth[tileableImageName] = tileWidth
    app.xOffset[tileableImageName] = xOffset

def drawTiles(app,rowsList,currentTileXPosition,currentTileYPosition,tileWidth,
              tileableImageName):
    for row in rowsList:
        # only draw tiles if they are within the bounds of the screen
        if((app.screenLeft <= currentTileXPosition < app.screenRight) and 
           (currentTileYPosition < app.screenBottom)):
                tileableImageSavePath = (f'images/{tileableImageName}/'+
                                    f'{tileableImageName}Tile_{row}.png')
                # only draw tiles if their file can be accessed, otherwise 
                # report an error
                if os.path.exists(tileableImageSavePath):
                    drawImage(tileableImageSavePath,currentTileXPosition,
                            currentTileYPosition,opacity = app.opacity[tileableImageName])
                else:
                    reportError('accessing desired tile file', 
                                'IMAGE COULD NOT BE FOUND', 'drawTiles', 
                                'File name', (tileableImageSavePath), None)
        currentTileXPosition += tileWidth

def tileImage(app,tileableImage,tileWidth,tileableImageName):
    # TILEABLE IMAGE NAME SHOULD BE THE SAME NAME AS THE FOLDER THAT CONTAINS IT
    tileableImageWidth, tileableImageHeight = getImageSize(tileableImage)
    rows = int(tileableImageWidth/tileWidth)
    tileableImage = Image.open(tileableImage)
    cropXPosition = 0
    for row in range(rows):
        currentTile = tileableImage.crop((cropXPosition,0,
                                        cropXPosition+tileWidth,
                                        tileableImageHeight))
        tileableImageSavePath = (f'images/{tileableImageName}/'+
                                 f'{tileableImageName}Tile_{row}.png')
        if os.path.isdir(f'images/{tileableImageName}'):
            currentTile.save(tileableImageSavePath)
        else:
            reportError('saving tile from an image', 
                        'FOLDER COULD NOT BE LOCATED', 'tileImage', 
                        'Folder you are trying to save to',
                        (tileableImageName), None)
        currentTile.close()
        cropXPosition += tileWidth

def onKeyPress(app,key):
    if(key == '+'):
        app.testWalkSpeed += 10
    if(key == "-"):
        app.testWalkSpeed -= 10

def onKeyHold(app,keys):
    # X movement
    if(('d' in keys) or ('a' in keys)):
        if(('d' in keys) and ('a' in keys)):
            app.currentPlayerXThrust = 0
            app.playerXFrictionConstant = -10
        elif(('d' in keys) and (not('a' in keys))):
            app.playerFacing = 'right'
            if(app.playerState != 'slide'):
                app.currentPlayerXThrust = app.playerXThrust
                app.playerXFrictionConstant = -10
            else:
                app.currentPlayerXThrust = app.playerXThrust/10
                app.playerXFrictionConstant = -1
        else:
            app.playerFacing = 'left'
            if(app.playerState != 'slide'):
                app.currentPlayerXThrust = -app.playerXThrust
                app.playerXFrictionConstant = -10
            else:
                app.currentPlayerXThrust = -app.playerXThrust/10
                app.playerXFrictionConstant = -1
    # Y movement
    driftConstant = 35 # tuned to control how quickly the player falls after 
                       # they have stopped flying upwards
    if(('w' in keys) or ('s' in keys)):
        if(('w' in keys) and ('s' in keys)):
            if(app.yOffset['ground'] > 0):
                app.currentPlayerYThrust = -app.setGravity - driftConstant
            app.playerYFrictionConstant = -10
        elif(('w' in keys) and (not('s' in keys))):
            # value for player wing counter is manually set to determine
            # length for which wings can provide upwards lift
            maxPlayerWingCounter = 2500
            if(app.playerWingCounter < maxPlayerWingCounter):
                app.currentPlayerYThrust = (app.playerYThrust - 
                                            int((app.playerWingCounter / 
                                                 (maxPlayerWingCounter / 
                                                  10))**2)-app.setGravity)
                app.playerWingCounter += 50
            elif(app.yOffset['ground'] > 0):
                app.currentPlayerYThrust = -app.setGravity - driftConstant
            else: 
                app.currentPlayerYThrust = 0
            app.playerYFrictionConstant = -10
        else:
            if(app.yOffset['ground'] > 0):
                app.currentPlayerYThrust = -app.setGravity - driftConstant
            else: 
                app.currentPlayerYThrust = 0
            app.playerYFrictionConstant = -10

def onKeyRelease(app,key):
    if((key == 'a') or (key == 'd')):
        app.currentPlayerXThrust = 0
    if((key == 'w') or (key == 's')):
        app.currentPlayerYThrust = 0
        app.playerYFrictionConstant = -1

def onStep(app):
    updatePlayerImage2(app)
    for tileableImageName in ['background','midground','ground']:
        updateTiles(app, app.image[tileableImageName], 
                    app.tileWidth[tileableImageName], tileableImageName, 
                    app.xOffset[tileableImageName], 
                    app.parallaxCoefficient[tileableImageName])
    updatePlayerVelocity(app)

def tempDisplayReadout(app,inputList):
    buffer = 10
    lineSpacing = 20
    lineXPosition = 0 + buffer
    lineYPosition = app.windowHeight - buffer
    for i in range(0,len(inputList),2):
        displayText = f'{inputList[i]}: {inputList[i+1]}'
        drawLabel(displayText, lineXPosition, lineYPosition, 
              fill = 'white', border = "black", borderWidth = 1, opacity = 100, 
              rotateAngle = 0, align = 'left-bottom', visible = True, size = 20, 
              font = 'arial', bold = True, italic = False)
        lineYPosition -= lineSpacing

def redrawAll(app): 
    for tileableImageName in ['background','midground','ground']:
        drawTiles(app,app.rowsList[tileableImageName], 
                app.initialTileXPosition[tileableImageName],
                app.initialTileYPosition[tileableImageName],
                app.tileWidth[tileableImageName],tileableImageName)
    drawImage(app.playerImage, app.playerX, app.playerY, 
              width = app.playerWidth, height = app.playerHeight)
    # temporary readout for variables
    # tempDisplayReadout(app,['currentPlayerXAcceleration',
    #                         app.currentPlayerXAcceleration,
    #                         'currentPlayerXVelocity',
    #                         app.currentPlayerXVelocity, 
    #                         'currentPlayerXThrust',
    #                         app.currentPlayerXThrust, 
    #                         'previousPlayerXVelocity',
    #                         app.previousPlayerXVelocity,
    #                         'playerXFrictionConstant',
    #                         app.playerXFrictionConstant,
    #                         'currentPlayerXFrictionForce',
    #                         app.currentPlayerXFrictionForce,
    #                         'currentMaxPlayerXVelocity',
    #                         app.currentMaxPlayerXVelocity,
    #                         'currentPlayerYAcceleration',
    #                         app.currentPlayerYAcceleration,
    #                         'currentPlayerYVelocity',
    #                         app.currentPlayerYVelocity, 
    #                         'currentPlayerYThrust',
    #                         app.currentPlayerYThrust, 
    #                         'previousPlayerYVelocity',
    #                         app.previousPlayerYVelocity,
    #                         'playerYFrictionConstant',
    #                         app.playerYFrictionConstant,
    #                         'currentPlayerYFrictionForce',
    #                         app.currentPlayerYFrictionForce,
    #                         'currentMaxPlayerYVelocity',
    #                         app.currentMaxPlayerYVelocity,
    #                         'current ground YOffset',
    #                         app.yOffset['ground'],
    #                         'playerWingCounter',
    #                         app.playerWingCounter,
    #                         'current player state',
    #                         app.playerState])
       
def appSetup(app):

    # ---- WINDOW SETUP ----

    # establishing screen width
    app.windowWidth = 1000
    app.windowHeight = 750

    # setting the left and right bounds of the screen
    # should be set a little ways beyond the visible edge of the screen
    # to ensure tiles are displayed properly
    app.screenLeft = -130
    app.screenRight = app.windowWidth + 5
    app.screenTop = 0
    app.screenBottom = app.windowHeight

    # setting the background color
    app.background = "blue"

    # ---- TILEABLE IMAGE SETUP ----

    # establishing variable type dictionaries
    app.tileWidth = dict()
    app.image = dict()
    app.parallaxCoefficient = dict()
    app.xOffset = dict()
    app.yOffset = dict()
    app.rowsList = dict()
    app.initialTileXPosition = dict()
    app.initialTileYPosition = dict()
    app.opacity = dict()

    # establishing tiling widths - THESE ARE DETERMINED ACCORDING TO THE IMAGES
    # tiling heights will be added once vertical movement is possible
    app.tileWidth['background'] = 125
    app.tileWidth['midground'] = 75
    app.tileWidth['ground'] = 50

    # etablishes background and ground images to display
    app.image['background'] = 'images/background/TEST_background_1.png'
    app.image['midground'] = 'images/midground/TEST_midground_1.png'
    app.image['ground'] = 'images/ground/TEST_ground_1.png'
    
    # parallax coefficients change how much each tiled image moves for a 
    # change in xOffset
    app.parallaxCoefficient['background'] = 3
    app.parallaxCoefficient['midground'] = 2
    app.parallaxCoefficient['ground'] = 1

    # opacity determines how transparent one of the tileable images should be
    app.opacity['background'] = 100
    app.opacity['midground'] = 100
    app.opacity['ground'] = 100

    # split images into tiles and save the tiles as seperate images
    tileImage(app,app.image['background'],app.tileWidth['background'],
              'background')
    tileImage(app,app.image['midground'],app.tileWidth['midground'],
              'midground')
    tileImage(app,app.image['ground'],app.tileWidth['ground'],
              'ground')

    # setting initial position data to 0
    app.xOffset['background'] = 0
    app.yOffset['background'] = 0
    app.initialTileXPosition['background'] = 0
    app.initialTileYPosition['background'] = 0
    app.xOffset['midground'] = 0
    app.yOffset['midground'] = 0
    app.initialTileXPosition['midground'] = 0
    app.initialTileYPosition['midground'] = 0
    app.xOffset['ground'] = 0
    app.yOffset['ground'] = 0
    app.initialTileXPosition['ground'] = 0
    app.initialTileYPosition['ground'] = 0

    # setting initial row data to 0
    app.rowsList['background'] = 0
    app.rowsList['midground'] = 0
    app.rowsList['ground'] = 0

    # ---- PLAYER SETUP ----

    # sets first player image to show
    app.playerImageIndex = [0,0,-1]

    # intiates player physics parameters
    app.currentPlayerXThrust = 0
    app.currentPlayerXVelocity = 0
    app.previousPlayerXVelocity = 0
    app.currentPlayerXFrictionForce = 0
    app.currentPlayerXAcceleration = 0
    app.currentMaxPlayerXVelocity = 0
    app.currentPlayerYThrust = 0
    app.currentPlayerYVelocity = 0
    app.previousPlayerYVelocity = 0
    app.currentPlayerYFrictionForce = 0
    app.currentPlayerYAcceleration = 0
    app.currentMaxPlayerYVelocity = 0
    # the following parameters are tuned by feel, and cannot be determined
    # mathematically
    app.playerMass = 25
    app.playerXThrust = 100
    app.playerXFrictionConstant = -10
    app.playerYThrust = 100
    app.playerYFrictionConstant = -10
    app.setGravity = -75

    # indicates what state the player is in
    # current states: 'ground', 'air', 'slide', 'roll'
    app.playerState = 'ground'

    # indicates the direction the player is facing
    app.playerFacing = 'right'

    # intializes player counters to 0
    app.playerAnimationCounter = 0
    app.playerWingCounter = 0

    # ---- APP SETUP ----

    # setting the framerate
    app.stepsPerSecond = 30

    # ---- TEMP DEBUG ----

    # misc testing setup
    app.testWalkSpeed = 10
    # app.screenLeft = 100
    # app.screenRight = app.windowWidth - 100


    app.tempDebugReadout = 1 # set to 1 to enable readout, set to 0 to disable

    # Finalization - run the contents of appStep to update everything prior 
    # to running. DO NOT RUN onStep() ITSELF!
    updatePlayerImage2(app)
    for tileableImageName in ['background','midground','ground']:
        updateTiles(app, app.image[tileableImageName], 
                    app.tileWidth[tileableImageName], tileableImageName, 
                    app.xOffset[tileableImageName], 
                    app.parallaxCoefficient[tileableImageName])
    updatePlayerVelocity(app)

appSetup(app)
# initlization!
runApp(width = app.windowWidth, height = app.windowHeight)

# Last Updated: 3:23 PM - 7/05/2025
# total hours spent working here: 22