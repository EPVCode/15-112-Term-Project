# Name: Eduardo Phelan-Vidal
# AndrewID: esphelan
# Section: A

# TODO:
# MAKE TITLE SCREEN - death state sets you there
# GENERALIZE PHYSICS SYSTEM - NOT JUST FOR PLAYERS, WE NEED PHYSICS FOR ENEMIES AS WELL
# ADD SUPPORT FOR EXTERNAL FORCES IN PHYSICS SYSTEM
# ADD GLOBAL X AND Y OFFSETS AND INCORPORATE INTO EXISTING SYSTEMS
# MAKE HEALTH BAR - need death state and ability to reset
# MAKE SUPPORT FOR MULTIPLE SIMULTANEOUS SPELLS (maybe)
# ADD ENEMIES!!!!!!!!!!
# PUT TOGETHER A PAUSE FEATURE - make SHIFT key the one to pause the game, since
# there is currently a bug where holding shift will cause key inputs to persist
# even after the key has stopped being held down. This can't happen if shift
# pauses the game.
# MAKE COMBO CHEAT SHEET FUNCTIONALITY - pressing a hotkey raises up with 
# shaky hands a scroll with your combos scribbled on it. This does not pause the
# game, and obscures your vison. 

# IMPORTS
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
import random

# CLASSES
# intilaizing light soure class
class lightSource:
    def __init__(self,spread,intensity,x,y,initialY,fadeRate):
        self.spread = spread
        self.intensity = intensity
        self.x = x
        self.y = y
        self.initialY = initialY
        self.counter = 0
        self.fadeRate = fadeRate
    def fade(self):
        self.intensity *= self.fadeRate

# initilzing BASE projectile class
class projectile:
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,displayAngle,initialX,initialY,targetX,targetY,isPlayerSpell):
        self.name = name
        self.animationFrames = frames
        self.animationCounter = 0
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.imageScale = imageScale
        self.displayImage = None
        self.displayAngle = displayAngle
        self.initialXPosition = initialX
        self.initialYPosition = initialY
        self.xPosition = initialX
        self.yPosition = initialY
        self.targetX = targetX
        self.targetY = targetY
        self.xVelocity = 0
        self.yVelocity = 0
        self.directionalVelocity = 0
        self.deleteMe = False
        self.isPlayerSpell = isPlayerSpell
        self.xOffset = 0
        self.yOffset = 0
        self.initialYOffset = 0
        
# initialzing linear projectile class - moves in a straight line
class linear(projectile):
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,displayAngle,initialX,initialY,targetX,targetY,isPlayerSpell):
        super().__init__(name,frames,imageWidth,imageHeight,imageScale,displayAngle,initialX,initialY,targetX,targetY,isPlayerSpell)
        self.directionalAcceleration = 0
        self.nearnessFactor = 0
        self.maxVelocity = 0
        self.directionAngle = None

    def move(self):
        dx = (self.xPosition - self.targetX)
        dy = (self.yPosition - self.targetY)
        if(self.directionAngle == None):
            self.directionAngle = math.degrees(math.atan(dy/dx))
            if(dx > 0):
                self.directionalAcceleration *= -1
        # print('directionAngle',self.directionAngle)
        self.directionalVelocity += self.directionalAcceleration
        if(abs(self.directionalVelocity) > self.maxVelocity):
            if(self.directionalVelocity > 0):
                self.directionalVelocity = self.maxVelocity
            elif(self.directionalVelocity < 0):
                self.directionalVelocity = -self.maxVelocity
            else:
                self.directionalVelocity = 0

        self.xVelocity += math.cos(math.radians(self.directionAngle)) * self.directionalVelocity
        self.yVelocity += math.sin(math.radians(self.directionAngle)) * self.directionalVelocity
        # print('xAcceleration:',xAcceleration)
        # print('yAcceleration:',yAcceleration)
        distance = getDistance(self.xPosition,self.yPosition,self.targetX,self.targetY)
        # print(distance)
        if distance < (self.nearnessFactor*3):
            # print('braking')
            self.xVelocity *= 0.5
            self.yVelocity *= 0.5

        self.xPosition += self.xVelocity
        self.yPosition += self.yVelocity

        atDestination = distance < self.nearnessFactor
        return atDestination

# initializing groundbounce projectile class - fires upwards then bounces
class groundbounce(projectile):
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,displayAngle,initialX,initialY,targetX,targetY,isPlayerSpell):
        super().__init__(name,frames,imageWidth,imageHeight,imageScale,displayAngle,initialX,initialY,targetX,targetY,isPlayerSpell)
        self.timer = 0
        self.lifespan = 0
        self.directionAngle = None
        self.directionalVelocity = 0
        self.gravitationalAcceleration = 0
        self.castRight = True
        self.groundYIndex = 0
        self.reboundCoefficient = 0
        self.bounces = 0
        self.maxBounces = 0

    def move(self):
        if(self.directionAngle == None):
            dx = (self.xPosition - self.targetX)
            dy = (self.yPosition - self.targetY)
            self.yPosition -= self.initialYOffset
            self.directionAngle = math.degrees(math.atan(dy/dx))
            # print('directionAngle',self.directionAngle)
            if(dx < 0):
                self.castRight = True
                self.xVelocity += math.cos(math.radians(self.directionAngle)) * self.directionalVelocity
                self.yVelocity += math.sin(math.radians(self.directionAngle)) * self.directionalVelocity
            elif(dx > 0):
                self.castRight = False
                self.xVelocity += math.cos(math.radians(self.directionAngle)) * self.directionalVelocity
                self.yVelocity -= math.sin(math.radians(self.directionAngle)) * self.directionalVelocity
        
        # print('y Offset:', self.yOffset)
        # print('y Position:',self.yPosition)

        # print('xAcceleration:',xAcceleration)
        # print('yAcceleration:',yAcceleration)
        
        if(self.castRight):
            self.xPosition += self.xVelocity
            self.yPosition += self.yVelocity
            self.yVelocity += self.gravitationalAcceleration
        elif(not self.castRight):
            # print('ah')
            self.xPosition -= self.xVelocity
            self.yPosition += self.yVelocity
            self.yVelocity += self.gravitationalAcceleration
            
        # print('current y index of ground:',self.groundYIndex)
        # print('current y index of projectile:',self.yPosition)
        # print('current distance from ground:', self.groundYIndex - self.yPosition)
        if(self.yPosition >= self.groundYIndex):
            self.displayAngle = random.randint(-180,180)
            # print('rebound!')
            self.bounces += 1
            self.yPosition = self.groundYIndex
            self.yVelocity *= -self.reboundCoefficient
            self.xVelocity *= self.reboundCoefficient
            while(self.yPosition >= self.groundYIndex):
                # print('kick')
                self.yPosition -= 10

        self.timer += 1

        return ((self.timer >= self.lifespan) or (self.bounces >= self.maxBounces))

# GENERAL HELPER FUNCTIONS
# My beloved PrintToConsole function (shortened to ptc)
def ptc(x,y):
    print(f'{x}: {y}')

# small list rotation helper function
def rotateList(list,rotations):
    return list[rotations:]+list[0:rotations]

# small distance function using pythagorean theorem
def getDistance(x_1,y_1,x_2,y_2):
    return((((x_2-x_1)**2)+((y_2-y_1)**2))**0.5)

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

# temporary function for debugging, displays the values of certain variables
def tempDisplayReadout(app,inputList):
    buffer = 10
    lineSpacing = 20
    lineXPosition = 0 + buffer
    lineYPosition = app.screenHeight - buffer
    for i in range(0,len(inputList),2):
        displayText = f'{inputList[i]}: {inputList[i+1]}'
        drawLabel(displayText, lineXPosition, lineYPosition, 
              fill = 'white', border = "black", borderWidth = 1, opacity = 100, 
              rotateAngle = 0, align = 'left-bottom', visible = True, size = 20, 
              font = 'arial', bold = True, italic = False)
        lineYPosition -= lineSpacing

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

# 2D list makign helper function using list comphrehension
# referenced from https://academy.cs.cmu.edu/notes/9011
def make2DList(rows,cols,fillData):
    return  [ [fillData] * cols for row in range(rows)]

# PLAYER PHYSICS & ANIMATIONS
def interpretPlayerWingImageIndex(app,indexToInterpret):

    # PLAYER WING IMAGE ENCODING KEY
    # The desired player wing image will be indicated according to the following 
    # list: app.playerWingImageIndex = [a,b,c] with following distinctions:
    # --- a ---
    # a indicates the DIRECTION that the player is facing 
    # a = 0 indicates that the player is facing RIGHT
    # a = 1 indicates that the player is facing LEFT
    # --- b ---
    # b indicates the current MOTION that the player is engaging in
    # b = 0 indicates that the player is STANDING
    # b = 1 indicates that the player is RUNNING
    # b = 2 indicates that the player is SLIDING
    # b = 3 indicates that the player is FLYING
    # b = 3 indiciates that the player is GLIDING
    # (this list will be UPDATED as more movements are added)
    # --- c ---
    # c indicates the CURRENT FRAME OF ANIMATION that the player is on
    # c = -1 indicates that the player's wing are NOT on a frame of an animation
    # c = 0 indicates that the player's wing are on the FIRST frame of an animation
    # c = 1 indicates that the player's wing are on the SECOND frame of an animation
    # and so on...

    # Dropdown to hide everything but the
    if(indexToInterpret == 0):
        if(app.playerWingImageIndex[0] == 0):
            return 'right' # FACING should NOT be capitalized
        elif(app.playerWingImageIndex[0] == 1):
            return 'left'
        else:
            reportError('interpreting player facing value', 
                        'INVALID VALUE RECIEVED',
                        'interpretPlayerWingImageIndex',
                        'Value', app.playerWingImageIndex[0],None)
    elif(indexToInterpret == 1):
        if(app.playerWingImageIndex[1] == 0):
            return 'Wing_closed' # MOTION SHOULD be capitalized
        elif(app.playerWingImageIndex[1] == 1):
            return 'Wing_closed2'
        elif(app.playerWingImageIndex[1] == 2):
            return 'Wing_empty'
        elif(app.playerWingImageIndex[1] == 3):
            return 'Wing'
        elif(app.playerWingImageIndex[1] == 4):
            return 'Wing_glide'
        else:
            reportError('interpreting player motion value', 
                        'INVALID VALUE RECIEVED', 
                        'interpretPlayerWingImageIndex', 
                        'Value', app.playerWingImageIndex[1],None)
    elif(indexToInterpret == 2):
        if(app.playerWingImageIndex[2] == -1):
            return '' # FRAME should be a number or an empty string
        elif(app.playerWingImageIndex[2] > -1):
            return (f'_{app.playerWingImageIndex[2]}')
        else:
            reportError('interpreting playerWingAnimationFrame value', 
                        'INVALID VALUE RECIEVED', 'interpretPlayerImageIndex', 
                        'Value', app.playerImageIndex[2], None)
    else:
        reportError('interpreting playerWingImageIndex', 
                        'INVALID INDEX', 'interpretPlayerWingImageIndex', 
                        'app.playerWingImageIndex has no index', 
                        f'[{indexToInterpret}]', None)

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
    # b = 3 indicates that the player is FLYING
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
                        'INVALID VALUE RECIEVED','interpretPlayerImageIndex', 
                        'Value', app.playerImageIndex[0],None)
    elif(indexToInterpret == 1):
        if(app.playerImageIndex[1] == 0):
            return 'Stand' # MOTION SHOULD be capitalized
        elif(app.playerImageIndex[1] == 1):
            return 'Run'
        elif(app.playerImageIndex[1] == 2):
            return 'Slide'
        elif(app.playerImageIndex[1] == 3):
            return 'Fly'
        else:
            reportError('interpreting playerMotion value', 
                        'INVALID VALUE RECIEVED', 'interpretPlayerImageIndex', 
                        'Value', app.playerImageIndex[1],None)
    elif(indexToInterpret == 2):
        if(app.playerImageIndex[2] == -1):
            return '' # FRAME should be a number or an empty string
        elif(app.playerImageIndex[2] > -1):
            return (f'_{app.playerImageIndex[2]}')
        else:
            reportError('interpreting playerAnimationFrame value', 
                        'INVALID VALUE RECIEVED', 'interpretPlayerImageIndex', 
                        'Value', app.playerImageIndex[2], None)
    else:
        reportError('interpreting playerImageIndex', 
                        'INVALID INDEX', 'interpretPlayerImageIndex', 
                        'app.playerImageIndex has no index', 
                        f'[{indexToInterpret}]', None)

def playerAnimationAltitudeCheck(app):
    if(app.ti['ground'].yOffset > 0):
        return 'air'
    else: 
        return 'ground'

# little helper function to set player wing offset at different states
def setPlayerWingOffset(app,x,y):
    if(app.playerFacing == 'right'):
        app.playerWingXOffset = x
        app.playerWingYOffset = y
    else:
        app.playerWingXOffset = -x
        app.playerWingYOffset = y

def interpretPlayerState(app):
        # 'Locking' animations, which are those for which the direction cannot
        # be immediately changed by pressing the arrow keys, take priority
        # over directional indication
    if(app.playerState == 'slide'): # IS PLAYER SLIDING?
        app.playerAnimationCounter += 1
        # print(app.playerAnimationCounter)
        # slideAnimationSpeed is an adjustable timing constant that is tuned by 
        # hand such that the slide animation plays at an appropriate speed
        slideAnimationSpeed = 3
        if((app.playerAnimationCounter % slideAnimationSpeed) == 0):
            app.playerImageIndex[2] += 1
            if(app.playerImageIndex[2] == 3): 
                # there are only four frames of the sliding animation

                # returning to either ground or air state
                app.playerState = playerAnimationAltitudeCheck(app)

                # resetting x friction back to normal (must occur even if key is
                # not currently being pressed)
                app.player['x'].frictionConstant = app.player['x'].setFrictionConstant
                # print('slide animation over')
                # ptc('app.playerState',app.playerState)

    else: # IF NOT SLIDING - CHECK WHAT STATE WE SHOULD BE IN
        app.playerState = playerAnimationAltitudeCheck(app)

    # assigning player direction - right or left
    if(app.playerFacing == 'right'):
        app.playerImageIndex[0] = 0
        app.playerWingImageIndex[0] = 0
    else:
        app.playerImageIndex[0] = 1
        app.playerWingImageIndex[0] = 1

    # different activities for player state
    if(app.playerState == 'ground'): # PLAYER IS ON THE GROUND
        # WHEN THE PLAYER IS ON THE GROUND THEY CAN BE STANDING, RUNNING, OR SLIDING

        app.playerWingCounter = 0 # reset wing counter when touching the ground

        # IF PLAYER IS NOT STANDING STILL:
        if(abs(app.player['x'].currentVelocity) > 1):

            # PLAYER SHOULD INITIATE SLIDE IF THEIR VELOCITY AND THRUST ARE IN 
            # OPPOSITE DIRECTIONS, AND THEIR THRUST IS NONZERO
            if((not sameSign(app.player['x'].currentVelocity, app.player['x'].currentThrust)) and (app.player['x'].currentThrust != 0)): 
                
                # put player into slide mode, will begin silde animation 
                # execution at the beginning of the function
                app.playerState = 'slide'
                app.playerAnimationCounter = 0 # reset animation counter
                app.playerImageIndex[1] = 2    # set player moition to sliding
                app.playerImageIndex[2] = 0    # set player animation to frame 0
                app.playerWingImageIndex[1] = 2 # set wing to empty (wings are hidden while sliding)
            
            # IF THE PLAYER IS NOT STANDING STILL, BUT THEY ARE NOT SLIDING, THEN THEY MUST BE RUNNING
            
            # first we check if the player is ALREADY running (player motion is set to running)
            elif(app.playerImageIndex[1] == 1):
                
                # reset animation counter to avoid running into integer limit
                if(app.playerAnimationCounter > 10000):
                    app.playerAnimationCounter = 0  
                    
                # print(21-int(abs((app.currentPlayerXVelocity))))
                # ptc('app.playerAnimationCounter',app.playerAnimationCounter)

                # set the maximum speed that running animation can play
                minimumTicksBetweenRunAnimationFrames = 2

                # ANIMATION LOOP FOR RUNNING

                # THIS CONTROLS THE VARIABLE SPEED OF THE RUNNING ANIMATION
                # THE NUMBER OF TICKS BETWEEN FRAMES OF THE ANIMATION DECREASES
                # AS PLAYER VELOCITY INCREASES
                if((app.playerAnimationCounter % (abs((int(abs(app.player['x'].currentVelocity)))-int(abs((app.player['x'].currentMaxVelocity))))+minimumTicksBetweenRunAnimationFrames) == 0)):
                    
                    # index to next frame in run animation
                    app.playerImageIndex[2] += 1

                    # ptc('app.playerImageIndex[2]',app.playerImageIndex[2])
                    
                    # there are six frames in the running animation. 
                    # if on the last frame, reset to the first frame
                    if(app.playerImageIndex[2] == 5):
                        app.playerImageIndex[2] = 0
                
                # index animation counter every frame that we are running
                app.playerAnimationCounter += 1

            # if the player is running, but their image is not set to running 
            # yet then we must set their image to running, and set up for the 
            # running amimation
            else:
                # reset player animation counter on first frame of run animation
                app.playerAnimationCounter = 0
                # reset player WING animation counter on first frame of run 
                # animation (just in case it is nonzero). wings are not animated
                # while running.
                app.playerWingAnimationCounter = 0
                # set player motion to RUNNING
                app.playerImageIndex[1] = 1
                # set player animation frame to 0 - first frame of animation
                app.playerImageIndex[2] = 0 
                # set wings to CLOSED2 - tilted closed position to make sure
                # they properly align with player running sprite
                app.playerWingImageIndex[1] = 1
                # set wing animation frame to -1, wings are NOT animated while 
                # player is running
                app.playerWingImageIndex[2] = -1
                
                # SET THE CORRECT WING SPRITE OFFSETS DEPENDING ON DIRECTION
                # these values are tuned manually
                setPlayerWingOffset(app,25,35)

        # IF PLAYER IS ON THE GROUND BUT NOT RUNNING OR SLIDING THEY MUST BE STANDING        
        else:
            # reset player animation counter, in case it is nonzero.
            # the player is not animated while they are standing
            app.playerAnimationCounter = 0
            # set player motion to STANDING
            app.playerImageIndex[1] = 0
            # set player animation frame to -1 --> NOT BEING ANIMATED
            app.playerImageIndex[2] = -1
            # set player wing to CLOSED - upright closed position to match 
            # standing animation
            app.playerWingImageIndex[1] = 0
            # set player wing animation frame to -1 --> NOT BEING ANIMATED
            app.playerWingImageIndex[2] = -1

            # SET THE CORRECT WING SPRITE OFFSETS DEPENDING ON DIRECTION
            # these values are tuned manually
            setPlayerWingOffset(app,32,20)

    elif(app.playerState == 'air'): # PLAYER IS CURRENTLY IN THE AIR
        # WHEN THE PLAYER IS IN THE AIR THEY CAN BE FLYING, GLIDING, OR FALLING
        
        # set player motion to FLYING
        app.playerImageIndex[1] = 3
        # set player animation frame to -1 --> NOT BEING ANIMATED
        app.playerImageIndex[2] = -1

        # this gets pretty convoluted, brace yourself...

        # IF THE PLAYER IS IN THE AIR, AND THEIR CURRENT UPWARDS THRUST IS 
        # GREATER THAN 0, THEN WE DO NOT WANT THE PLAYERS WINGS TO BE CLOSED.
        # PLAYERS WINGS ARE EITHER ACTIVELY FLYING, OR GLIDING
        if(app.player['y'].currentThrust > 0):
            # set wing motion to FLYING
            app.playerWingImageIndex[1] = 3

            # IF THE PLAYER'S WING COUNTER IS GREATER THAN IT'S MAXIMUM THEY 
            # MUST BE GLIDING IF THE PLAYER IS GLIDING THEN THEIR CURRENT 
            # UPWARDS THRUST WILL BE EQUAL TO GLIDE THRUST BUT THE PLAYER CAN 
            # STILL BE GLIDING EVEN IF THEIR WING COUNTER IS NOT PAST ITS 
            # MAXIMUM SO I ALSO EXPLICITELY CHECK THAT THE PLAYERS UPWARD 
            # THRUST IS NOT EQUAL TO GLIDE THRUST

            # IF THE PLAYER IS IN THE AIR, AND THEIR CURRENT UPWARDS THRUST IS 
            # NONZERO, AND THEY ARE NOT GLIDING, THEN THEY MUST BE FLYING:
            if((app.playerWingCounter < app.maxPlayerWingCounter) and (app.player['y'].currentThrust != app.playerGlideThrust)):
                
                # reset wing animation counter to avoid running into integer limit
                if(app.playerWingAnimationCounter > 10000):
                    app.playerWingAnimationCounter = 0  
                
                # setting the speed of the wing animation 
                # unlike the run animation, the speed is constant.
                wingAnimationSpeed = 1

                # ANIMATION LOOP FOR FLYING
                if(app.playerWingAnimationCounter % wingAnimationSpeed == 0):
                    # index to next frame in flying animation
                    app.playerWingImageIndex[2] += 1

                    # ptc('app.playerWingAnimationCounter',app.playerWingAnimationCounter)
                    # ptc('app.playerWingImageIndex[2]',app.playerWingImageIndex[2])
                    # ptc('app.playerImageIndex[2]',app.playerImageIndex[2])

                    # there are six frames in the running animation. 
                    # if on the last frame, reset to the first frame
                    if(app.playerWingImageIndex[2] == 5):
                        app.playerWingImageIndex[2] = 0

                # index wing animation counter every frame that we are flying
                app.playerWingAnimationCounter += 1

            # explained above: if the player fails the above if statement then
            # they MUST BE GLIDING
            else:
                # set wing animation counter to 0, since wings are not animated
                # while gliding
                app.playerWingAnimationCounter = 0
                # set wing motion to GLIDING
                app.playerWingImageIndex[1] = 4
                # set wing animation frame to -1 --> NOT BEING ANIMATED
                app.playerWingImageIndex[2] = -1

        # IF THE PLAYER IS IN THE AIR BUT THEY AER NOT NOT FLYING OR GLIDING 
        # THEN THEY MUST BE FALLING
        else:
            # set wing animation counter to 0, since wings are not animated
            # while falling
            app.playerWingAnimationCounter = 0

            # set wing motion to CLOSED2, the angled closed position to match
            # the angled back of the player sprite in the flying position
            app.playerWingImageIndex[1] = 1
            # set wing animation frame to -1 --> NOT BEING ANIMATED
            app.playerWingImageIndex[2] = -1

        # WE USE THE SAME OFFSET FOR THE WINGS FOR FLYING, GLIDING, AND FALLING
        # SET THE CORRECT WING SPRITE OFFSETS DEPENDING ON DIRECTION
        # these values are tuned manually
        setPlayerWingOffset(app,27,27)

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
    
    playerSpriteWidth = 500 # width of actual player sprite image - same for wings
    playerSpriteHeight = 500 # height of actual player sprite image - same for wings
    playerScale = 0.25
    app.playerWidth = int(playerSpriteWidth*playerScale)
    app.playerHeight = int(playerSpriteHeight*playerScale)
    app.playerWingWidth = int(playerSpriteWidth*playerScale)
    app.playerWingHeight = int(playerSpriteHeight*playerScale)
    app.playerX = int((app.screenWidth-app.playerWidth)/2)
    app.playerY =  int((app.screenHeight-app.playerHeight)/2)

    interpretPlayerState(app)
    
    playerFacing = interpretPlayerImageIndex(app,0)
    playerMotion = interpretPlayerImageIndex(app,1)
    playerAnimationFrame = interpretPlayerImageIndex(app,2)

    wingFacing = interpretPlayerWingImageIndex(app,0)
    wingMotion = interpretPlayerWingImageIndex(app,1)
    wingAnimationFrame = interpretPlayerWingImageIndex(app,2)

    app.playerWingX = int((app.screenWidth-app.playerWidth)/2) - app.playerWingXOffset
    app.playerWingY =  int((app.screenHeight-app.playerHeight)/2) - app.playerWingYOffset

        
    #s etting Player Image Path
    playerImageName = (f'{playerFacing}{playerMotion}{playerAnimationFrame}')
    testPlayerImagePath = (f'images/player/{playerImageName}.png')

    # setting wing image path
    playerWingImageName = (f'{wingFacing}{wingMotion}{wingAnimationFrame}')
    testPlayerWingImagePath = (f'images/player/{playerWingImageName}.png')
    
    # Assigning Player Image Path and returning an error if it is invalid
    if os.path.exists(testPlayerImagePath):
        app.playerImage = (f'images/player/{playerImageName}.png')
    else:
        reportError('accessing desired player image file', 
                    'IMAGE COULD NOT BE FOUND', 'UpdatePlayerImage2', 
                    'File name', (f'images/{playerImageName}.png'), None)
    if os.path.exists(testPlayerWingImagePath):
        app.playerWingImage = (f'images/player/{playerWingImageName}.png')
    else:
        reportError('accessing desired player wing image file', 
                    'IMAGE COULD NOT BE FOUND', 'UpdatePlayerImage2', 
                    'File name', (f'images/{playerWingImageName}.png'), None)

def drawPlayer(app):
    # if player is running right specifically we want to display the wings 
    # OVER the player image. Under no other condition is this visibly neseccary
    if((app.playerFacing == 'right') and (app.playerImageIndex[1] == 1)):
        drawImage(app.playerImage, app.playerX, app.playerY, 
                width = app.playerWidth, height = app.playerHeight)
        drawImage(app.playerWingImage, app.playerWingX, app.playerWingY, 
                width = app.playerWingWidth, height = app.playerWingHeight)
    else:
        drawImage(app.playerWingImage, app.playerWingX, app.playerWingY, 
                width = app.playerWingWidth, height = app.playerWingHeight)
        drawImage(app.playerImage, app.playerX, app.playerY, 
                width = app.playerWidth, height = app.playerHeight)

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
    if(abs(app.player['x'].currentVelocity) < 0.5):
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
        app.player['y'].previousVelocity = 0
    runPlayerVelocityCalculations(app,'y')

    # SHORTEN ONCE FINISHED
    for tileableImageName in ['background','midground','ground']:
        app.ti[tileableImageName].xOffset += (app.player['x'].currentVelocity)
        if((app.ti[tileableImageName].yOffset + (app.player['y'].currentVelocity)) >= 0):
            app.ti[tileableImageName].yOffset +=(app.player['y'].currentVelocity)
        else:
            app.ti[tileableImageName].yOffset = 0
            app.player['y'].previousVelocity = 0
            # special check to make sure the lightmap actually shows that we 
            # are on the ground when the player is on the ground
            if(app.lightmapYOffset != 0):
                updateLightmap(app,True)
    for lightSource in app.lightSources:
        lightSource.x -= ((app.player['x'].currentVelocity)/app.lightmapScalingFactor)
        if((app.ti['ground'].yOffset + (app.player['y'].currentVelocity)) >= 0):
            lightSource.y += ((app.player['y'].currentVelocity)/app.lightmapScalingFactor)
        else:
             # always update lightmap the moment the player returns to the ground
            lightSource.y = lightSource.initialY

    for projectileName in app.activeMapProjectiles:
        app.projectile[projectileName].xOffset -= (app.player['x'].currentVelocity)
        app.projectile[projectileName].yOffset = app.ti['ground'].yOffset

# TILEABLE IMAGES
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
        (app.screenWidth-tileableImageWidth)/2)
    
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

# LIGHTING
def lightmapSetup(app):
    app.lightmapScalingFactor = 50
    app.lightmapBuffer = 100
    app.lightmapMatrixX = int(app.screenWidth/app.lightmapScalingFactor)+10
    app.lightmapMatrixY = int(app.screenHeight/app.lightmapScalingFactor)+10
    app.lightmapOpacityMatrix = numpy.array([[[0,255]] * app.lightmapMatrixX]*app.lightmapMatrixY, dtype=numpy.uint8)
    app.lightmapXPosition = -(app.lightmapBuffer/5)
    app.lightmapYPosition = -(app.lightmapBuffer/5)
    print(f'{len(app.lightmapOpacityMatrix)} rows')
    print(f'{len(app.lightmapOpacityMatrix[0])} columns')

# helper function to calculate gaussian lightmap map
def calculateLightmapGaussian(x,y,lightSources,opacityOffset):
    lightsourceMaxIntensity = 255
    opacity = 255
    # arbitrady adjusted value for calculation distance cutoff
    # it is unnessecary to calculate the effects of a light source on a point
    # if that light source is definitely too far away to have an effect
    # having a distance cutoff saves computation time
    maxDistance = 1000
    for lightSource in lightSources:
        if(getDistance(x,y,lightSource.x,lightSource.y) < maxDistance):
            opacity -= int((lightSource.intensity)*((lightsourceMaxIntensity)**((-1*(((x-lightSource.x)**2)/(2*((lightSource.spread)**2))))-(((y-lightSource.y )**2)/(2*((lightSource.spread)**2))))))
    return [0,min(max((opacity+opacityOffset),0),255)]

def updateLightmap(app,groundCheck):
    # these if statements aren't techanically nessecary but it much better 
    # helps me see the conditions under which the lightmap should update
    updateLightmap = False
    if(len(app.lightSources) > 0):
        for lightSource in app.lightSources:
            if(((((0-(app.lightmapBuffer*lightSource.spread))/app.lightmapScalingFactor)) <= lightSource.x <= (int((app.screenWidth+(app.lightmapBuffer*lightSource.spread))/app.lightmapScalingFactor))) and (((0-(app.lightmapBuffer*lightSource.spread))/app.lightmapScalingFactor) <= lightSource.y <= (int((app.screenHeight+(app.lightmapBuffer*lightSource.spread))/app.lightmapScalingFactor)))):
                # print('inbounds')
                # print('lightSource.x: ',lightSource.x)
                # print('lightSource.y: ',lightSource.y)
                updateLightmap = True
                # print('trigger 0')
    if(0 < app.ti['ground'].yOffset < app.screenHeight-app.ti['ground'].initialTileYPosition):
        updateLightmap = True
        # print('trigger 1')
    if(0 < app.lightmapYOffset < app.screenHeight-app.ti['ground'].initialTileYPosition):
        updateLightmap = True
        # print('trigger 2')
    if(groundCheck):
        updateLightmap = True
        # print('trigger 3')
        # ptc('app.lightmapYOffset',app.lightmapYOffset)    

    # ptc('app.lightmapYOffset',app.lightmapYOffset)    

    if(updateLightmap and (app.lightmapUpdateCounter % app.lightmapUpdateRate == 0)):
        for y in range(app.lightmapMatrixY):
            app.lightmapYOffset = app.ti['ground'].yOffset
            groundY = app.ti['ground'].yOffset+app.ti['ground'].initialTileYPosition
            if(y < groundY/app.lightmapScalingFactor):
                opacityOffset = -app.backgroundBrightness
            else:
                # tuned value that determines how far down the light from the room
                # permeates the ground tiles
                floorLightPermeabilityConstant = 10
                opacityOffset = -app.backgroundBrightness + y*floorLightPermeabilityConstant
                # print(opacityOffset)
            for x in range(app.lightmapMatrixX):
                app.lightmapOpacityMatrix[y,x] = calculateLightmapGaussian(x,y,app.lightSources,opacityOffset)
        lightmap = Image.fromarray(app.lightmapOpacityMatrix, mode = 'LA')
        app.lightmapImage = CMUImage(lightmap)
    app.lightmapUpdateCounter += 1
    # ptc('app.lightmapUpdateCounter',app.lightmapUpdateCounter)

def updateLightsources(app):
    i = 0
    while i < len(app.lightSources):
        if(app.lightSources[i].intensity == 0):
            app.lightSources.pop(i)
            print('# of active light soures: ',len(app.lightSources))
        else:
            app.lightSources[i].intensity = int(math.floor((app.lightSources[i].intensity * app.lightSources[i].fadeRate)*100)/100)
            i+=1

def drawLightmap(app):
    drawImage(app.lightmapImage,app.lightmapXPosition,app.lightmapYPosition,width = (app.lightmapMatrixX*app.lightmapScalingFactor),height = (app.lightmapMatrixY*app.lightmapScalingFactor),opacity=app.lightmapOpacity)

# SPELL ORB
def updateSpellOrb(app):

    # update image
    if(app.spellOrbCharged):
        app.spellOrbImage = 'images/spellOrbs/spellOrbCharged.png'
    else:
        app.spellOrbImage = 'images/spellOrbs/spellOrbUncharged.png'

    # update position
    app.spellOrbXOffset += (((app.player['x'].currentVelocity)/app.spellOrbDampingCoefficient))-((app.spellOrbInitialX-app.spellOrbXPosition)/app.spellOrbDriftConstant)
    if(abs(app.spellOrbXOffset) < 0.5):
        app.spellOrbXOffset = 0
    # print(app.spellOrbXOffset)
    app.spellOrbYOffset = -(abs(app.spellOrbXOffset*2)**(0.5))
    app.spellOrbXPosition = app.spellOrbInitialX - app.spellOrbXOffset
    app.spellOrbYPosition = app.spellOrbInitialY - app.spellOrbYOffset

    # update rotation
    if(app.playerFacing == 'right'):
        app.spellOrbRotationAngle += app.spellOrbRotationSpeed
    else:
        app.spellOrbRotationAngle -= app.spellOrbRotationSpeed

def drawSpellOrb(app):
    drawImage(app.spellOrbImage,app.spellOrbXPosition,app.spellOrbYPosition, width = int(app.spellOrbImageSize * app.spellOrbScalingFactor), height = int(app.spellOrbImageSize * app.spellOrbScalingFactor), align = 'center', rotateAngle = app.spellOrbRotationAngle)

# SPELL CASTING

# gets the side of the orb that the mouse pointer is at the point of casting
def getMouseOrbSide(app,mouseX):
    if mouseX >= app.spellOrbXPosition:
        app.mouseOrbSide = 'right'
    else:
        app.mouseOrbSide = 'left'

# charges the spell, and initiates the spell in the active spells list
def chargeSpell(app,spellName):
    if(app.spellOrbCharged):
        return
    else:
        try:
            app.activeSpells = [app.spells[spellName]]
            app.spellOrbCharged = True
            app.drawingSpell = False
        except:
            reportError('initiating spell', 
                        'INVALID SPELL', 'chargeSpell', 
                        'spell name', (spellName), 'reference appStart to find ' \
                        'valid spells')

# enables the spell casting animation itself, and calculates the apropriate 
# angle for the spell animation to cast
def initiateSpellCast(app,spellName,targetX,targetY):
    if(app.castSpellNow):
        return
    try:
        app.spells[spellName].targetX = targetX
        app.spells[spellName].targetY = targetY
    except:
        reportError('initiating spell', 
                        'INVALID SPELL', 'intiateSpellCast', 
                        'spell name', (spellName), 'reference appStart to ' \
                        'find valid spells')
        
    if(app.spells[spellName].displayType == 'endEffect'):
        distanceToTarget = getDistance(app.spellOrbXPosition,app.spellOrbYPosition,targetX,targetY)
        dx = (targetX - app.spellOrbXPosition)
        if(dx == 0):
            dx = 0.00001
        dy = (targetY - app.spellOrbYPosition)
        displayAngle = math.degrees(math.atan(dy/dx))
        app.spells[spellName].displayAngle = displayAngle
        # print(app.spells[spellName].displayAngle)
        app.spells[spellName].displayWidth = distanceToTarget
        xPositionRotationOffset = math.sin(math.atan(dy/dx)/2)*math.sin(math.atan(dy/dx)/2)*distanceToTarget
        yPositionRotationOffset = math.cos(math.atan(dy/dx)/2)*math.sin(math.atan(dy/dx)/2)*distanceToTarget
        # ptc('xPositionRotationOffset',xPositionRotationOffset)
        # ptc('yPositionRotationOffset',yPositionRotationOffset)
        if(app.mouseOrbSide == "right"):
            app.spells[spellName].xPosition = app.spellOrbXPosition - xPositionRotationOffset + (distanceToTarget)/2
            app.spells[spellName].yPosition = app.spellOrbYPosition + yPositionRotationOffset
        else: 
            app.spells[spellName].xPosition = app.spellOrbXPosition + xPositionRotationOffset - (distanceToTarget)/2
            app.spells[spellName].yPosition = app.spellOrbYPosition - yPositionRotationOffset
        # imageXYRatio = app.spells[spellName].imageHeight / app.spells[spellName].imageWidth
        app.spells[spellName].displayHeight = app.spells[spellName].imageHeight

    elif(app.spells[spellName].displayType in app.projectileTypeList):
        # get initial data from spell setup
        frames = app.spells[spellName].animationFrames
        width = app.spells[spellName].imageWidth
        height = app.spells[spellName].imageHeight
        scale = app.spells[spellName].imageScale
        initialX = app.spellOrbXPosition
        initialY = app.spellOrbYPosition
        # create projectile instances using spell data
        print('projectile Type:',app.spells[spellName].projectileType)
        if(app.spells[spellName].projectileType == "linear"):
            app.projectile[spellName] = linear(spellName,frames,width,height,scale,0,initialX,initialY,targetX,targetY,True)
        elif(app.spells[spellName].projectileType == "groundbounce"):
            app.projectile[spellName] = groundbounce(spellName,frames,width,height,scale,0,initialX,initialY,targetX,targetY,True)
        getProjectileData(app,spellName)
        # register each projectile as either a map or player projectile
        # if projectile is a map projectile we have to set it's initial 
        # velocity to the player's velocity at the time of casting
        if(app.spells[spellName].displayType == 'mapProjectile'):
            app.activeMapProjectiles.append(app.spells[spellName].name)
            print('added projectile:',spellName,'to active map projectiles')
            if(app.playerFacing == 'right'):
                app.projectile[spellName].xVelocity = (app.player['x'].currentVelocity)/5
                app.projectile[spellName].yVelocity = (-app.player['y'].currentVelocity)/5
            else:
                app.projectile[spellName].xVelocity = -app.player['x'].currentVelocity
                app.projectile[spellName].yVelocity = -app.player['y'].currentVelocity
        elif(app.spells[spellName].displayType == 'playerProjectile'):
            app.activePlayerProjectiles.append(app.spells[spellName].name)
            print('added projectile:',spellName,'to active player projectiles')

    else:
        reportError('initiating spell', 'INVALID SPELL DISPLAY TYPE', 
                    'intiateSpellCast', 'display type', 
                    app.spells[spellName].displayType, None)
    
    # start casting spell 
    app.castSpellNow = True

# plays the spell animation, and removes the spell from app.activeSpells when
# the spell is finished, as well as calls activateSpellEffect ON THE LAST FRAME
def castSpell(app,spellName):
    # print('casting Spell')
    if(app.spells[spellName].displayType == 'endEffect'):
        spellDirection = app.mouseOrbSide[0].upper()+app.mouseOrbSide[1:]
        if(app.spells[spellName].animationCounter == (app.spells[spellName].animationFrames - 1)):
            activateSpellEffect(app,spellName)
        elif(app.spells[spellName].animationCounter == (app.spells[spellName].animationFrames)):
            app.spells[spellName].animationCounter = 0
            app.spellOrbCharged = False
            app.drawingSpell = False
            app.activeSpells = []
            return
    elif(app.spells[spellName].displayType in app.projectileTypeList):
        app.spells[spellName].animationCounter %= app.spells[spellName].animationFrames
        if(app.spells[spellName].projectileType == "linear"):
            atDestination = app.projectile[spellName].move()
            if(atDestination):
                activateSpellEffect(app,spellName)
                app.spells[spellName].animationCounter = 0
                app.drawingSpell = False
                app.spellOrbCharged = False
                app.activeSpells = []
                app.projectile[spellName].deleteMe = True
        elif(app.spells[spellName].projectileType == "groundbounce"):
            timerUp = app.projectile[spellName].move()
            if(timerUp):
                activateSpellEffect(app,spellName)
                app.spells[spellName].animationCounter = 0
                app.drawingSpell = False
                app.spellOrbCharged = False
                app.activeSpells = []
                app.projectile[spellName].deleteMe = True
        # determining spell travel direction
        if(app.projectile[spellName].xVelocity >= 0):      
            spellDirection = 'Right'
        else:
            spellDirection = 'Left'
        # assigning spell as either an active map or player projectile

    else:
        reportError('initiating spell', 'INVALID SPELL DISPLAY TYPE', 
                    'castSpell', 'display type', 
                    app.spells[spellName].displayType, None)
    # print(spellDirection)
    app.spellDisplayImage = f'images/spells/{spellName}{spellDirection}_{app.spells[spellName].animationCounter}.png'
    if(app.spells[spellName].displayType in app.projectileTypeList):
        app.projectile[spellName].displayImage = app.spellDisplayImage
    app.spells[spellName].animationCounter += 1
    # print('spell animationCounter:', app.spells[spellName].animationCounter)
    app.drawingSpell = True

# actually draws the spell animation sprite
def drawSpell(app,spellName):
    if(app.spells[spellName].projectileType == None):
        drawImage(app.spellDisplayImage,app.spells[spellName].xPosition,app.spells[spellName].yPosition,width = app.spells[spellName].displayWidth, height = app.spells[spellName].displayHeight, align='center',rotateAngle = app.spells[spellName].displayAngle)

# actually plays the effect of the spell
def activateSpellEffect(app,spellName):
    if(spellName == 'testLightSpell'):
        app.lightSources.append(lightSource(3,255,(app.spells[spellName].targetX/app.lightmapScalingFactor),(app.spells[spellName].targetY/app.lightmapScalingFactor),(app.spells[spellName].targetY/app.lightmapScalingFactor),0.95))
    if(spellName == 'testBall'):
        print('YIPPEE!!')

# PROJECTILE MANAGEMENT

# big helper function to just assign all of the data needed for different 
# projectile behaviors

def drawProjectile(app,projectileName):
    app.projectile[projectileName].displayWidth = int(app.projectile[projectileName].imageWidth*app.projectile[projectileName].imageScale)
    app.projectile[projectileName].displayHeight = int(app.projectile[projectileName].imageHeight*app.projectile[projectileName].imageScale)
    # print(f'projectile: {projectileName}, image: {app.projectile[projectileName].displayImage}')
    # print('xPosition:',app.projectile[projectileName].xPosition)
    # print('yPosition:',app.projectile[projectileName].yPosition)
    if(app.projectile[projectileName].displayImage != None):
        totalXPosition = (app.projectile[projectileName].xPosition+app.projectile[projectileName].xOffset)
        totalYPosition = (app.projectile[projectileName].yPosition+app.projectile[projectileName].yOffset)
        # print('totalYPosition:',totalYPosition)
        drawImage(app.projectile[projectileName].displayImage,totalXPosition,totalYPosition,width = app.projectile[projectileName].displayWidth, height = app.projectile[projectileName].displayHeight, align='center',rotateAngle = app.projectile[projectileName].displayAngle)

def updateProjectiles(app):
    # update active map projectiles
    for projectileName in app.activeMapProjectiles:
        if(not app.projectile[projectileName].isPlayerSpell):
            pass
            # actually update projectile state
        if(app.projectile[projectileName].deleteMe):
            app.activeMapProjectiles.remove(projectileName)
            del app.projectile[projectileName]
            print('removed map projectile:',projectileName)
    # update active player projectiles
    for projectileName in app.activePlayerProjectiles:
        if(not app.projectile[projectileName].isPlayerSpell):
            pass
            # actually update projectile state
        if(app.projectile[projectileName].deleteMe):
            app.activePlayerProjectiles.remove(projectileName)
            del app.projectile[projectileName]
            print('removed player projectile:', projectileName)

def getProjectileData(app,projectileName):
    if(projectileName == 'testBall'):
        app.projectile[projectileName].directionalAcceleration = 0.5
        app.projectile[projectileName].nearnessFactor = 25
        app.projectile[projectileName].maxVelocity = 5
    elif(projectileName == 'levelOneSlimeBall'):
        app.projectile[projectileName].directionalVelocity = 10
        app.projectile[projectileName].lifespan = app.stepsPerSecond * 3
        app.projectile[projectileName].maxBounces = 5
        app.projectile[projectileName].gravitationalAcceleration = 1
        app.projectile[projectileName].groundYIndex = app.ti['ground'].initialTileYPosition
        app.projectile[projectileName].initialYOffset = app.ti['ground'].yOffset
        app.projectile[projectileName].reboundCoefficient = 0.8

# COMBO MANAGEMENT

def setupCombos(app):
    app.fullComboList = []
    app.fullLetterList = []
    for spell in app.spells:
        currentCombo = app.spells[spell].combo
        print('current spell:',app.spells[spell].name)
        for letter in currentCombo:
            if(not letter in app.fullLetterList):
                app.fullLetterList.append(letter)
        app.fullComboList.append(currentCombo)
    ptc('app.fullComboList',app.fullComboList)
    ptc('app.fullLetterList',app.fullLetterList)

# helper function to detect if our combo in progress is part of any 
# full combo that we actually have
def matchesCombo(app):
    combosIn = 0
    for possibleCombo in app.fullComboList:
        letterMatch = True
        for i in range(len(app.comboInProgress)):
            if(app.comboInProgress[i] != possibleCombo[i]):
                letterMatch = False
                break
        if(letterMatch):
            combosIn += 1
            # print(f'comboInProgrgress {app.comboInProgress} is in full combo {possibleCombo}!')
            if(app.comboInProgress == possibleCombo):
                print('combo complete!',app.comboInProgress,'is',possibleCombo)
                return app.comboInProgress
    return(combosIn > 0)

def detectCombos(app,currentKey):
    if(not app.spellOrbCharged):
        app.comboInProgress += currentKey
        ptc('comboInProgress',app.comboInProgress)
        comboMatched = matchesCombo(app)
        if(comboMatched == False):
            print('combo failed!')
            app.comboInProgress = ''
        elif(comboMatched != True):
            for spell in app.spells:
                if(comboMatched == app.spells[spell].combo):
                    print(f'charging spell {app.spells[spell].name} with corresponding combo {comboMatched}. ({comboMatched} = {app.spells[spell].combo})')
                    chargeSpell(app,app.spells[spell].name)
                    app.comboInProgress = ''

# APP EVENT HANDLERS
def onKeyPress(app,key):
    # enable/disable temporary display readout
    if(key == 'p'):
        if(app.tempDisplayReadout):
            app.tempDisplayReadout = False
        else:
            app.tempDisplayReadout = True

    if(key in app.fullLetterList):
        detectCombos(app,key)

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
    if((('d' in keys) or ('a' in keys)) or (('w' in keys) or ('s' in keys))):
        updateLightmap(app,False)
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
                app.player['y'].currentThrust = (app.player['y'].setThrust-int((app.playerWingCounter/(app.maxPlayerWingCounter/10))**3)-app.setGravity)
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

def onMousePress(app,mouseX,mouseY, button):
    # testing lighting engine
    # app.lightSources.append(lightSource(2,255,(mouseX/app.lightmapScalingFactor),(mouseY/app.lightmapScalingFactor),(mouseY/app.lightmapScalingFactor),0.95))
    # if(button == 0):
    #     chargeSpell(app,'testLightSpell')
    if((button == 2) and (len(app.activeSpells) == 1)):
        # print(app.activeSpells)
        initiateSpellCast(app,app.activeSpells[0].name,mouseX,mouseY)

def onMouseRelease(app,mouseX,mouseY):
    pass

def onMouseMove(app,mouseX,mouseY):
    if(not(app.castSpellNow)):
        getMouseOrbSide(app,mouseX)

def onStep(app):
    updatePlayerImage2(app)
    for tileableImageName in ['background','midground','ground']:
        updateTiles(app,tileableImageName)
    updatePlayerVelocity(app)
    updateLightmap(app,False)
    updateLightsources(app)
    if(app.castSpellNow):
        if(len(app.activeSpells) == 1):
            for spell in app.activeSpells:
                castSpell(app,spell.name)
        else:
            app.castSpellNow = False
    updateSpellOrb(app)
    updateProjectiles(app)

def redrawAll(app): 
    # ['background','midground','ground']
    for tileableImageName in ['background','midground','ground']:
        drawTiles(app,tileableImageName)
    drawPlayer(app)
    drawSpellOrb(app)
    drawLightmap(app)
    for spell in app.activeSpells:
        if(app.drawingSpell):
            drawSpell(app,spell.name)
    for projectile in app.activeMapProjectiles:
        drawProjectile(app,app.projectile[projectile].name)
    for projectile in app.activePlayerProjectiles:
        drawProjectile(app,app.projectile[projectile].name)
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

# APP SETUP
def appSetup(app):

    # ---- WINDOW SETUP ----

    # establishing screen width
    app.screenWidth = 1000
    app.screenHeight = 750

    # setting the left and right bounds of the screen
    # should be set a little ways beyond the visible edge of the screen
    # to ensure tiles are displayed properly
    app.screenLeft = -130
    app.screenRight = app.screenWidth + 5
    app.screenTop = 0
    app.screenBottom = app.screenHeight

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
    app.ti['background'].image = 'images/background/background_1.png'
    app.ti['midground'].image = 'images/midground/midground_1.png'
    app.ti['ground'].image = 'images/ground/ground_1.png'
    
    # parallax coefficients change how much each tiled image moves for a 
    # change in xOffset
    app.ti['background'].parallaxCoefficient = 17
    app.ti['midground'].parallaxCoefficient = 5
    app.ti['ground'].parallaxCoefficient = 1

    # opacity determines how transparent one of the tileable images should be
    # they are set to 100 by default
    app.ti['background'].opacity = 100
    app.ti['midground'].opacity = 75
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

    # sets first player wing image to show, and establishing X and Y offsets
    app.playerWingImageIndex = [0,0,-1]
    app.playerWingXOffset = 0
    app.playerWingYOffset = 0

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
    app.playerMass = 30
    app.player['x'].setThrust = 750
    app.player['x'].setFrictionConstant = -20
    app.player['x'].frictionConstant = -20
    app.player['y'].setThrust = 750
    app.player['y'].setFrictionConstant = -15
    app.player['y'].frictionConstant = -15
    app.setGravity = -150
    driftConstant = 135 # used to tune how quickly a player falls while gliding
    app.playerGlideThrust = -app.setGravity - driftConstant

    # value for player wing counter is manually set to determine the ammount of 
    # time for which wings can provide upwards lift
    app.maxPlayerWingCounter = 5000

    # indicates what state the player is in
    # current states: 'ground', 'air', 'slide', 'roll'
    app.playerState = 'ground'

    # indicates the direction the player is facing
    app.playerFacing = 'right'

    # intializes player counters to 0
    app.playerAnimationCounter = 0
    app.playerWingAnimationCounter = 0
    app.playerWingCounter = 0
    
    # ---- SPELL ORB SETUP ----

    # establshing charged state of spell orb
    app.spellOrbCharged = False

    # initializing spell orb offset and position variables
    app.spellOrbXPosition = 0
    app.spellOrbYPosition = 0
    app.spellOrbXOffset = 0
    app.spellOrbYOffset = 0
    app.spellOrbInitialX = (app.screenWidth // 2)
    app.spellOrbInitialY = (app.screenHeight // 2) - 95

    # setting up spell orb rotation
    app.spellOrbRotationAngle = 0
    app.spellOrbRotationSpeed = 1

    # spell orb drift constant, controls how far away the orb drifts from the 
    # player when they are moving - larger = farther drift
    app.spellOrbDriftConstant = 10

    # spell orb damping constant, controls how much the player's velocity 
    # affects the orb, higher is less effect
    app.spellOrbDampingCoefficient = 5

    # setting up image paramanetrs for spell orb
    app.spellOrbImageSize = 500 # 500 x 500 pixel square
    app.spellOrbScalingFactor = 0.0625

    # ---- SPELL CASTING SETUP ---
    class spell:
        def __init__(self,combo,name,displayType,frames,imageWidth,imageHeight,imageScale):
            self.combo = combo
            self.name = name
            # spells can have (as of right now) one of three display types
            # 'endEffect' is an animation that displays from the spell orb to a
            # location and causes some effect at the end
            # 'playerProjectile' spawns a projectile that moves relative to 
            # the player
            # 'mapProjectile' spawns a projectile that moves relative to the map
            self.displayType = displayType
            # projectile type specifices which subclass of the projectile
            # superclass should be referenced.
            # currently avaiable projectile types are:
            # - linear
            # - groundbounce
            self.projectileType = None
            self.animationFrames = frames
            self.animationCounter = 0
            self.imageWidth = imageWidth
            self.imageHeight = imageHeight
            self.imageScale = imageScale
            self.displayWidth = 0
            self.displayHeight = 0
            self.displayAngle = 0
            self.xPosition = 0
            self.yPosition = 0
            self.targetX = 0
            self.targetY = 0

    # initializing spell dictionary
    app.spells = dict()

    # establishing usable spellsr
    app.spells['testLightSpell'] = spell('rfv','testLightSpell','endEffect',9,500,250,1)
    app.spells['testBall'] = spell('rtf','testBall','playerProjectile',2,250,250,0.25)
    app.spells['testBall'].projectileType = 'linear'
    app.spells['levelOneSlimeBall'] = spell('grtf','levelOneSlimeBall','mapProjectile',1,250,250,0.2)
    app.spells['levelOneSlimeBall'].projectileType = 'groundbounce'
    # setting up spell display image
    app.spellDisplayImage = ''

    # setting up the list of currently active spells
    # this list should only ever contain the current active spell or no spells
    app.activeSpells = []

    # establishing the spell drawing enabler
    app.drawingSpell = False

    # establishing the spell casting enabler
    app.castSpellNow = False

    # establishing signifier that tells which side of the screen the mouse is on
    app.mouseOrbSide = 'right'

    # initiating combo in progress tracker
    app.comboInProgress = ''

    # ---- PROJECTILE SETUP ----

    # initilzing BASE projectile class
    # --> DONE GLOBALLY     

    # initialzing linear projectile class - moves in a straight line
    # --> DONE GLOBALLY         

    # initializing projectile dictionary
    app.projectile = dict()

    # initilaizing list of projectile types
    app.projectileTypeList = ['playerProjectile','mapProjectile']

    # intilalizing lists of active map projectiles and player projectiles
    app.activeMapProjectiles = []
    app.activePlayerProjectiles = []

    # ---- LIGHTING SETUP ----

    # initliaizing light source class
    # --> DONE GLOBALLY
    
    # iniializing light sources list
    app.lightSources = []

    # establishing lighting opacity
    app.lightmapOpacity = 100

    # establishing lightmap buffer (help overcome tiling artifacts)
    app.lightmapBuffer = 10

    # lighting image counter (i hate this but i have to figure out how to make
    # app.draw actually update itself... same problem where it always draws
    # the first image it ever drew for something)
    app.lightmapImageCounter = 0

    # establishing lightmap update counter (lightmap does not have to update
    # every single time it is called, instead it can update once ever
    # lightmapUpdateRate ticks
    app.lightmapUpdateCounter = 0
    app.lightmapUpdateRate = 5

    # setting up lightmap Y offset
    app.lightmapYOffset = 0

    # establishing background brightness setting
    app.backgroundBrightness = 175

    # ---- APP SETUP ----

    # setting the framerate
    app.stepsPerSecond = 60

    # ---- TEMP DEBUG ----

    # misc testing setup
    # app.testWalkSpeed = 10
    # app.screenLeft = 100
    # app.screenRight = app.screenWidth - 100

     # set to True to enable readout, set to False to disable
    app.tempDisplayReadout = False

    # Finalization - run the contents of appStep to update everything prior 
    # to running. DO NOT RUN onStep() ITSELF!
    updatePlayerImage2(app)
    for tileableImageName in ['background','midground','ground']:
        updateTiles(app, tileableImageName)
    updatePlayerVelocity(app)
    lightmapSetup(app)
    app.lightSources.append(lightSource(1,0,0,0,0,0.9))
    updateLightmap(app,False)
    updateSpellOrb(app)
    setupCombos(app)

# MAIN()
def main():
    appSetup(app)
    runApp(width = app.screenWidth, height = app.screenHeight)

main()

# total hours spent working here: ~56