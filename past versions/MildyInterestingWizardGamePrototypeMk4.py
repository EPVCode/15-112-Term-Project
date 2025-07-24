# Name: Eduardo Phelan-Vidal
# AndrewID: esphelan
# Section: A

# TODO:
# INCORPORATE SPELL ORB - floats above player's head. offensive spells cast from
# the center of the orb rather than from the tip of the player's staff since 
# figuring out how to animate that is extremely difficult. Probably give it the 
# "player following" physics that the shadow orb has in terraria where it lags 
# behind slightly but eventually catches up
# DRAW BACKGROUNDS - I am TIRED of looking at checkerboard patterns
# DRAW FLYING ANIMATION - no more still levitating in the air
# WORK OUT FIRST COMBOS - figure out combo detection system, how to read keys
# PUT TOGETHER A PAUSE FEATURE

from cmu_graphics import *
# I only use os to delete files, or detect if a file exists
import os  
# I only use sys for the sys.exit() feature, which I have found to be a clean 
# way to exit the program after an error occurs
import sys 
# I use PIL for image cropping and resizing
from PIL import Image
import math
# numpy used for matrix transformations in lighting engine
import numpy
import copy

# intilaizing light soure class (does this need to be done globally?)
class lightSource:
        def __init__(self,spread,intensity,x,y,fadeRate):
            self.spread = spread
            self.intensity = intensity
            self.x = x
            self.y = y
            self.counter = 0
            self.fadeRate = fadeRate
        def fade(self):
            self.intensity *= self.fadeRate

# My beloved PrintToConsole function (shortened to ptc)
def ptc(x,y):
    print(f'{x}: {y}')

# small list rotation helper function
def rotateList(list,rotations):
    return list[rotations:]+list[0:rotations]

# small distance function using pythagorean theorem
def getDistance(x_1,y_1,x_2,y_2):
    return((((x_2-x_1)**2)+((y_2-y_1)**2))**0.5)

def playerAnimationAltitudeCheck(app):
    if(app.ti['ground'].yOffset > 0):
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
        # the number being modded by here is an adjustable timing constant 
        # that is tuned by hand such that the slide animation plays at an 
        # appropriate speed
        if((app.playerAnimationCounter % 3) == 0):
            app.playerImageIndex[2] += 1
            if(app.playerImageIndex[2] == 3): 
                # there are only four frames of the sliding animation
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
        if(abs(app.player['x'].currentVelocity) > 1):
            if((not sameSign(app.player['x'].currentVelocity,
                              app.player['x'].currentThrust)) and 
                              (app.player['x'].currentThrust != 0)): 
                               # 90% of max velocity
                app.playerState = 'slide'
                # print('in slide mode')
                app.playerAnimationCounter = 0
                app.playerImageIndex[1] = 2
                app.playerImageIndex[2] = 0
            elif(app.playerImageIndex[1] == 1):
                if(app.playerAnimationCounter > 10000):
                    app.playerAnimationCounter = 0  
                # print(21-int(abs((app.currentPlayerXVelocity))))
                # ptc('app.playerAnimationCounter',app.playerAnimationCounter)
                minimumTicksBetweenRunAnimationFrames = 2
                if((app.playerAnimationCounter % (abs((int(abs(app.player['x'].currentVelocity)))-int(abs((app.player['x'].currentMaxVelocity))))+minimumTicksBetweenRunAnimationFrames) == 0)):
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

def runPlayerVelocityCalculations(app,axis):
    # SHORTEN ONCE FINALIZED
    app.player[axis].currentAcceleration = (((app.player[axis].currentThrust)+(app.player[axis].gravity)+((app.player[axis].frictionConstant)*(app.player[axis].previousVelocity)))/((app.playerMass)-(app.player[axis].frictionConstant)))
    app.player[axis].currentVelocity = ((app.player[axis].currentAcceleration)+(app.player[axis].previousVelocity))
    app.player[axis].currentFrictionForce = ((app.player[axis].frictionConstant)*(app.player[axis].currentVelocity))
    app.player[axis].currentMaxVelocity = (((app.player[axis].currentThrust)*(1-((app.playerMass)/(app.player[axis].frictionConstant))))/((app.playerMass)-(app.player[axis].frictionConstant)))
    app.player[axis].previousVelocity = app.player[axis].currentVelocity

def updatePlayerVelocity(app):

    # handling X velocity

    # edge snapping to 0 velocity in x direction 
    if(abs(app.player['x'].currentVelocity) < 0.01):
        app.player['x'].previousVelocity = 0

    runPlayerVelocityCalculations(app,'x')

    # edge snapping to max velocity in edge direction
    if(((app.player['x'].currentVelocity - 
         app.player['x'].currentMaxVelocity) < 0.01) and 
         (abs(app.player['x'].currentAcceleration) < 0.01)):
            app.player['x'].previousVelocity = (
                app.player['x'].currentMaxVelocity)
            
    # handling Y velocity
    if((app.ti['ground'].yOffset > 0) or app.player['y'].currentThrust > 0):
        app.playerState = 'air'
        app.player['y'].gravity = app.setGravity
    else:
        app.player['y'].gravity = 0
        app.previousPlayerYVelocity = 0
    runPlayerVelocityCalculations(app,'y')

    playerSpeedMultiplier = 4 # speed adjustment value
    # SHORTEN ONCE FINISHED
    for tileableImageName in ['background','midground','ground']:
        app.ti[tileableImageName].xOffset += ((app.player['x'].currentVelocity)*playerSpeedMultiplier)
        if((app.ti[tileableImageName].yOffset + ((app.player['y'].currentVelocity)*playerSpeedMultiplier)) >= 0):
            app.ti[tileableImageName].yOffset += ((app.player['y'].currentVelocity)*playerSpeedMultiplier)
        else:
            app.ti[tileableImageName].yOffset = 0

def updateTiles(app,tileableImageName):
    # retrieving variable values
    tileWidth = app.ti[tileableImageName].tileWidth
    xOffset = app.ti[tileableImageName].xOffset
    yOffset = app.ti[tileableImageName].yOffset
    parallaxCoefficient = app.ti[tileableImageName].parallaxCoefficient
    tileableImageWidth = app.ti[tileableImageName].imageWidth
    tileableImageHeight = app.ti[tileableImageName].imageHeight 
    cols = app.ti[tileableImageName].numberOfCols
    initialColsList = app.ti[tileableImageName].initialColsList

    # applying parallax
    xOffsetParallax = int(xOffset/parallaxCoefficient)
    yOffsetParallax = int(yOffset/parallaxCoefficient)

    # calculating if a tile needs to be swapped to the other side of the screen
    if(xOffsetParallax > 0):
        sign = 1
    else:
        sign = -1
    colOffset = math.floor(abs(xOffsetParallax)/tileWidth)*sign
    
    if(xOffset > tileableImageWidth):
        colOffset -= cols
        xOffsetParallax -= tileableImageWidth
    elif(xOffset < -tileableImageWidth):
        colOffset += cols
        xOffsetParallax += tileableImageWidth

    # rotating the list appropriately to scroll the tiles
    app.ti[tileableImageName].currentColsList = (
        rotateList(initialColsList,colOffset))

    applicableXOffset = xOffsetParallax-(colOffset*tileWidth)

    # ptc(f'{tileableImageName} Y Offset', tileableImageY)
    
    # SHORTEN WHEN FINISHED
    app.ti[tileableImageName].currentTileXPosition = ((app.ti[tileableImageName].initialTileXPosition)-applicableXOffset)
    app.ti[tileableImageName].currentTileYPosition = ((app.ti[tileableImageName].initialTileYPosition)+yOffsetParallax)
    app.ti[tileableImageName].xOffset = (xOffsetParallax * parallaxCoefficient)

def drawTiles(app,tileableImageName):
    tileWidth = app.ti[tileableImageName].tileWidth
    currentColsList = app.ti[tileableImageName].currentColsList
    currentTileXPosition = app.ti[tileableImageName].currentTileXPosition
    currentTileYPosition = app.ti[tileableImageName].currentTileYPosition
    
    for row in currentColsList:
        # only draw tiles if they are within the bounds of the screen
        if((app.screenLeft <= currentTileXPosition < app.screenRight) and 
           (currentTileYPosition < app.screenBottom)):
                tileableImageSavePath = (f'images/{tileableImageName}/'+
                                    f'{tileableImageName}Tile_{row}.png')
                # only draw tiles if their file can be accessed, otherwise 
                # report an error
                if os.path.exists(tileableImageSavePath):
                    drawImage(tileableImageSavePath,currentTileXPosition,
                              currentTileYPosition,opacity = 
                              app.ti[tileableImageName].opacity)
                else:
                    reportError('accessing desired tile file', 
                                'IMAGE COULD NOT BE FOUND', 'drawTiles', 
                                'File name', (tileableImageSavePath), None)
        currentTileXPosition += tileWidth

def tileImage(app,tileableImage,tileWidth,tileableImageName):
    # TILEABLE IMAGE NAME SHOULD BE THE SAME NAME AS THE FOLDER THAT CONTAINS IT
    tileableImageWidth, tileableImageHeight = getImageSize(tileableImage)
    cols = int(tileableImageWidth/tileWidth)
    tileableImage = Image.open(tileableImage)
    cropXPosition = 0
    # cropping image into tiles and saving them individually
    for col in range(cols):
        currentTile = tileableImage.crop((cropXPosition,0,
                                        cropXPosition+tileWidth,
                                        tileableImageHeight))
        tileableImageSavePath = (f'images/{tileableImageName}/'+
                                 f'{tileableImageName}Tile_{col}.png')
        if os.path.isdir(f'images/{tileableImageName}'):
            currentTile.save(tileableImageSavePath)
        else:
            reportError('saving tile from an image', 
                        'FOLDER COULD NOT BE LOCATED', 'tileImage', 
                        'Folder you are trying to save to',
                        (tileableImageName), None)
        currentTile.close()
        cropXPosition += tileWidth
    
    # setting the initial X offset for the image
    app.ti[tileableImageName].initialTileXPosition = (
        (app.windowWidth-tileableImageWidth)/2)
    
    # setting the image width and height
    app.ti[tileableImageName].imageWidth = tileableImageWidth
    app.ti[tileableImageName].imageHeight = tileableImageHeight

    # setting the number of columns for the tileable image, as well as 
    # generating the colsList used to determine the order in which the 
    # images are displayed
    app.ti[tileableImageName].numberOfCols = cols
    colsList = []
    for col in range(cols):
        colsList.append(col)
    app.ti[tileableImageName].initialColsList = colsList
    
def lightmapSetup(app):
    app.lightmapScalingFactor = 10
    app.lightmapSectors = int(app.windowWidth / app.lightmapSectorWidth)
    for i in range(app.lightmapSectors):
        app.lightmapSectorDict[f'sector_{i}']=[]
    print('lightmap sectors: ',app.lightmapSectors)
    lightmapMatrixX = int(app.windowWidth/app.lightmapScalingFactor)
    lightmapMatrixY = int(app.windowHeight/app.lightmapScalingFactor)
    lightmapOpacityMatrix = numpy.array([[255] * lightmapMatrixX]*lightmapMatrixY, dtype=numpy.uint8)
    print(f'{len(lightmapOpacityMatrix)} rows')
    print(f'{len(lightmapOpacityMatrix[0])} columns')

# helper function to calculate gaussian lightmap map
def calculateLightmapGaussian(x,y,lightSources):
    lightsourceMaxIntensity = 255
    opacity = 255
    # arbitrady adjusted value for calculation distance cutoff
    # it is unnessecary to calculate the effects of a light source on a point
    # if that light source is definitely too far away to have an effect
    # having a distance cutoff saves computation time
    maxDistance = 1000
    for lightSource in lightSources:
        if(getDistance(x,y,lightSource.x,lightSource.y) < maxDistance):
            opacity -= int((lightsourceMaxIntensity)*((lightSource.intensity)**((-1*(((x-lightSource.x)**2)/(2*((lightSource.spread)**2))))-(((y-lightSource.y )**2)/(2*((lightSource.spread)**2))))))
    return max(opacity,0)

def updateLightmap(app):
    # go through all visible sectors
    lightmapSectorX = 0
    for lightmapSector in range(app.lightmapSectors):
        print('current sector X: ',lightmapSectorX)
        # check matrix for all visible sectors:
        lightmapMatrixX = int(app.lightmapSectorWidth/app.lightmapScalingFactor)
        lightmapMatrixY = int(app.windowHeight/app.lightmapScalingFactor)
        print('lightmapMatrixX: ',lightmapMatrixX)
        print('lightmapMatrixY: ',lightmapMatrixY)
        print('lightmapSector: ',lightmapSector)
        print('lightmapSectorX: ',lightmapSectorX)
        comparisonMatrix = numpy.array([[255] * lightmapMatrixX]*lightmapMatrixY, dtype=numpy.uint8)
        lightmapOpacityMatrix = copy.deepcopy(comparisonMatrix)
        for y in range(lightmapMatrixY):
            for x in range(lightmapMatrixX):
                lightmapOpacityMatrix[y,x] = calculateLightmapGaussian(x+lightmapSectorX,y,app.lightSources)
        # print(comparisonMatrix)
        # print(lightmapOpacityMatrix)
        if(not(numpy.array_equal(lightmapOpacityMatrix,comparisonMatrix))):
            lightmap = Image.fromarray(lightmapOpacityMatrix, mode = 'L')
            if os.path.exists(f'images/lightmap/Sector_{app.lightmapImageCounter-app.lightmapSectors}.png'):
                os.remove(f'images/lightmap/Sector_{app.lightmapImageCounter-app.lightmapSectors}.png')
            app.lightmapImageCounter += 1
            lightmapSectorSaveAddress=(f'images/lightmap/Sector_{app.lightmapImageCounter}.png')
            lightmap.save(lightmapSectorSaveAddress)
            lightmap.close()
            print('generate image!')
        else:
            lightmapSectorSaveAddress = 'images/lightmap/LIGHTMAP_TEST_DEFAULT.png'
        #[X POSITION, Y POSITION,WIDTH,HEIGHT,IMAGE ADDRESS]
        app.lightmapSectorDict[f'sector_{lightmapSector}'] = [lightmapSectorX,0,lightmapMatrixX,lightmapMatrixY,lightmapSectorSaveAddress]
        print(app.lightmapSectorDict[f'sector_{lightmapSector}'])
        lightmapSectorX += app.lightmapSectorWidth/app.lightmapScalingFactor


    # REFERENCING THIS ARTICLE - NEED HELP
    # https://www.geeksforgeeks.org/python/file-flush-method-in-python/



def drawLightmap(app):
    for lightmapSector in range(app.lightmapSectors):
        # print('lightmapSector: ',lightmapSector)
        lightmapSectorX = app.lightmapSectorDict[f'sector_{lightmapSector}'][0]
        lightmapSectorY = app.lightmapSectorDict[f'sector_{lightmapSector}'][1]
        lightmapSectorWidth = app.lightmapSectorDict[f'sector_{lightmapSector}'][2]+app.lightmapBuffer
        lightmapSectorHeight = app.lightmapSectorDict[f'sector_{lightmapSector}'][3]+app.lightmapBuffer
        lightmapSectorImage = app.lightmapSectorDict[f'sector_{lightmapSector}'][4]
        # print('lightmapSectorX:',lightmapSectorX)
        # print('lightmapSectorY:',lightmapSectorY)
        # print('lightmapSectorWidth:',lightmapSectorWidth)
        # print('lightmapSectorHeight:',lightmapSectorHeight)
        # print('lightmapSectorImage:',lightmapSectorImage)
        drawImage(lightmapSectorImage,lightmapSectorX*app.lightmapScalingFactor,lightmapSectorY*app.lightmapScalingFactor,width = (lightmapSectorWidth*app.lightmapScalingFactor),height = (lightmapSectorHeight*app.lightmapScalingFactor),opacity=app.lightmapOpacity)

def onKeyPress(app,key):
    # enable/disable temporary display readout
    if(key == 't'):
        if(app.tempDisplayReadout):
            app.tempDisplayReadout = False
        else:
            app.tempDisplayReadout = True

def onKeyHold(app,keys):
    # TESTING ONLY - DIRECTLY CHANGE OFFSETS
    # if('d' in keys and not('a' in keys)):
    #     for i in ['background','midground','ground']:
    #         app.ti[i].xOffset += 10
    # else:
    #     for i in ['background','midground','ground']:
    #         app.ti[i].xOffset -= 10

    # X movement

    # SHORTEN ONCE FINISHED
    if(('d' in keys) or ('a' in keys)):
        if(('d' in keys) and ('a' in keys)):
            app.player['x'].currentThrust = 0
            if(app.ti['ground'].yOffset > 0):
                app.player['x'].frictionConstant = (app.player['y'].setFrictionConstant)
            else:
                app.player['x'].frictionConstant = (app.player['x'].setFrictionConstant)
        elif(('d' in keys) and (not('a' in keys))):
            app.playerFacing = 'right'
            if(app.playerState != 'slide'):
                app.player['x'].currentThrust = app.player['x'].setThrust 
                if(app.ti['ground'].yOffset > 0):
                    app.player['x'].frictionConstant = (app.player['y'].setFrictionConstant)
                else:
                    app.player['x'].frictionConstant = (app.player['x'].setFrictionConstant)
            else:
                app.player['x'].currentThrust = (app.player['x'].setThrust/10)
                app.player['x'].frictionConstant = (app.player['x'].setFrictionConstant/100)
        else:
            app.playerFacing = 'left'
            if(app.playerState != 'slide'):
                app.player['x'].currentThrust = -app.player['x'].setThrust 
                if(app.ti['ground'].yOffset > 0):
                    app.player['x'].frictionConstant = (app.player['y'].setFrictionConstant)
                else:
                    app.player['x'].frictionConstant = (app.player['x'].setFrictionConstant)
            else:   
                app.player['x'].currentThrust = -(app.player['x'].setThrust/10)
                app.player['x'].frictionConstant = (app.player['x'].setFrictionConstant/100)
    # Y movement
    if(('w' in keys) or ('s' in keys)):
        if(('w' in keys) and ('s' in keys)):
            if(app.ti['ground'].yOffset > 0):
                app.player['y'].currentThrust = app.playerGlideThrust
            app.player['y'].frictionConstant = (
                app.player['y'].setFrictionConstant)
        elif(('w' in keys) and (not('s' in keys))):
            if(app.playerWingCounter < app.maxPlayerWingCounter):
                app.player['y'].currentThrust = (app.player['y'].setThrust-
                                                 int((app.playerWingCounter/
                                                      (app.maxPlayerWingCounter
                                                       /10))**2)-app.setGravity)
                app.playerWingCounter += 50
            elif(app.ti['ground'].yOffset > 0):
                app.player['y'].currentThrust = app.playerGlideThrust
            else: 
                app.player['y'].currentThrust = 0
            app.player['y'].frictionConstant = (
                app.player['y'].setFrictionConstant)
        else:
            if(app.ti['ground'].yOffset > 0):
                app.player['y'].currentThrust = app.playerGlideThrust
            else: 
                app.player['y'].currentThrust = 0
            app.player['y'].frictionConstant = (
                app.player['y'].setFrictionConstant)

def onKeyRelease(app,key):
    if((key == 'a') or (key == 'd')):
        app.player['x'].currentThrust = 0
    if((key == 'w') or (key == 's')):
        app.player['y'].currentThrust = 0
        app.player['y'].frictionConstant = -1

def onMousePress(app,mouseX,mouseY):
    # testing lighting engine
    app.lightSources.append(lightSource(1,1000,(mouseX/app.lightmapScalingFactor),(mouseY/app.lightmapScalingFactor),0.95))
    updateLightmap(app)

def onMouseRelease(app,mouseX,mouseY):
    pass

def onStep(app):
    updatePlayerImage2(app)
    for tileableImageName in ['background','midground','ground']:
        updateTiles(app,tileableImageName)
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
    # ['background','midground','ground']
    for tileableImageName in ['background','midground','ground']:
        drawTiles(app,tileableImageName)
    drawImage(app.playerImage, app.playerX, app.playerY, 
              width = app.playerWidth, height = app.playerHeight)
    drawLightmap(app)
    # temporary readout for variables
    if(app.tempDisplayReadout):
        tempDisplayReadout(app,['currentPlayerXAcceleration',
                                app.player['x'].currentAcceleration,
                                'currentPlayerXVelocity',
                                app.player['x'].currentVelocity, 
                                'currentPlayerXThrust',
                                app.player['x'].currentThrust, 
                                'previousPlayerXVelocity',
                                app.player['x'].previousVelocity,
                                'playerXFrictionConstant',
                                app.player['x'].frictionConstant,
                                'currentPlayerXFrictionForce',
                                app.player['x'].currentFrictionForce,
                                'currentMaxPlayerXVelocity',
                                app.player['x'].currentMaxVelocity,
                                'current X gravity',
                                app.player['x'].gravity,
                                'currentPlayerYAcceleration',
                                app.player['y'].currentAcceleration,
                                'currentPlayerYVelocity',
                                app.player['y'].currentVelocity, 
                                'currentPlayerYThrust',
                                app.player['y'].currentThrust, 
                                'previousPlayerYVelocity',
                                app.player['y'].previousVelocity,
                                'playerYFrictionConstant',
                                app.player['y'].frictionConstant,
                                'currentPlayerYFrictionForce',
                                app.player['y'].currentFrictionForce,
                                'currentMaxPlayerYVelocity',
                                app.player['y'].currentMaxVelocity,
                                'current Y gravity',
                                app.player['y'].gravity,
                                'current ground YOffset',
                                app.ti['ground'].yOffset,
                                'playerWingCounter',
                                app.playerWingCounter,
                                'current player state',
                                app.playerState])
       
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

    # establishing tileable image class
    class tileableImage:
        def __init__(self):
            self.image = 0
            self.numberOfCols = 0
            self.initialColsList = 0
            self.currentColsList = 0
            self.xOffset = 0
            self.yOffset = 0
            self.tileWidth = 0
            self.imageWidth = 0
            self.imageHeight = 0
            self.parallaxCoefficient = 0
            self.initialTileXPosition = 0
            self.initialTileYPosition = 0
            self.currentTileXPosition = 0
            self.currentTileYPosition = 0
            self.opacity = 100
    
    app.ti = dict() 
    # ti stands for Tileable Image. an abbreviation was needed otherwise
    # calling from this dictionary would become absurdly long

    # establishing images as instances of the class
    app.ti['background'] = tileableImage()
    app.ti['midground'] = tileableImage()
    app.ti['ground'] = tileableImage()

    # establishing tiling widths 
    # THESE ARE MANUALLY SET ACCORDING TO THE IMAGES
    app.ti['background'].tileWidth = 125
    app.ti['midground'].tileWidth = 75
    app.ti['ground'].tileWidth = 50

    # etablishes background and ground images to display
    app.ti['background'].image = 'images/background/TEST_background_1.png'
    app.ti['midground'].image = 'images/midground/TEST_midground_1.png'
    app.ti['ground'].image = 'images/ground/TEST_ground_1.png'
    
    # parallax coefficients change how much each tiled image moves for a 
    # change in xOffset
    app.ti['background'].parallaxCoefficient = 3
    app.ti['midground'].parallaxCoefficient = 2
    app.ti['ground'].parallaxCoefficient = 1

    # opacity determines how transparent one of the tileable images should be
    # they are set to 100 by default
    app.ti['background'].opacity = 100
    app.ti['midground'].opacity = 100
    app.ti['ground'].opacity = 100

    # split images into tiles and save the tiles as seperate images
    for tileableImageName in ['background','midground','ground']:
        tileImage(app,app.ti[tileableImageName].image,
                  app.ti[tileableImageName].tileWidth,
                  tileableImageName)

    # establishing initial y offsets
    app.ti['background'].initialTileYPosition = -600
    app.ti['midground'].initialTileYPosition = 125
    app.ti['ground'].initialTileYPosition = 426

    # ---- PLAYER SETUP ----

    # sets first player image to show
    app.playerImageIndex = [0,0,-1]

    # intiates player physics parameters
    class playerPhysics:
        def __init__(self):
            self.currentThrust = 0
            self.setThrust = 0
            self.currentVelocity = 0
            self.previousVelocity = 0
            self.currentFrictionForce = 0
            self.currentAcceleration = 0
            self.currentMaxVelocity = 0
            self.frictionConstant = 0
            self.setFrictionConstant = 0
            self.gravity = 0
    app.player = dict()
    app.player['x'] = playerPhysics()
    app.player['y'] = playerPhysics()


    # the following parameters are tuned by feel, and cannot be determined
    # mathematically
    app.playerMass = 25
    app.player['x'].setThrust = 150
    app.player['x'].setFrictionConstant = -15
    app.player['x'].frictionConstant = -15
    app.player['y'].setThrust = 100
    app.player['y'].setFrictionConstant = -10
    app.player['y'].frictionConstant = -10
    app.setGravity = -75
    driftConstant = 20 # used to tune how quickly a player falls while gliding
    app.playerGlideThrust = -app.setGravity - driftConstant

    # value for player wing counter is manually set to determine the ammount of 
    # time for which wings can provide upwards lift
    app.maxPlayerWingCounter = 2500

    # indicates what state the player is in
    # current states: 'ground', 'air', 'slide', 'roll'
    app.playerState = 'ground'

    # indicates the direction the player is facing
    app.playerFacing = 'right'

    # intializes player counters to 0
    app.playerAnimationCounter = 0
    app.playerWingCounter = 0
    
    # ---- LIGHTING SETUP ----

    # initliaizing light source class - DONE GLOBALLY
    
    # iniializing light sources list
    app.lightSources = []

    # establishing lighting opacity
    app.lightmapOpacity = 75

    # establishing lightmap sector width and lightmap sector dictionary
    app.lightmapSectorWidth = 100
    app.lightmapSectorDict = dict()

    # establishing lightmap buffer (help overcome tiling artifacts)
    app.lightmapBuffer = 10

    # lighting image counter (i hate this but i have to figure out how to make
    # app.draw actually update itself... same problem where it always draws
    # the first image it ever drew for something)
    app.lightmapImageCounter = 0

    # ---- APP SETUP ----

    # setting the framerate
    app.stepsPerSecond = 4

    # ---- TEMP DEBUG ----

    # misc testing setup
    app.testWalkSpeed = 10
    # app.screenLeft = 100
    # app.screenRight = app.windowWidth - 100

     # set to True to enable readout, set to False to disable
    app.tempDisplayReadout = False

    # Finalization - run the contents of appStep to update everything prior 
    # to running. DO NOT RUN onStep() ITSELF!
    updatePlayerImage2(app)
    for tileableImageName in ['background','midground','ground']:
        updateTiles(app, tileableImageName)
    updatePlayerVelocity(app)
    lightmapSetup(app)
    updateLightmap(app)

appSetup(app)
# initlization!
runApp(width = app.windowWidth, height = app.windowHeight)

# Last Updated: 3:30 PM - 7/06/2025
# total hours spent working here: 28