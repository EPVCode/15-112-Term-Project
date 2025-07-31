# Name: Eduardo Phelan-Vidal
# AndrewID: esphelan
# Section: A

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
# random used for screenshake
import random

# CLASSES
# ---- LIGHTING ----
# intilaizing light soure class
class LightSource:
    def __init__(self,spread,intensity,x,y,fadeRate):
        self.spread = spread
        self.intensity = intensity
        self.x = x
        self.y = y
        self.initialY = y
        self.counter = 0
        self.fadeRate = fadeRate
    def fade(self):
        self.intensity *= self.fadeRate

# ---- SPELLS ---- 
class Spell:
    def __init__(self,spellType,combo,name,displayType,frames,imageWidth,
                 imageHeight,imageScale,manaCost,drawBuffer):
        # spells types can be 'aggressive' or 'defensive' 
        # one aggressive and one defensive spell can exist at a time
        # but you cannot cast one while the other is active
        self.spellType = spellType
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
        # - pointHoming
        # - stationary
        self.projectileType = None
        self.animationFrames = frames
        self.animationCounter = 0
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.imageScale = imageScale
        self.displayWidth = int(imageWidth * imageScale)
        self.displayHeight = int(imageHeight * imageScale)
        self.displayAngle = 0
        self.xPosition = 0
        self.yPosition = 0
        self.targetX = 0
        self.targetY = 0
        self.manaCost = manaCost
        self.directional = False
        self.drawBuffer = drawBuffer
        self.opacity = 100

# ---- PROJECTILES ----
# initilzing BASE projectile class
class Projectile:
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,
                 displayAngle,drawBuffer,initialX,initialY,targetX,
                 targetY,isPlayerSpell):
        self.name = name
        self.animationFrames = frames
        self.animationFrameList = []
        self.animationCounter = 0
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.imageScale = imageScale
        self.displayWidth = int(imageWidth * imageScale)
        self.displayHeight = int(imageHeight * imageScale)
        self.drawBuffer = drawBuffer
        self.imagePath = None
        self.displayAngle = displayAngle
        self.xPosition = initialX
        self.yPosition = initialY
        self.initialX = initialX
        self.initialY = initialY
        self.targetX = targetX
        self.targetY = targetY
        self.xVelocity = 0
        self.yVelocity = 0
        self.directionalVelocity = 0
        self.inheritPlayerVelocity = False
        self.deleteMe = False
        self.isPlayerSpell = isPlayerSpell
        self.initialYOffset = 0
        self.xOffset = 0
        self.yOffset = 0
        self.damage = 0
        self.ignoreScreenBounds = False
        # adding all hitbox parameters evey though all of them will not be used
        # is there another way around this?
        self.radius = 0
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        self.xAdjustment = 0
        self.yAdjustment = 0
        
# initialzing linear projectile class - moves in a straight line
class Linear(Projectile):
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,
                 displayAngle,drawBuffer,initialX,initialY,targetX,
                 targetY,isPlayerSpell):
        super().__init__(name,frames,imageWidth,imageHeight,imageScale,
                         displayAngle,drawBuffer,initialX,initialY,targetX,
                         targetY,isPlayerSpell)
        self.directionalAcceleration = 0
        self.maxTravel = 0
        self.maxVelocity = 0
        self.directionAngle = None

    def update(self):
        return self.move()
    
    def move(self):
        if(self.directionAngle == None):
            dx = (self.xPosition - self.targetX)
            dy = (self.yPosition - self.targetY)
            # print(dy)
            # print(dx)
            self.maxTravel = getDistance(self.xPosition,self.yPosition,
                                         self.targetX,self.targetY)
            # ptc('hypotenuse',self.maxTravel)
            if(self.maxTravel == 0):
                self.maxTravel = 0.001
            if(dx > 0):
                self.directionAngle = (math.radians(180) + 
                                       (math.asin((dy)/self.maxTravel)))
            else:
                self.directionAngle = (math.asin((-dy)/self.maxTravel))
            self.displayAngle = math.degrees(self.directionAngle)

        self.directionalVelocity += self.directionalAcceleration
        if(abs(self.directionalVelocity) > self.maxVelocity):
            if(self.directionalVelocity > 0):
                self.directionalVelocity = self.maxVelocity
            elif(self.directionalVelocity < 0):
                self.directionalVelocity = -self.maxVelocity
            else:
                self.directionalVelocity = 0

        self.xVelocity = (math.cos(self.directionAngle) * 
                          self.directionalVelocity)
        self.yVelocity = (math.sin(self.directionAngle) * 
                          self.directionalVelocity)

        self.xPosition += self.xVelocity
        self.yPosition += self.yVelocity

        # print('projectile name:',self.name)
        # ptc('self.xPosition',self.xPosition)
        # ptc('self.yPosition',self.yPosition)
        # ptc('y offset:',self.yOffset)

        distanceTravelled = getDistance(self.xPosition,self.yPosition,
                                        self.initialX,self.initialY)
        # print(distanceTravelled)

        return (distanceTravelled >= self.maxTravel)

class Stationary(Projectile):
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,
                 displayAngle,drawBuffer,initialX,initialY,targetX,targetY,
                 isPlayerSpell,lifespan):
        super().__init__(name,frames,imageWidth,imageHeight,imageScale,
                         displayAngle,drawBuffer,initialX,initialY,targetX,
                         targetY,isPlayerSpell)
        self.lifespan = lifespan
        self.timer = 0

    def update(self):
        self.imagePath = (self.animationFrameList[
            (self.timer % len(self.animationFrameList))])
        self.timer += 1 
        return (self.timer % self.lifespan) == 0

# initializing pointHoming projectile class - homes towards a initial point
class PointHoming(Projectile):
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,
                 displayAngle,drawBuffer,initialX,initialY,targetX,
                 targetY,isPlayerSpell):
        super().__init__(name,frames,imageWidth,imageHeight,imageScale,
                         displayAngle,drawBuffer,initialX,initialY,targetX,
                         targetY,isPlayerSpell)
        self.directionalAcceleration = 0
        self.nearnessFactor = 0
        self.damping = 0
        self.maxVelocity = 0
        self.directionAngle = None

    def update(self):
        return self.move()

    def move(self):
        dx = (self.xPosition - self.targetX)
        dy = (self.yPosition - self.targetY)
        # print(dy)
        # print(dx)
        distance = getDistance(self.xPosition,self.yPosition,self.targetX,
                               self.targetY)
        # ptc('distance',distance)
        if(distance == 0):
            distance = 0.001
        if(dx > 0):
            self.directionAngle = math.radians(180) + (math.asin((dy)/distance))
        else:
            self.directionAngle = (math.asin((-dy)/distance))

        # print('directionAngle',self.directionAngle)
        self.directionalVelocity += self.directionalAcceleration
        if(abs(self.directionalVelocity) > self.maxVelocity):
            if(self.directionalVelocity > 0):
                self.directionalVelocity = self.maxVelocity
            elif(self.directionalVelocity < 0):
                self.directionalVelocity = -self.maxVelocity
            else:
                self.directionalVelocity = 0
        self.xVelocity += (math.cos(self.directionAngle) * 
                           self.directionalVelocity)
        self.yVelocity += (math.sin(self.directionAngle) * 
                           self.directionalVelocity)
        # print('xAcceleration:',xAcceleration)
        # print('yAcceleration:',yAcceleration)
        # if distance < (self.nearnessFactor*3):
        #     # print('braking')
        #     self.xVelocity *= 0.5
        #     self.yVelocity *= 0.5
        self.xVelocity *= (1 - ((1/distance) * self.damping))
        self.yVelocity *= (1 - ((1/distance) * self.damping))

        self.xPosition += self.xVelocity
        self.yPosition += self.yVelocity

        self.displayAngle = math.degrees(self.directionAngle)

        atDestination = (distance < self.nearnessFactor) or abs(distance)>1000
        # print(atDestination)
        return atDestination

# initializing groundbounce projectile class - fires upwards then bounces
class Groundbounce(Projectile):
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,
                 displayAngle,drawBuffer,initialX,initialY,targetX,
                 targetY,isPlayerSpell):
        super().__init__(name,frames,imageWidth,imageHeight,imageScale,
                         displayAngle,drawBuffer,initialX,initialY,targetX,
                         targetY,isPlayerSpell)
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

    def update(self):
        return self.move()

    def move(self):
        if(self.directionAngle == None):
            self.yPosition -= self.initialYOffset
            self.targetY -= self.initialYOffset
            dx = (self.xPosition - self.targetX)
            if(dx == 0):
                dx = 0.001
            dy = (self.yPosition - self.targetY)
            self.directionAngle = math.degrees(math.atan(dy/dx))
            # print('directionAngle',self.directionAngle)
            if(dx < 0):
                self.castRight = True
                self.xVelocity += (math.cos(math.radians(self.directionAngle)) 
                                   * self.directionalVelocity)
                self.yVelocity += (math.sin(math.radians(self.directionAngle)) *
                                    self.directionalVelocity)
            elif(dx > 0):
                self.castRight = False
                self.xVelocity += (math.cos(math.radians(self.directionAngle)) *
                                    self.directionalVelocity)
                self.yVelocity -= (math.sin(math.radians(self.directionAngle)) *
                                    self.directionalVelocity)
        
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
        # print('current distance from ground:',
        # self.groundYIndex - self.yPosition)
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

        return ((self.timer >= self.lifespan) or 
                (self.bounces >= self.maxBounces))
    
# setting up class for the laser beam attack in particular
class InsidiousCreatureLaser:
    def __init__(self,app,name,xOffset,yOffset):
        # print('fired laser')
        self.fireAngleDeg = random.randint(0,360)
        self.fireAngleRad = math.radians(self.fireAngleDeg)
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.counter = 0
        self.targetingBeamWidth = 5
        self.targetingBeamHalfLength = 1500
        self.targetingBeamOpacity = 100
        self.targetingBeamCenterX = app.playerObject.centerX - self.xOffset
        self.targetingBeamCenterY = app.playerObject.centerY - self.yOffset
        self.targetingBeamX_1 = (self.targetingBeamCenterX - 
                                 (math.cos(self.fireAngleRad) * 
                                  self.targetingBeamHalfLength))
        self.targetingBeamY_1 = (self.targetingBeamCenterY - 
                                 (math.sin(self.fireAngleRad) * 
                                  self.targetingBeamHalfLength))
        self.targetingBeamX_2 = (self.targetingBeamCenterX + 
                                 (math.cos(self.fireAngleRad) * 
                                  self.targetingBeamHalfLength))
        self.targetingBeamY_2 = (self.targetingBeamCenterY + 
                                 (math.sin(self.fireAngleRad) * 
                                  self.targetingBeamHalfLength))
        self.name = name
        self.drawTargetingBeam = True
        self.initiatedProjectile = False
        self.deleteMe = False      

    def fireLaser(self,app):
        app.projectile[self.name] = Linear(
            self.name,0,500,100,3,100,0,(self.targetingBeamX_1 + self.xOffset), 
            (self.targetingBeamY_1), (self.targetingBeamX_2 + self.xOffset), 
            (self.targetingBeamY_2),False)
        app.projectile[self.name].ignoreScreenBounds = True
        app.projectile[self.name].imagePath = (
            'images/insidiousCreature/laser.png')
        # print('added projectile:',self.name,'to active map projectiles')
        app.activeMapProjectiles.append(self.name)
        initiateProjectile(app,self.name)
        
    def draw(self):
        if(self.drawTargetingBeam):
            # print('drawing laser!')
            drawLine((self.targetingBeamX_1 + self.xOffset), 
                     (self.targetingBeamY_1 + self.yOffset), 
                     (self.targetingBeamX_2 + self.xOffset), 
                     (self.targetingBeamY_2 + self.yOffset), 
                     fill = 'red', 
                     lineWidth = self.targetingBeamWidth, 
                     opacity = self.targetingBeamOpacity)

    def update(self,other,app):
        self.xOffset = other.xOffset
        self.yOffset = other.yOffset
        if(self.drawTargetingBeam):
            self.targetingBeamOpacity -= 5
            if(self.targetingBeamOpacity <= 0):
                self.drawTargetingBeam = False
                self.fireLaser(app)
    
    def __hash__(self):
        return hash(str(self))

# ---- ENEMIES ----
class Enemy:
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,
                 alignment,drawBuffer,displayAngle,initialX,initialY,
                 maxHealth,playerDamageOnHit):
        self.name = name
        self.animationFrames = frames
        self.animationCounter = 0
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.imageScale = imageScale
        self.alignment = alignment
        self.displayWidth = int(imageWidth * imageScale)
        self.displayHeight = int(imageHeight * imageScale)
        self.imagePath = None
        self.drawBuffer = drawBuffer
        self.displayAngle = displayAngle
        self.xPosition = initialX
        self.yPosition = initialY
        self.health = maxHealth
        self.maxHealth = maxHealth
        self.playerDamageOnHit = playerDamageOnHit
        self.xDistanceFromPlayer = 0
        self.xOffset = 0
        self.yOffset = 0
        self.facing = 'right'
        self.deleteMe = False
        self.invulnerable = False

class InsidiousCreature(Enemy):

    # setting up class for multiple instances - used for teeth projectiles, 
    # and pickups
    class MultipleData:
        def __init__(self,name,imagePath,max):
            self.name = name
            self.imagePath = imagePath
            self.maxInstances = max
            self.activeInstances = set()
            self.checkSet = set(
                [f'{name}_{i}' for i in range(self.maxInstances)])
            self.currentValue = 0

    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,
                 alignment,drawBuffer,displayAngle,initialX,initialY,
                 maxHealth,playerDamageOnHit):
        super().__init__(name,frames,imageWidth,imageHeight,imageScale,
                         alignment,drawBuffer,displayAngle,initialX,initialY,
                         maxHealth,playerDamageOnHit)
        self.behaviors = ['stationary','chase']
        self.behavioralMode = 'stationary'
        self.radius = 0
        self.phase = 0
        self.subphase = 0
        self.subphaseCounter = 0 
        self.playerHoverDistance = 500
        self.intendedYPosition = 0
        # setting up dictionary of multiples - used for teeth projectiles and
        # pickups
        self.multiples = dict()
        # etablishing instances of MultipleData as values in the multiples dict
        self.multiples['tooth'] = self.MultipleData(
            'tooth','images/insidiousCreature/tooth.png',3)
        self.multiples['bigTooth'] = self.MultipleData(
            'bigTooth','images/insidiousCreature/bigTooth.png',10)
        self.multiples['manaPickup'] = self.MultipleData(
            'manaPickup','images/pickups/manaPickup.png',15)
        self.multiples['healthPickup'] = self.MultipleData(
            'healthPickup','images/pickups/healthPickup.png',15)
        self.multiples['laser'] = self.MultipleData(
            'laser','images/insidiousCreature/laser.png',5)
        self.attackCounter = 1
        self.attackSpeed = 20
        self.attackAngle = 0
        self.healthCheckpoint = 0
        self.phaseCheckpoint = 800
        self.dxPlayer = 0
        self.pickupSpawnRadius = 300
        self.chargeSpeed = 500
        self.chargeThrust = 1000
        self.chargeDuration = 15 # in steps
        self.charging = False
        self.returning = False
        self.chargeStartingX = 0
        self.chargeStartingY = 0
        self.chargeAngle = 0
        self.targetRotationSpeed = 0
        self.rotationSpeed = 0
        self.rotationAcceleration = 0
        # initialzing active laser dictionary
        self.activeLasers = dict()
        self.boundingBoxSetRadius = 0
    
    def move(self,app):
        # establishing radius, and position data
        self.playerRadius = getDistance((self.xPosition + self.xOffset), 
                                        (self.yPosition + self.yOffset), 
                                        app.playerObject.xPosition, 
                                        app.playerObject.yPosition)
        self.dxPlayer = ((self.xPosition + self.xOffset) - 
                         app.playerObject.xPosition)
        self.dyPlayer = ((self.yPosition + self.yOffset) - 
                         app.playerObject.yPosition)

        # setting rotation
        self.displayAngle += self.rotationSpeed
        self.displayAngle %= 360
        
        # rise up at beginning, right after awakening
        if(self.subphase == 'rise'):
            if(self.yPosition > (app.ti['ground'].initialTileYPosition - 150)):
                app.icPhysics['y'].currentThrust += 5
            elif(app.icPhysics['y'].currentThrust > 0):
                app.icPhysics['y'].currentThrust = (
                    app.icPhysics['y'].currentThrust * 0.9)
                if(app.icPhysics['y'].currentThrust < 1):
                    app.icPhysics['y'].currentThrust = 0
            else:
                self.invulnerable = False
                self.subphase = 'chase'
        
        # chase behavior, follow player
        elif(self.subphase == 'chase'):
            if(self.dxPlayer < -self.playerHoverDistance):
                app.icPhysics['x'].currentThrust = -500
            elif(self.dxPlayer > self.playerHoverDistance):
                app.icPhysics['x'].currentThrust = 500
            else:
                app.icPhysics['x'].currentThrust = 0

            self.intendedYPosition = (
                app.playerObject.yPosition - self.yOffset - 150)
            dy = self.yPosition - self.intendedYPosition
            hoverMargin = 100
            if(dy > hoverMargin):
                app.icPhysics['y'].currentThrust = dy 
            elif(dy < -hoverMargin):
                app.icPhysics['y'].currentThrust = dy * 2
            else:
                app.icPhysics['y'].currentThrust = 0
        
        # charge at player
        elif(self.subphase == 'charge'):
            if(self.charging == False):
                self.chargeAngle = getAngle(
                    -self.dxPlayer, -self.dyPlayer, 'radians')
                self.charging = True
            app.icPhysics['x'].currentThrust = (
                math.cos(self.chargeAngle) * self.chargeThrust)
            app.icPhysics['y'].currentThrust = (
                math.sin(self.chargeAngle) * self.chargeThrust)
        
        # return to starting position prior to chase
        elif(self.subphase == 'return'):
            self.returning = True
            app.icPhysics['x'].currentThrust = (
                math.cos(self.chargeAngle) * -(self.chargeThrust/2))
            app.icPhysics['y'].currentThrust = (
                math.sin(self.chargeAngle) * -(self.chargeThrust/2))
            runPhysicsCalculations(app.icPhysics['x'])   
            runPhysicsCalculations(app.icPhysics['y'])
            self.xPosition -= app.icPhysics['x'].currentVelocity
            self.yPosition -= app.icPhysics['y'].currentVelocity
            if((abs(self.xPosition - self.chargeStartingX) <= 
                abs(app.icPhysics['x'].currentVelocity)) or 
                (abs(self.yPosition - self.chargeStartingY) <= 
                 abs(app.icPhysics['y'].currentVelocity))):
                
                self.xPosition = self.chargeStartingX
                self.yPosition = self.chargeStartingY
                self.returning = False
                self.subphase = 'chase'

        # reset thrust to 0                        
        else:
            app.icPhysics['x'].currentThrust = 0
            app.icPhysics['y'].currentThrust = 0

        # return behavior already handles calculations and position update, 
        # don't run them twice
        if(not (self.subphase == 'return')):
            # run physics calculations and update position
            runPhysicsCalculations(app.icPhysics['x'])   
            runPhysicsCalculations(app.icPhysics['y'])
            # ptc("app.icPhysics['y'].currentVelocity",
            # app.icPhysics['y'].currentVelocity)
            self.xPosition -= app.icPhysics['x'].currentVelocity
            self.yPosition -= app.icPhysics['y'].currentVelocity

    def attackCoordinator(self,app):
        # phase 1 attacks and behaviors
        if((self.phase == 1) and (self.subphase == 'chase')):
            # managing rectangular bounding box
            if(app.boundingBox == None):
                app.boundingBox = RectBoundingBox(
                    self.xPosition, self.yPosition, self.xOffset, 
                    self.yOffset, 2500, 1750, 3)
            else:
                app.boundingBox.syncOffsets(self)
                app.boundingBox.align(
                    self.xPosition, self.yPosition,self.dxPlayer)
            # managing tooth attack
            if((self.attackCounter % self.attackSpeed) == 0):
                self.fireTooth(app)
                self.attackCounter = 0
            self.attackCounter += 1
            # detecting when to change the tooth attack speed
            if(self.health <= self.healthCheckpoint):
                self.attackSpeed -= 2
                self.healthCheckpoint -= 125
                # print('changed attack speed, now', self.attackSpeed)
                # print('new health checkpoint:',self.healthCheckpoint)
        
        # phase 2 attacks and behaviors
        elif((self.phase == 2)):
            # managing circular bounding box
            self.boundingBoxSetRadius = 1000
            if(app.boundingBox == None):
                # also initializing attack speed
                self.attackSpeed = 45
                app.boundingBox = CircBoundingBox(
                    self.xPosition, self.yPosition, self.xOffset, self.yOffset, 
                    (self.boundingBoxSetRadius * 5), 5)
            else:
                # sychorize x and y offsets between bounding box and boss
                app.boundingBox.syncOffsets(self)
                # starting the display radius at a larger value, and
                # progressively shrinking it at the start of phase 2
                if(app.boundingBox.displayRadius > self.boundingBoxSetRadius):
                    app.boundingBox.displayRadius = max(
                        ((app.boundingBox.displayRadius*(0.9))-1), 
                        self.boundingBoxSetRadius)
                # only passing the rest of the data when the boss is NOT 
                # charging, since I want the bounding box to stay where it was 
                # when the boss started to charge
                if(self.subphase == 'chase'):
                    app.boundingBox.align(
                        self.xPosition,self.yPosition,self.playerRadius)
            # handling laser attack
            if(self.subphase == 'chase'):
                if((self.attackCounter % self.attackSpeed) == 0):
                    self.fireLaser(app)
                    self.attackCounter = 0
                self.attackCounter += 1
            # initalizing charge
            if((self.subphaseCounter % self.chargeSpeed) == 0):
                # print('charging!')
                self.subphase = 'startCharge'
                self.subphaseCounter = 1
                self.attackCounter = 1
                self.targetRotationSpeed = 25
                self.rotationSpeed = 1
                self.rotationAcceleration = 1.04
                self.chargeStartingX = self.xPosition
                self.chargeStartingY = self.yPosition
            # starting rotation
            if(self.subphase == 'startCharge'):
                self.rotationSpeed = min(
                    (self.rotationSpeed * self.rotationAcceleration), 
                    self.targetRotationSpeed)
                if(self.rotationSpeed == self.targetRotationSpeed):
                    self.subphase = 'charge'
                    self.targetRotationSpeed = 0
                    self.rotationAcceleration = 0.95
            # iterating attack counter and stopping charge when done
            elif(self.subphase == 'charge'):
                if((self.attackCounter % self.chargeDuration) == 0):
                    self.subphase = 'return'
                    self.attackCounter = 0
                    self.charging = False
                self.attackCounter += 1
            # stopping the rotation once the charge is finished
            elif(self.subphase == 'return'):
                self.attackCounter = 1
                if(self.rotationSpeed != 0):
                    self.rotationSpeed = max(
                        (self.rotationSpeed * self.rotationAcceleration)-1, 
                        self.targetRotationSpeed)
        
        # phase 3 attacks and behaviors
        elif((self.phase == 3) and not (self.subphase == 'phaseChange_3')):
            # managing circular bounding box
            self.boundingBoxSetRadius = 800
            if(app.boundingBox == None):
                # also initializing attack speed
                self.attackSpeed = 2
                app.boundingBox = CircBoundingBox(
                    self.xPosition, self.yPosition, self.xOffset, self.yOffset, 
                    (self.boundingBoxSetRadius * 5), 10)
            else:
                # sychorize x and y offsets between bounding box and boss
                app.boundingBox.syncOffsets(self)
                # starting the display radius at a larger value, and
                # progressively shrinking it at the start of phase 2
                if(app.boundingBox.displayRadius > self.boundingBoxSetRadius):
                    app.boundingBox.displayRadius = max(
                        (app.boundingBox.displayRadius*(0.9))-1, 
                        self.boundingBoxSetRadius)
                # only passing the rest of the data when the boss is NOT 
                # charging, since I want the bounding box to stay where it was 
                # when the boss started to charge
                app.boundingBox.align(
                    self.xPosition,self.yPosition,self.playerRadius)
            # handling big tooth attack
            if((self.attackCounter % self.attackSpeed) == 0):
                self.fireBigTooth(app,self.attackAngle)
                self.attackCounter = 0
                self.attackAngle += 11
            self.attackCounter += 1

        # updating active lasers
        laserDeleteSet = set()
        for laser in self.activeLasers:
            self.activeLasers[laser].update(self,app)
            if(self.activeLasers[laser].deleteMe):
                laserDeleteSet.add(laser)
        for laser in laserDeleteSet:
            if(laser in self.multiples['laser'].activeInstances):
                self.multiples['laser'].activeInstances.remove(laser)
                del self.activeLasers[laser]

    def fireTooth(self,app):
        # print('firing!')
        # checking for available tooth names
        self.multiples['tooth'].currentValue = None
        for projectile in self.multiples['tooth'].checkSet:
            if(projectile not in self.multiples['tooth'].activeInstances):
                self.multiples['tooth'].currentValue = projectile
                break
        if(self.multiples['tooth'].currentValue == None):
            return
        tooth = self.multiples['tooth'].currentValue
        
        # print('current tooth:',self.multiples['tooth'].currentValue)
        
        # setting up initial position and target position
        initialX = self.xPosition + self.xOffset
        initialY = self.yPosition + self.yOffset
        targetX = app.playerObject.centerX
        targetY = app.playerObject.centerY
        
        # factoring in overshoot, to make the projectile follow through more
        overshoot = 100
        dx = targetX - initialX
        dy = targetY - initialY
        distance = getDistance(targetX, targetY, initialX, initialY)
        if(distance == 0):
            distance = 0.001
        if(dx > 0):
            rotationAngle = math.radians(180) + (math.asin((dy)/distance))
        else:
            rotationAngle = (math.asin((-dy)/distance))
        
        # also adding in aim offset, to give projectiles a bit of variation
        aimOffset = 15
        rotationAngle += math.radians(random.randint(-aimOffset, aimOffset))
        targetX -= math.cos(rotationAngle) * overshoot
        targetY -= math.sin(rotationAngle) * overshoot
        
        # ptc('initialX',initialX)
        # ptc('initialY',initialY)
        # ptc('targetX',targetX)
        # ptc('targetY',targetY)

        # initiating projectile
        app.projectile[tooth] = Linear(
            tooth,0,250,250,0.5,10,0,initialX,(initialY-self.yOffset),
            targetX,(targetY-self.yOffset),False)
        app.projectile[tooth].displayAngle = rotationAngle
        app.projectile[tooth].imagePath = self.multiples['tooth'].imagePath
        # print('added projectile:',
        #       self.multiples[tooth].currentValue,
        #       'to active map projectiles')
        app.activeMapProjectiles.append(tooth)
        initiateProjectile(app,tooth)

        # adding current tooth value to list of active tooth values
        self.multiples['tooth'].activeInstances.add(tooth)        

    def fireBigTooth(self,app,angle):
        # print('firing big tooth!')
        
        # checking for available big teeth names
        self.multiples['bigTooth'].currentValue = None
        for projectile in self.multiples['bigTooth'].checkSet:
            if(projectile not in self.multiples['bigTooth'].activeInstances):
                self.multiples['bigTooth'].currentValue = projectile
                break
        if(self.multiples['bigTooth'].currentValue == None):
            return
        bigTooth = self.multiples['bigTooth'].currentValue
        # print('current tooth:',self.multiples['bigTooth'].currentValue)
        
        # setting up initial position and target position
        initialX = self.xPosition + self.xOffset
        initialY = self.yPosition + self.yOffset
        targetX = (initialX + 
                   (math.cos(math.radians(angle)) * self.boundingBoxSetRadius))
        targetY = (initialY + 
                   (math.sin(math.radians(angle)) * self.boundingBoxSetRadius))
        initialX += (math.cos(math.radians(angle)) * 
                     self.boundingBoxSetRadius * (0.5))
        initialY += (math.sin(math.radians(angle)) * 
                     self.boundingBoxSetRadius * (0.5))
         
        # ptc('initialX',initialX)
        # ptc('initialY',initialY)
        # ptc('targetX',targetX)
        # ptc('targetY',targetY)
        
        # initiating projectile
        app.activeMapProjectiles.append(bigTooth)
        # print('tooth name:',name)
        # print('x:',initialX)
        # print('y:',initialY)
        # print('y offset:',self.yOffset)
        app.projectile[bigTooth] = Linear(
            bigTooth,0,750,250,1,10,0,initialX,(initialY-self.yOffset),
            targetX,(targetY-self.yOffset),False)
        p = app.projectile[bigTooth]
        p.displayAngle = angle
        p.ignoreScreenBounds = True
        p.imagePath = self.multiples['bigTooth'].imagePath
        # print('added projectile:',
        #       self.multiples[bigTooth].currentValue,
        #       'to active map projectiles')
        p.directionalAcceleration = 10
        p.maxVelocity = 100
        p.damage = 25
        p.initialYOffset = app.ti['ground'].yOffset
        p.yOffset = app.ti['ground'].yOffset
        # setting up adjustment data for hitbox
        xAdjustment = int(p.displayWidth * 0)
        yAdjustment = int(p.displayHeight * 0.5)
        # print('initiated AngledRect')
        
        # initiating hitbox
        # print(associatedObject.initialYOffset)
        # print(centerX, centerY)
        width = p.displayWidth - xAdjustment
        height = int(p.displayHeight) - yAdjustment
        dx = targetX - initialX
        dy = targetY - initialY
        rotationAngle = getAngle(dx, dy, 'degrees')
        # ptc('rotationAngle',rotationAngle)
        [(x_1,y_1),(x_2,y_2),(x_3,y_3),(x_4,y_4)] = applyRectangleRotation(
            initialX, (initialY-self.yOffset), width, height, rotationAngle)
        app.hitbox[bigTooth] = HitboxAngledRect(
            x_1,y_1,x_2,y_2,x_3,y_3,x_4,y_4,p)
        h = app.hitbox[bigTooth]
        h.belongsTo = 'enemy'
        # print('coordinates:',p.x_1,p.y_1,p.x_2,p.y_2,p.x_3,p.y_3,p.x_4,p.y_4)
        
        # adding current big tooth name to list of active big tooth names
        self.multiples['bigTooth'].activeInstances.add(bigTooth)    

    def fireLaser(self,app):
        # checking for avilable laser names
        self.multiples['laser'].currentValue = None
        for projectile in self.multiples['laser'].checkSet:
            if(projectile not in self.multiples['laser'].activeInstances):
                self.multiples['laser'].currentValue = projectile
                break
        if(self.multiples['laser'].currentValue == None):
            return
        laser = self.multiples['laser'].currentValue
        
        # adding laser name to list of active laser names
        self.multiples['laser'].activeInstances.add(laser)
        
        # initiating laser
        self.activeLasers[laser] = (InsidiousCreatureLaser(
            app,laser,self.xOffset,self.yOffset))

    def updateImage(self,app):
        # setting initial image
        if(self.phase == 0):
            self.imagePath = 'images/insidiousCreature/eyesClosed.png'
        
        # setting phase 1 image
        elif(self.phase == 1):
            self.imagePath = 'images/insidiousCreature/eyesOpen.png'
        
        # setting phase 2 and phase 2 transition images
        elif(self.phase == 2): 
            if(self.subphase == 'phaseChange_2'):
                self.imagePath = 'images/insidiousCreature/eyesOpen.png'
            else:
                self.imagePath = 'images/insidiousCreature/phase_2.png'
        
        # setting phase 3 and phase 3 transition images
        elif(self.phase == 3):
            if(self.subphase == 'phaseChange_3'):
                self.imagePath = 'images/insidiousCreature/phase_2.png'
            else:
                self.imagePath = 'images/insidiousCreature/phase_3.png'
                
    def spawnPickups(self,pickupType,quantity,restorationAmmount,app):
        # looping over number of pickups
        for i in range(quantity):
            # checking for avilable pickup names
            self.multiples[pickupType].currentValue = None
            for pickup in self.multiples[pickupType].checkSet:
                if(pickup not in self.multiples[pickupType].activeInstances):
                    self.multiples[pickupType].currentValue = pickup
                    break
            if(self.multiples[pickupType].currentValue == None):
                return
            pickup = self.multiples[pickupType].currentValue
            
            # setting rotation and initial position
            rotationAngle = math.radians(random.randint(0,360))
            initialX = (self.xPosition + self.xOffset + 
                        (math.cos(rotationAngle) * self.pickupSpawnRadius))
            initialY = (self.yPosition + 
                        (math.sin(rotationAngle) * self.pickupSpawnRadius))
            # ptc('initialX',initialX)
            # ptc('initialY',initialY)
            # print(pickup)
            
            # initiating pickup
            app.pickups[pickup] = Pickup(
                app,pickupType,pickup,restorationAmmount,
                self.multiples[pickupType].imagePath,50,50,1,0,
                initialX,initialY,0,self.yOffset,100,'center')
            
            # adding pickup name to list of active pickup names
            self.multiples[pickupType].activeInstances.add(pickup)

    def updateState(self,app):
        # initiate boss
        if((self.health != self.maxHealth) and (app.currentBoss == None)):
            app.currentBoss = 'insidiousCreature'
            app.screenShakeMagnitude += 3
            self.phase = 1
            self.subphase = 'rise'
            self.health = self.maxHealth
            self.healthCheckpoint = self.maxHealth - 60
            self.invulnerable = True
        
        # run attack coordinator
        self.attackCoordinator(app)
        
        # deactivate boss if dead
        if(self.health == 0):
            app.boundingBox = None
            # death animation and effects
            app.lightSources.append(LightSource(
                10,255,
                ((self.xPosition + self.xOffset)/app.lightmapScalingFactor),
                ((self.yPosition + self.yOffset)/app.lightmapScalingFactor),
                0.95))
            frameList = [
                f'images/explosion/explosion_{i}.gif' for i in range(17)]
            app.simpleAnimations.append(SimpleAnimation(
                app,frameList,3,True,700,1000,0,'center',
                (self.xPosition + self.xOffset),(self.yPosition),True,0))
            app.playerHealth = 100
            app.gameState = 'winCutscene'
            self.deleteMe = True
        
        # switching phase
        if(self.health <= self.phaseCheckpoint):
            app.boundingBox = None
            self.phase += 1
            self.phaseCheckpoint = max((self.phaseCheckpoint - 700), -1)
            self.subphase = f'phaseChange_{self.phase}'
            # print('new Phase!', self.phase)
            # print('new phase checkpoint:', self.phaseCheckpoint)
            framelist = [f'images/insidiousCreature/phaseChangeCloud_{i}.png' 
                         for i in range(15)]
            x = self.xPosition + self.xOffset
            y = self.yPosition
            self.subphaseCounter = 0
            self.invulnerable = True
            # phase 2 transition animation and effects
            if(self.phase == 2):
                app.lightSources.append(LightSource(
                    10,255,(x/app.lightmapScalingFactor),
                    (y/app.lightmapScalingFactor),0.95))
                app.simpleAnimations.append(SimpleAnimation(
                    app,framelist,3,True,750,750,0,'center',x,y,True,0.1))
                self.spawnPickups('manaPickup',3,10,app)
                self.spawnPickups('healthPickup',3,20,app)
            elif(self.phase == 3):
                # phase 3 transition animation and effects
                self.displayAngle = 0
                for i in range(5):
                    app.simpleAnimations.append(SimpleAnimation(
                        app,framelist,3,True,750,750,0,'center',x,y,True,0.1))
                app.lightSources.append(LightSource(
                    10,255,(x/app.lightmapScalingFactor),
                    (y/app.lightmapScalingFactor),0.95))
                self.spawnPickups('manaPickup',5,15,app)
                self.spawnPickups('healthPickup',5,25,app)
        
        # helping with subphase management and phase cutscenes
        if(self.phase != 0):
            self.subphaseCounter += 1
            # transition from phase 1 - 2
            if((self.subphase == 'phaseChange_2') and 
               self.subphaseCounter >= 40):
                self.invulnerable = False
                self.subphase = 'chase'
                self.playerDamageOnHit = 30
            # transition from phase 2 - 3
            if((self.subphase == 'phaseChange_3') and 
               self.subphaseCounter >= 40):
                self.subphase = 'final'
                self.invulnerable = False
                self.playerDamageOnHit = 20

    def drawLasers(self):
        # looping through active lasers and drawing their guide projectiles
        for laser in self.activeLasers:
            self.activeLasers[laser].draw()

    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self,other):
        return ((isinstance(other,InsidiousCreature)) and 
                (self.name == other.name))

# test boss
class TheHideousBeast(Enemy):
    def __init__(self,name,frames,imageWidth,imageHeight,imageScale,
                 alignment,drawBuffer,displayAngle,initialX,initialY,
                 maxHealth,playerDamageOnHit):
        super().__init__(name,frames,imageWidth,imageHeight,imageScale,
                         alignment,drawBuffer,displayAngle,initialX,initialY,
                         maxHealth,playerDamageOnHit)
        self.behaviors = ['stationary','chase']
        self.behavioralMode = 'stationary'
        self.modeTimer = 0

    def move(self,app):
        self.xDistanceFromPlayer = (
            ((app.screenWidth // 2) - self.xPosition) - self.xOffset)
        if(self.behavioralMode == 'chase'):
            approachThreshold = 500
            chaceCoefficient = 12
            if(self.xDistanceFromPlayer > approachThreshold):
                app.THBPhysics['x'].currentThrust = ((
                    app.THBPhysics['x'].setThrust) * 
                    ((abs(self.xDistanceFromPlayer) ** 0.5)//chaceCoefficient))
                app.THBPhysics['x'].frictionConstant = (
                    app.THBPhysics['x'].setFrictionConstant)
            elif(self.xDistanceFromPlayer < -approachThreshold):
                app.THBPhysics['x'].currentThrust = (
                    -app.THBPhysics['x'].setThrust * 
                    ((abs(self.xDistanceFromPlayer) ** 0.5)//chaceCoefficient))
                app.THBPhysics['x'].frictionConstant = (
                    app.THBPhysics['x'].setFrictionConstant)
            else:
                app.THBPhysics['x'].currentThrust = 0
                app.THBPhysics['x'].frictionConstant = (
                    app.THBPhysics['x'].setFrictionConstant * 3)
            app.THBPhysics['x'].currentThrust += (
                app.THBPhysics['x'].currentVelocity * 
                app.THBPhysics['x'].frictionConstant)
            simplePhysicsCalculations(
                app.THBPhysics['x'],app.THBPhysics['x'].currentThrust)
            self.xPosition += app.THBPhysics['x'].currentVelocity
        elif(self.behavioralMode == 'stationary'):
            # ptc('self.facing',self.facing)
            pass
        
        # ptc('xDistanceFromPlayer',xDistanceFromPlayer)

    def updateImage(self,app):
        if(self.xDistanceFromPlayer >= 0):
            self.facing = 'right'
        else:
            self.facing = 'left'
        # no support for animations just yet, since this is a test boss
        self.imagePath = f'images/theHideousBeast/{self.facing}Move.png'

    def updateState(self,app):
        if(self.modeTimer % 300 == 0):
            self.modeTimer = 1
            if(self.behavioralMode == 'chase'):
                self.behavioralMode = 'stationary'
            elif(self.behavioralMode == 'stationary'):
                self.behavioralMode = 'chase'
            # ptc('self.behavioralMode',self.behavioralMode)
        self.modeTimer += 1
        if(self.health == 0):
            print('died')
            app.playerHealth == 100
            self.deleteMe = True

# ---- BOUNDING BOX ---- 
class BoundingBox:
    def __init__(self,xPosition,yPosition,xOffset,yOffset,outOfBoundsDamage):
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.initialXPosition = xPosition
        self.initialYPosition = yPosition
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.outOfBoundsDamage = outOfBoundsDamage
        self.dxPlayer = 0
    
class RectBoundingBox(BoundingBox):
    def __init__(self,xPosition,yPosition,xOffset,yOffset,width,height,
                 outOfBoundsDamage):
        super().__init__(xPosition,yPosition,xOffset,yOffset,outOfBoundsDamage)
        self.width = width
        self.height = height
        self.verticalImagePath = 'images/boundingBox/vertical.png'
        self.horizontalImagePath = 'images/boundingBox/horizontal.png'
        self.borderWidth = 50
        self.borderHeight = 50
        self.getBorderPositions()

    def getBorderPositions(self):
        self.left = self.xPosition - int(self.width // 2)
        self.right = self.xPosition + int(self.width // 2)
        self.top = self.yPosition - int(self.height // 2)
        self.bottom = self.yPosition + int(self.height // 2)

    def syncOffsets(self,other):
        self.xOffset = other.xOffset
        self.yOffset = other.yOffset

    def align(self,otherX,otherY,otherDxPlayer):
        self.xPosition = otherX
        self.yPosition = otherY
        self.dxPlayer = otherDxPlayer
        self.getBorderPositions()

    def checkPlayerLocation(self,app):
        # print(self.dxPlayer)
        if(abs(self.dxPlayer) > (self.width // 2)):
            # print(self.xPosition + self.xOffset)
            # print('out of bounds!')
            if(app.playerImmunityFrames == 0):
                app.playerHealth = max(
                    (app.playerHealth - self.outOfBoundsDamage), 0)
                app.screenShakeMagnitude += 5
                app.playerImmunityFrames += self.outOfBoundsDamage*3

    def draw(self):
        drawImage(self.verticalImagePath, 
                  (self.left + self.xOffset), 
                  (self.yPosition + self.yOffset), 
                  width = self.borderWidth, 
                  height = self.height, 
                  align = 'center')
        drawImage(self.verticalImagePath, 
                  (self.right + self.xOffset), 
                  (self.yPosition + self.yOffset), 
                  width = self.borderWidth, 
                  height = self.height, 
                  align = 'center')
        drawImage(self.horizontalImagePath, 
                  (self.xPosition + self.xOffset), 
                  (self.top + self.yOffset), 
                  width = self.width, 
                  height = self.borderHeight, 
                  align = 'center')
        drawImage(self.horizontalImagePath, 
                  (self.xPosition + self.xOffset), 
                  (self.bottom + self.yOffset), 
                  width = self.width, 
                  height = self.borderHeight, 
                  align = 'center')
    
class CircBoundingBox(BoundingBox):
    def __init__(self,xPosition,yPosition,xOffset,yOffset,displayRadius,
                 outOfBoundsDamage):
        super().__init__(xPosition,yPosition,xOffset,yOffset,outOfBoundsDamage)
        self.displayRadius = displayRadius
        self.imagePath = 'images/boundingBox/circular.png'
        self.playerRadius = 0

    def syncOffsets(self,other):
        self.xOffset = other.xOffset
        self.yOffset = other.yOffset

    def align(self,otherX,otherY,otherPlayerRadius):
        self.xPosition = otherX
        self.yPosition = otherY
        self.playerRadius = otherPlayerRadius

    def checkPlayerLocation(self,app):
        # print(self.dxPlayer)
        if(self.playerRadius >= self.displayRadius):
            # print(self.xPosition + self.xOffset)
            # print('out of bounds!')
            if(app.playerImmunityFrames == 0):
                app.playerHealth = max(
                    (app.playerHealth - self.outOfBoundsDamage), 0)
                app.screenShakeMagnitude += 5
                app.playerImmunityFrames += self.outOfBoundsDamage*3

    def draw(self):
        drawImage(self.imagePath, 
                  (self.xPosition + self.xOffset), 
                  (self.yPosition + self.yOffset), 
                  width = (self.displayRadius * 2), 
                  height = (self.displayRadius * 2), 
                  align = 'center')

# ---- SIMPLE ANIMATION ----
class SimpleAnimation:
    def __init__(self,app,frameList,animationSpeed,relativeToMap,displayWidth,
                 displayHeight,rotation,alignment,xPosition,yPosition,fade,
                 fadeRate):
        self.frameList = frameList
        self.animationSpeed = animationSpeed
        self.relativeToMap = relativeToMap
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight
        self.rotation = rotation
        self.alignment = alignment
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.xOffset = 0
        self.yOffset = 0
        self.currentFramePath = ''
        self.frameOn = 0
        self.counter = 0
        self.fade = fade
        self.fadeRate = fadeRate
        self.opacity = 100
        self.update(app)

    def update(self,app):
        if((self.counter % self.animationSpeed) == 0):
            self.counter = 0
            if(self.frameOn == len(self.frameList)):
                app.simpleAnimations.remove(self)
                return
            else:
                self.currentFramePath = self.frameList[self.frameOn]
                self.frameOn += 1
        self.counter += 1
        if(self.fade):
            self.opacity = max((self.opacity - self.fadeRate), 0)
        if(self.relativeToMap):
            self.xOffset -= app.player['x'].currentVelocity
            self.yOffset = app.ti['ground'].yOffset

    def draw(self,app):
        x = self.xPosition + self.xOffset + app.screenShakeX
        y = self.yPosition + self.yOffset + app.screenShakeY
        # ptc('x',x)
        # ptc('y',y)
        drawImage(self.currentFramePath,x,y,width = self.displayWidth, 
                  height = self.displayHeight, rotateAngle = self.rotation, 
                  align = self.alignment, opacity = self.opacity)

# ---- OVERLAY ----
class Overlay:
    def __init__(self,imagePath,imageWidth,imageHeight,imageScale,displayAngle,
                 xPosition,yPosition,xOffset,yOffset,opacity,alignment):
        self.imagePath = imagePath
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.imageScale = imageScale
        self.displayWidth = int(imageWidth * imageScale)
        self.displayHeight = int(imageHeight * imageScale)
        self.displayAngle = displayAngle
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.opacity = opacity
        self.displayWidth // 2
        self.alignment = alignment

    def draw(self,app):
        # initiating data
        x = self.xPosition + self.xOffset
        left = app.screenLeft - (self.displayWidth // 2)
        right = app.screenRight + (self.displayWidth // 2)
        y = self.yPosition + self.yOffset
        top = app.top - (self.displayHeight // 2)
        bottom = app.bottom + (self.displayHeight // 2)
        # actually drawing
        if((left < x < right) and (top < y < bottom)):
            drawImage(self.imagePath, (x + app.screenShakeX), 
                      (y + app.screenShakeY), width = self.displayWidth, 
                      height = self.displayHeight, opacity = self.opacity, 
                      rotateAngle = self.displayAngle, align = self.alignment)

# ---- PICKUPS ----
class Pickup(Overlay):
    def __init__(self,app,pickupType,name,restorationAmmount,imagePath,
                 imageWidth,imageHeight,imageScale,displayAngle,xPosition,
                 yPosition,xOffset,yOffset,opacity,alignment):
        super().__init__(imagePath,imageWidth,imageHeight,imageScale,
                         displayAngle,xPosition,yPosition,xOffset,yOffset,
                         opacity,alignment)
        self.pickupType = pickupType
        self.name = name
        self.radius = int(20 * self.imageScale)
        self.hitbox = initiateHitbox(app,name,self,'pickup',0,0,'hitboxCircle')
        self.restorationAmmount = restorationAmmount
        self.deleteMe = False

# ---- HITBOXES ----
class Hitbox:
    def __init__(self):
        self.xOffset = 0
        self.yOffset = 0
        self.associatedObject = None
        self.belongsTo = None

class HitboxCircle(Hitbox):
    def __init__(self,x,y,radius):
        super().__init__()
        self.xPosition = x
        self.yPosition = y
        self.radius = radius

    def align(self,other):
        self.xPosition = other.xPosition
        self.yPosition = other.yPosition
        self.xOffset = other.xOffset
        self.yOffset = other.yOffset

class HitboxRect(Hitbox):
    def __init__(self,left,right,top,bottom):
        super().__init__()
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.xAdjustment = 0
        self.yAdjustment = 0

    def getVertList(self):
        return [[self.left,self.bottom],
                [self.right,self.bottom],
                [self.right,self.top],
                [self.left,self.top]]

    def align(self,other):
        self.left = (
            other.xPosition - (other.displayWidth//2) + self.xAdjustment)
        self.right = (
            other.xPosition + (other.displayWidth//2) - self.xAdjustment)
        self.top = (
            other.yPosition - (other.displayHeight//2) + self.yAdjustment)
        self.bottom = (
            other.yPosition + (other.displayHeight//2) - self.yAdjustment)
        self.xOffset = int(other.xOffset)
        self.yOffset = int(other.yOffset)

class HitboxAngledRect(Hitbox):
    def __init__(self,x_1,y_1,x_2,y_2,x_3,y_3,x_4,y_4,asscociatedObject):
        super().__init__()
        self.x_1 = x_1
        self.y_1 = y_1
        self.x_2 = x_2
        self.y_2 = y_2
        self.x_3 = x_3
        self.y_3 = y_3
        self.x_4 = x_4
        self.y_4 = y_4
        self.associatedObject = asscociatedObject
        self.align(self.associatedObject)

    def align(self,other):
        if(isinstance(other,Projectile)):
            self.x_1 = (self.x_1 + other.xVelocity)
            self.y_1 = (self.y_1 + other.yVelocity)
            self.x_2 = (self.x_2 + other.xVelocity)
            self.y_2 = (self.y_2 + other.yVelocity)
            self.x_3 = (self.x_3 + other.xVelocity)
            self.y_3 = (self.y_3 + other.yVelocity)
            self.x_4 = (self.x_4 + other.xVelocity)
            self.y_4 = (self.y_4 + other.yVelocity)
            self.xOffset = int(other.xOffset)
            self.yOffset = int(other.yOffset)
    
    def getVertList(self):
        return [[int(self.x_1),int(self.y_1)],
                [int(self.x_2),int(self.y_2)],
                [int(self.x_3),int(self.y_3)],
                [int(self.x_4),int(self.y_4)]]
    
    def __hash__(self):
        return hash(str(self))

    def __eq__(self,other):
        selfList = [self.x_1,self.y_1,self.x_2,self.y_2,
                    self.x_3,self.y_3,self.x_4,self.y_4]
        otherList = [other.x_1,other.y_1,other.x_2,other.y_2,
                     other.x_3,other.y_3,other.x_4,other.y_4]
        return ((isinstance(other,HitboxAngledRect)) and 
                ([int(i) for i in selfList] == [int(i) for i in otherList]))

# DEBUG/TESTING FUNCTIONS
# debug function for displaying the defensive spell sectors 
# (used especially for the shield spell)
def displaySectors(app):
    sectorOpacity = 50

    # drawCircle(playerHeadX, playerHeadY, 10, fill = 'red', opacity = 50)

    sectorColors = dict()
    sectorColors['ssDown'] = 'lightGreen'
    sectorColors['ssLeft'] = 'salmon'
    sectorColors['ssRight'] = 'salmon'
    sectorColors['ssUpLeft'] = 'lightSkyBlue'
    sectorColors['ssUpRight'] = 'lightSkyBlue'
    sectorColors['ssUp'] = 'mediumPurple'

    # obtaining player head position
    x_0 = app.playerObject.centerX
    y_0 = app.playerObject.centerY

    # arbitrary hypotenuse value, just has to be large enough such that the 
    # sectors go off the screen
    hypotenuse = 700
    for sector in app.sectorAngles:
        sectorAngle_1 = app.sectorAngles[sector][0]
        sectorAngle_2 = app.sectorAngles[sector][1]
        # ptc('sectorAngle_1',sectorAngle_1)
        # ptc('sectorAngle_2',sectorAngle_2)
        x_1 = x_0 + (hypotenuse * math.cos(math.radians(sectorAngle_1)))
        y_1 = y_0 + (hypotenuse * math.sin(math.radians(sectorAngle_1)))
        x_2 = x_0 + (hypotenuse * math.cos(math.radians(sectorAngle_2)))
        y_2 = y_0 + (hypotenuse * math.sin(math.radians(sectorAngle_2)))
        drawPolygon(x_0,y_0,x_1,y_1,x_2,y_2,fill=sectorColors[sector],
                    opacity=sectorOpacity)

# debug function for display anticipated shield positions
def displayShieldPositions(app):
    for direction in app.shieldData:
        x = app.shieldData[direction][0]
        y = app.shieldData[direction][1]
        drawCircle(x,y,10,fill='red')

# debug function for debugging, displays the values of certain variables
def displayReadout(app,inputList):
    buffer = 10
    lineSpacing = 20
    lineXPosition = 0 + buffer
    lineYPosition = app.screenHeight - buffer
    for i in range(0,len(inputList),2):
        displayText = f'{inputList[i]}: {inputList[i+1]}'
        drawLabel(displayText, 
        lineXPosition, lineYPosition, 
              fill = 'white', border = "black", borderWidth = 1, opacity = 100, 
              rotateAngle = 0, align = 'left-bottom', visible = True, size = 20,
              font = 'arial', bold = True, italic = False)
        lineYPosition -= lineSpacing

def displayDebugFeatures(app):
    debugTextBuffer = 10
    debugTextHeight = 20
    debugTextRight = (app.screenWidth - debugTextBuffer)
    debugTextBottom = (
        (app.screenHeight - debugTextBuffer) - 
        (debugTextHeight * (len(app.debugFeatureDisplayText) - 1)))
    for debugText in app.debugFeatureDisplayText:
        drawLabel(debugText,debugTextRight,debugTextBottom,
                  fill='white',align='right-bottom')
        debugTextBottom += debugTextHeight

    if(app.displayScreenZones):
        displaySectors(app)
    if(app.displayShieldPositions):
        displayShieldPositions(app)
    if(app.displayReadout):
        displayReadout(app,['currentPlayerXAcceleration',
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

# GENERAL HELPER FUNCTIONS
# function to get justified angle based off of dx and dy
def getAngle(dx,dy,outputType):
    distance = (((dx ** 2) + (dy ** 2)) ** (0.5))
    if(distance == 0):
        distance = 0.001
    if(dx > 0):
        if(outputType == 'degrees'):
            return 180 + math.degrees(math.asin((dy)/distance))
        else:
            return math.radians(180) + math.asin((dy)/distance)
    else:
        if(outputType == 'degrees'):
            return math.degrees(math.asin((-dy)/distance))
        else: 
            return math.asin((-dy)/distance)

# function to check polygon intersection, used for angled rectanlgle collisions
def checkConvexPolygonIntersection(vertexList_1,vertexList_2):
    # Polygon intersection referenced from 
    # https://www.gorillasun.de/blog/an-algorithm-for-polygon-intersections/
    # and implementation guided by Professor Mike Taylor and TA Nathan Xie
    insideRect = False
    for checkPoint in vertexList_1:
        # setting the x and y position of the point we are checking
        checkX = checkPoint[0]
        checkY = checkPoint[1]
        insideRect = False
        
        i = 0
        j = len(vertexList_2) -1

        while(i < len(vertexList_2)):
            # breaking up the polygon into it's line segments
            xI = vertexList_2[i][0]
            yI = vertexList_2[i][1]
            xJ = vertexList_2[j][0]
            yJ = vertexList_2[j][1]
            # checking whether the 'ray' we cast from the point intersects
            # with the line segment we have determined
            # it is not a real ray, we simply use two mathemtical formulae
            # to approximate the effect of a ray.
            # we first check if the y value of the point is within 
            # the range of the y values of the line segment
            # and then check, using another equation, whether the point 
            # should be inside our polygon. 
            # this equation is described in detail at the following link:
            # https://math.stackexchange.com/questions/274712/calculate-on-which
            # -side-of-a-straight-line-is-a-given-point-located/274728#274728
            # print('yI:',yI,' checkY:',checkY,' yJ:',yJ)
            # print('check 1:',(yI > checkY) != (yJ > checkY))
            dy = (yJ - yI)
            if(dy == 0):
                dy = 0.001
            # print('check 2:',
            #       (checkX < ((((xJ - xI) * (checkY - yI)) / dy) + xI)))
            intersection = (
                ((yI > checkY) != (yJ > checkY)) and 
                (checkX < ((((xJ - xI) * (checkY - yI)) / dy) + xI)))
            # if an intersection is detected, then flip the inside variable
            # this essentially counts whether our interesections are even
            # or odd. The cumulative effects of this flipping will detail
            # whether the point is inside the polygon or not, as described
            # by the Jordan curve theorem, which is detailed here:
            # https://en.wikipedia.org/wiki/
            # Jordan_curve_theorem?ref=gorillasun.de
            # in addition to being utilized by the original website
            if(intersection): 
                insideRect = not insideRect
            # indexing the bounds to select the next line segment
            i += 1
            j = i-1
        if(insideRect):
            return insideRect
    return False

# function to mathemtically apply a rotation to a given rectangle. This 
# outputs four verticies rotated around the rectangle's center
def applyRectangleRotation(centerX,centerY,width,height,rotationAngle):
    radAngle = math.radians(rotationAngle)
    # settign up coordinates
    # (x_4,y_4) --- (x_3,y_3)
    #     |             |    
    # (x_1,y_1) --- (x_2,y_2)

    x_1I = x_4I = -width//2
    x_2I = x_3I = width//2 
    y_1I = y_2I = height//2
    y_3I = y_4I = -height//2
    # rectangle rotation formula reference from https://www.gorillasun.de/blog/
    # an-algorithm-for-polygon-intersections/#drawing-rotated-rectangles
    initialPointSet = [(x_1I,y_1I),(x_2I,y_2I),(x_3I,y_3I),(x_4I,y_4I)]
    finalPointSet = []
    for point in initialPointSet:
        finalX = (centerX + (
            (point[0] * math.cos(radAngle)) - (point[1] * math.sin(radAngle))))
        finalY = (centerY + (
            (point[0] * math.sin(radAngle)) + (point[1] * math.cos(radAngle))))
        finalPointSet.append((finalX,finalY))
    # ptc('finalPointSet',finalPointSet)
    return finalPointSet

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

# helper function to check that a point is within the bounds of the screen
def onScreen(app, x, y, buffer):
    return ((app.screenLeft - buffer) < x < (app.screenRight + buffer) and 
            (app.screenTop - buffer) < y < (app.screenBottom + buffer))

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

# reports which screen sector the mouse is currently in
def getMouseScreenSector(app,mouseX,mouseY):
    x_0 = app.playerObject.centerX
    y_0 = app.playerObject.centerY
    dy = mouseY - y_0
    dx = mouseX - x_0
    if(dx == 0):
        dx = 0.001
    mouseAngle = math.degrees(math.atan(dy/dx))
    if(dx < 0):
        mouseAngle += 180
    elif(dy < 0):
        mouseAngle += 360
    currentScreenSector = None
    # ptc('mouseAngle',mouseAngle)
    # the only sector that must be checked manually is ssRight, since it
    # crosses 0 degrees. all the other sectors can be checked in a loop
    if((0 <= mouseAngle < app.sectorAngles['ssRight'][0]) or 
       (app.sectorAngles['ssRight'][1] <= mouseAngle <= 360)):
       currentScreenSector = 'ssRight'
    else:
        for sector in app.sectorAngles:
            sectorAngle_1 = app.sectorAngles[sector][0]
            sectorAngle_2 = app.sectorAngles[sector][1]
            if(sectorAngle_1 >= mouseAngle > sectorAngle_2):
                currentScreenSector = sector
    app.mouseScreenSector = currentScreenSector

# GENERAL PHYSICS FUNCTIONS
# updating the positioning of various objects based off of player velocity
def updatePositioning(app):
    # update tileable image positioning
    for tileableImageName in app.tileableImageList:
        app.ti[tileableImageName].xOffset += (app.player['x'].currentVelocity)
        if((app.ti[tileableImageName].yOffset + 
            (app.player['y'].currentVelocity)) >= 
            app.currentPlayerGroundYOffset):
            app.ti[tileableImageName].yOffset += (
                app.player['y'].currentVelocity)
        else:
            app.ti[tileableImageName].yOffset = app.currentPlayerGroundYOffset
            app.player['y'].previousVelocity = 0
            # special check to make sure the lightmap actually shows that we 
            # are on the ground when the player is on the ground
            if(app.lightmapYOffset != 0):
                updateLightmap(app,True)
    
    # update lightmap positioning
    for lightSource in app.lightSources:
        lightSource.x -= (
            (app.player['x'].currentVelocity) / app.lightmapScalingFactor)
        if((app.ti['ground'].yOffset + 
            (app.player['y'].currentVelocity)) >= 
            app.currentPlayerGroundYOffset):
            lightSource.y += (
                (app.player['y'].currentVelocity) / app.lightmapScalingFactor)
        else:
            # always update lightmap the moment the player returns to the ground
            lightSource.y = lightSource.initialY
    
    # update projectile positioning
    for projectileName in app.activeMapProjectiles:
        app.projectile[projectileName].xOffset -= (
            app.player['x'].currentVelocity)
        app.projectile[projectileName].yOffset = app.ti['ground'].yOffset
        # print(projectileName)

    # update enemy positioning
    for enemyName in app.enemies:
        enemy = app.enemies[enemyName]
        enemy.xOffset -= (app.player['x'].currentVelocity)
        enemy.yOffset = int(app.ti['ground'].yOffset)

    # update overlay positionings
    for overlay in app.overlays:
        app.overlays[overlay].xOffset -= app.player['x'].currentVelocity
        app.overlays[overlay].yOffset = int(app.ti['ground'].yOffset)

    # update pickupo positionings
    for pickup in app.pickups:
        app.pickups[pickup].xOffset -= app.player['x'].currentVelocity
        app.pickups[pickup].yOffset = int(app.ti['ground'].yOffset)
    
    # update total X Offset (for out of bounds effects)
    app.totalXOffset -= app.player['x'].currentVelocity

# full-complexity physics calculations, utilized mainly by player and bosses
def runPhysicsCalculations(subject):
    subject.currentAcceleration = (
        ((subject.currentThrust)+(subject.gravity)+
         ((subject.frictionConstant)*(subject.previousVelocity)))/
         ((subject.mass)-(subject.frictionConstant)))
    
    subject.currentVelocity = (
        (subject.currentAcceleration)+(subject.previousVelocity))
    
    subject.currentFrictionForce = (
        (subject.frictionConstant)*(subject.currentVelocity))
    
    subject.currentMaxVelocity = (
        ((subject.currentThrust)*
         (1-((subject.mass)/(subject.frictionConstant))))/
         ((subject.mass)-(subject.frictionConstant)))
    
    subject.previousVelocity = subject.currentVelocity

# simpler version of the physics calculations, for improved speed
def simplePhysicsCalculations(subject,netForce):
    subject.currentAcceleration = netForce / subject.mass
    subject.currentVelocity += subject.currentAcceleration

# PLAYER PHYSICS & ANIMATIONS
# overview of my player animation pipeline:
# The state of the player, whether that be characterized by velocity, altitude,
# key presses, must be interpreted into the appropriate image to be displayed 
# to represent that state. 
# If the player's velocity is zero, they must be standing still, and thus the 
# image for standing must be shown. 
# If the player is flying then the flying animation must be played, etc...
# my way of doing so works as such:
# Player state is interpreted into a list of three values which I call an 
# image index. There exists a seperate image index for the player and for the
# player's wings. The encoding scheme of the player image index is described in
# function interpretPlayerImageIndex, and the encoding scheme of the wing
# image index is described in the function interpretPlayerWingImageIndex.
# The function interpretPlayerState is what is actually responsible for 
# determining the three values of the index depending on the player's state.
# This index is then constructed into a usable image path in the 
# function updatePlayerImage2, and the image is finally displayed in
# the function drawPlayer. 

# turns wing index data into usable strings, that will then be constructed
# into the appropriate wing image's path
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
    # c = -1 indicates that the player's wing are NOT on a frame of animation
    # c = 0 indicates that the player's wing are on the 1st frame of animation
    # c = 1 indicates that the player's wing are on the 2nd frame of animation
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

# turns player index data into usable strings, that will then be constructed
# into the appropriate player image's path
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

# small helper function to check the player's y offset and return applicable
# altitude
def playerAnimationAltitudeCheck(app):
    if(app.ti['ground'].yOffset > app.currentPlayerGroundYOffset):
        return 'air'
    else: 
        return 'ground'

# small helper function to set player wing offset at different states
def setPlayerWingOffset(app,x,y):
    if(app.playerFacing == 'right'):
        app.playerWingXOffset = x
        app.playerWingYOffset = y
    else:
        app.playerWingXOffset = -x
        app.playerWingYOffset = y

# interperts current game behaviors and player state to set the apropriate
# image index values.
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
                app.player['x'].frictionConstant = (
                    app.player['x'].setFrictionConstant)
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
        # WHEN THE PLAYER IS ON THE GROUND 
        # THEY CAN BE STANDING, RUNNING, OR SLIDING

        app.playerWingCounter = 0 # reset wing counter when touching the ground

        # IF PLAYER IS NOT STANDING STILL:
        if(abs(app.player['x'].currentVelocity) > 1):

            # PLAYER SHOULD INITIATE SLIDE IF THEIR VELOCITY AND THRUST ARE IN 
            # OPPOSITE DIRECTIONS, AND THEIR THRUST IS NONZERO
            if((not sameSign(app.player['x'].currentVelocity, 
                             app.player['x'].currentThrust)) and 
                             (app.player['x'].currentThrust != 0)): 
                
                # put player into slide mode, will begin silde animation 
                # execution at the beginning of the function
                app.playerState = 'slide'
                app.playerAnimationCounter = 0 # reset animation counter
                app.playerImageIndex[1] = 2    # set player moition to sliding
                app.playerImageIndex[2] = 0    # set player animation to frame 0
                # set wing to empty (wings are hidden while sliding)
                app.playerWingImageIndex[1] = 2 
            
            # IF THE PLAYER IS NOT STANDING STILL, 
            # BUT THEY ARE NOT SLIDING, THEN THEY MUST BE RUNNING
            
            # first we check if the player is ALREADY running 
            # (player motion is set to running)
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
                if((app.playerAnimationCounter % 
                    (abs((int(abs(app.player['x'].currentVelocity)))-
                         int(abs((app.player['x'].currentMaxVelocity))))+
                         minimumTicksBetweenRunAnimationFrames) == 0)):
                    
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
                setPlayerWingOffset(app,15,23)

        # IF PLAYER IS ON THE GROUND 
        # BUT NOT RUNNING OR SLIDING THEY MUST BE STANDING        
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
            setPlayerWingOffset(app,18,18)

    elif(app.playerState == 'air'): # PLAYER IS CURRENTLY IN THE AIR
        # WHEN THE PLAYER IS IN THE AIR THEY CAN BE FLYING, GLIDING, OR FALLING
        
        # set player motion to FLYING
        app.playerImageIndex[1] = 3
        # set player animation frame to -1 --> NOT BEING ANIMATED
        app.playerImageIndex[2] = -1

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
            if((app.playerWingCounter < app.maxPlayerWingCounter) and 
               (app.player['y'].currentThrust != app.playerGlideThrust)):
                
                # reset wing animation counter to avoid running into int limit
                if(app.playerWingAnimationCounter > 10000):
                    app.playerWingAnimationCounter = 0  
                
                # setting the speed of the wing animation 
                # unlike the run animation, the speed is constant.
                wingAnimationSpeed = 1

                # ANIMATION LOOP FOR FLYING
                if(app.playerWingAnimationCounter % wingAnimationSpeed == 0):
                    # index to next frame in flying animation
                    app.playerWingImageIndex[2] += 1

                    # ptc('app.playerWingAnimationCounter',
                    #     app.playerWingAnimationCounter)
                    # ptc('app.playerWingImageIndex[2]',
                    #     app.playerWingImageIndex[2])
                    # ptc('app.playerImageIndex[2]',
                    #     app.playerImageIndex[2])

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
        setPlayerWingOffset(app,16,18)

# updates player image and constructs the image
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

    interpretPlayerState(app)
    
    playerFacing = interpretPlayerImageIndex(app,0)
    playerMotion = interpretPlayerImageIndex(app,1)
    playerAnimationFrame = interpretPlayerImageIndex(app,2)

    wingFacing = interpretPlayerWingImageIndex(app,0)
    wingMotion = interpretPlayerWingImageIndex(app,1)
    wingAnimationFrame = interpretPlayerWingImageIndex(app,2)

    app.playerWingX = (
        int((app.screenWidth-app.playerObject.displayWidth)/2) -
          app.playerWingXOffset)
    app.playerWingY = (
        int((app.screenHeight-app.playerObject.displayHeight)/2) - 
        app.playerWingYOffset)

        
    # setting Player Image Path
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
    
    # assigning wing image path and returning an error if it is invalid
    if os.path.exists(testPlayerWingImagePath):
        app.playerWingImage = (f'images/player/{playerWingImageName}.png')
    else:
        reportError('accessing desired player wing image file', 
                    'IMAGE COULD NOT BE FOUND', 'UpdatePlayerImage2', 
                    'File name', (f'images/{playerWingImageName}.png'), None)

# draws the player
def drawPlayer(app):
    # if player is running right specifically we want to display the wings 
    # OVER the player image. Under no other condition is this visibly neseccary
    if((app.playerFacing == 'right') and (app.playerImageIndex[1] == 1)):
        drawImage(app.playerImage, 
                  (app.playerObject.xPosition + app.screenShakeX), 
                  (app.playerObject.yPosition + app.screenShakeY), 
                  width = app.playerObject.displayWidth, 
                  height = app.playerObject.displayHeight)
        drawImage(app.playerWingImage, 
                  (app.playerWingX + app.screenShakeX), 
                  (app.playerWingY + app.screenShakeY), 
                  width = app.playerWingWidth, 
                  height = app.playerWingHeight)
    else:
        drawImage(app.playerWingImage, 
                  (app.playerWingX + app.screenShakeX), 
                  (app.playerWingY + app.screenShakeY), 
                  width = app.playerWingWidth, 
                  height = app.playerWingHeight)
        drawImage(app.playerImage, 
                  (app.playerObject.xPosition + app.screenShakeX), 
                  (app.playerObject.yPosition + app.screenShakeY), 
                  width = app.playerObject.displayWidth, 
                  height = app.playerObject.displayHeight)

# runs the main player physics simulations for the game
def updatePlayerVelocity(app):

    # handling X velocity

    # edge snapping to 0 velocity in x direction 
    if(abs(app.player['x'].currentVelocity) < 0.5):
        app.player['x'].previousVelocity = 0

    runPhysicsCalculations(app.player['x'])

    # edge snapping to max velocity in edge direction
    if(((app.player['x'].currentVelocity - 
         app.player['x'].currentMaxVelocity) < 0.01) and 
         (abs(app.player['x'].currentAcceleration) < 0.01)):
            app.player['x'].previousVelocity = (
                app.player['x'].currentMaxVelocity)
            
    # handling Y velocity
    if((app.ti['ground'].yOffset > app.currentPlayerGroundYOffset) or 
       app.player['y'].currentThrust > 0):
        app.playerState = 'air'
        app.player['y'].gravity = app.setGravity
    else:
        app.player['y'].gravity = 0
        app.player['y'].previousVelocity = 0

    # interpreting player Y position, and using that to determine which
    # ground coordinate the player is currently set to
    
    # applicablePlayerYPosition = (app.ti['ground'].initialTileYPosition - 
    #                              app.ti['ground'].yOffset)
    levels = len(app.playerGroundYOffsets)
    for i in range(levels):
        if((i == (levels-1)) or (
            app.playerGroundYOffsets[i] <= 
            int(app.ti['ground'].yOffset) < 
            app.playerGroundYOffsets[i+1])):
            
            app.currentPlayerGroundYOffset = app.playerGroundYOffsets[i]
            # print('assigned current player ground y offset:', 
            #       app.currentPlayerGroundYOffset)
            groundYIndex = i
            break
    if((app.sPressed) and 
       (app.currentPlayerGroundYOffset != app.playerGroundYOffsets[0])):
        
        app.currentPlayerGroundYOffset = (
            app.playerGroundYOffsets[groundYIndex-1])
    # print(applicablePlayerYPosition)
    # print('currentYOffset:',app.ti['ground'].yOffset)
    # print('currentGroundY:',app.currentPlayerGroundYOffset)

    runPhysicsCalculations(app.player['y'])
    
    # updating positioning based off of player velocty and location
    updatePositioning(app)
    
# TILEABLE IMAGES
# updates tileable image positions, and is responsible for the tiling affect
# and tile reordering procedure
def updateTiles(app,tileableImageName):
    # retrieving variable values
    tileWidth = app.ti[tileableImageName].tileWidth
    xOffset = app.ti[tileableImageName].xOffset
    yOffset = app.ti[tileableImageName].yOffset
    parallaxCoefficient = app.ti[tileableImageName].parallaxCoefficient
    tileableImageWidth = app.ti[tileableImageName].imageWidth
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
    
    app.ti[tileableImageName].currentTileXPosition = (
        (app.ti[tileableImageName].initialTileXPosition)-applicableXOffset)
    app.ti[tileableImageName].currentTileYPosition = (
        (app.ti[tileableImageName].initialTileYPosition)+yOffsetParallax)
    app.ti[tileableImageName].xOffset = (xOffsetParallax * parallaxCoefficient)

# draws the tiles to the screen, but only if they are within bounds
def drawTiles(app,tileableImageName):
    tileWidth = app.ti[tileableImageName].tileWidth
    currentColsList = app.ti[tileableImageName].currentColsList
    currentTileXPosition = app.ti[tileableImageName].currentTileXPosition
    currentTileYPosition = app.ti[tileableImageName].currentTileYPosition
    currentTileBottom = (app.ti[tileableImageName].currentTileYPosition + 
                         app.ti[tileableImageName].imageHeight)
    
    for row in currentColsList:
        # only draw tiles if they are within the bounds of the screen
        if((app.screenLeft <= currentTileXPosition < app.screenRight) and 
           (currentTileYPosition < app.screenBottom) and 
           (currentTileBottom > app.screenTop)):
                tileableImageSavePath = (f'images/{tileableImageName}/'+
                                    f'{tileableImageName}Tile_{row}.png')
                # only draw tiles if their file can be accessed, otherwise 
                # report an error
                if os.path.exists(tileableImageSavePath):
                    drawImage(tileableImageSavePath,
                              (currentTileXPosition+app.screenShakeX),
                              (currentTileYPosition+app.screenShakeY),
                              opacity = app.ti[tileableImageName].opacity)
                else:
                    reportError('accessing desired tile file', 
                                'IMAGE COULD NOT BE FOUND', 'drawTiles', 
                                'File name', (tileableImageSavePath), None)
        currentTileXPosition += tileWidth

# takes the tileable images and cuts them up into tiles using PIL image cropping
# this only happens at the very beginning, and as such is an ok method to use
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
# sets up lightmap positioning, scaling, and opacity matrix 
def lightmapSetup(app):
    app.lightmapScalingFactor = 50
    app.lightmapBuffer = 100
    app.lightmapMatrixX = int(app.screenWidth/app.lightmapScalingFactor)+5
    app.lightmapMatrixY = int(app.screenHeight/app.lightmapScalingFactor)+5
    app.lightmapOpacityMatrix = (
        numpy.array([[[0,255]] * app.lightmapMatrixX]*app.lightmapMatrixY, 
                    dtype=numpy.uint8))
    app.lightmapXPosition = -(app.lightmapBuffer/5)
    app.lightmapYPosition = -(app.lightmapBuffer/5)
    # print(f'{len(app.lightmapOpacityMatrix)} rows')
    # print(f'{len(app.lightmapOpacityMatrix[0])} columns')

# helper function to calculate gaussian lightmap map
def calculateLightmapGaussian(x,y,lightSources,opacityOffset):
    lightsourceMaxIntensity = 255
    opacity = 255
    # arbitray adjusted value for calculation distance cutoff
    # it is unnessecary to calculate the effects of a light source on a point
    # if that light source is definitely too far away to have an effect
    # having a distance cutoff saves computation time
    maxDistance = 1000
    for lightSource in lightSources:
        if(getDistance(x,y,lightSource.x,lightSource.y) < maxDistance):
            # gaussian function implementaiton - guided by Professor Mike Taylor
            # and the equation was referenced from here:
            # https://en.wikipedia.org/wiki/Gaussian_functionr
            opacity -= int(
                (lightSource.intensity)*
                ((lightsourceMaxIntensity)**
                 ((-1*(((x-lightSource.x)**2)/(2*((lightSource.spread)**2))))-
                  (((y-lightSource.y )**2)/(2*((lightSource.spread)**2))))))
    return [0,min(max((opacity+opacityOffset),0),255)]

# specifically determines when and under which conditions the lightmap should
# update, to ensure that it only updates when absolutely nessceary, as 
# the PIL image from array method is extremely slow. 
def updateLightmap(app,groundCheck):
    # these if statements aren't techanically nessecary but it much better 
    # helps me see the conditions under which the lightmap should update
    updateLightmap = False
    if(len(app.lightSources) > 0):
        for lightSource in app.lightSources:
            # checking if the light source we want to display is within bounds
            left = (((0-
                      (app.lightmapBuffer*lightSource.spread))/
                      app.lightmapScalingFactor))
            right = (int((app.screenWidth+
                          (app.lightmapBuffer*lightSource.spread))/
                          app.lightmapScalingFactor))
            up = ((0-
                   (app.lightmapBuffer*lightSource.spread))/
                   app.lightmapScalingFactor)
            down = (int((app.screenHeight+
                         (app.lightmapBuffer*lightSource.spread))/
                         app.lightmapScalingFactor))
            if((left <= lightSource.x <= right) and 
               (up <= lightSource.y <= down)):
                # print('inbounds')
                # print('lightSource.x: ',lightSource.x)
                # print('lightSource.y: ',lightSource.y)
                updateLightmap = True
                # print('trigger 0')
    if(0 < app.ti['ground'].yOffset < 
       (app.screenHeight-app.ti['ground'].initialTileYPosition)):
        updateLightmap = True
        # print('trigger 1')
    if(0 < app.lightmapYOffset < 
       (app.screenHeight-app.ti['ground'].initialTileYPosition)):
        updateLightmap = True
        # print('trigger 2')
    if(groundCheck):
        updateLightmap = True
        # print('trigger 3')
        # ptc('app.lightmapYOffset',app.lightmapYOffset)    

    # actually updating the lightmap
    if(updateLightmap and 
       (app.lightmapUpdateCounter % app.lightmapUpdateRate == 0)):
        # print('updating lightmap!')
        for y in range(app.lightmapMatrixY):
            app.lightmapYOffset = app.ti['ground'].yOffset
            groundY = (
                app.ti['ground'].yOffset+app.ti['ground'].initialTileYPosition)
            if(y < groundY/app.lightmapScalingFactor):
                opacityOffset = -app.backgroundBrightness
            else:
                # tuned value that determines how far down the light from the
                # room permeates the ground tiles
                floorLightPermeabilityConstant = 10
                opacityOffset = (-app.backgroundBrightness + 
                                 (y * floorLightPermeabilityConstant))
                # print(opacityOffset)
            # using our gaussian helper function to construct the opacity matrix
            for x in range(app.lightmapMatrixX):
                app.lightmapOpacityMatrix[y,x] = (
                    calculateLightmapGaussian(
                        x,y,app.lightSources,opacityOffset))
        # turning the opacity matrix into a displayable image
        lightmap = Image.fromarray(app.lightmapOpacityMatrix, mode = 'LA')
        # saving that image
        app.lightmapImage = CMUImage(lightmap)
    app.lightmapUpdateCounter += 1
    # ptc('app.lightmapUpdateCounter',app.lightmapUpdateCounter)

# keeps track of active lightsources and updates them as they fade, then deletes
# them when their intensity reaches 0
def updateLightsources(app):
    i = 0
    while i < len(app.lightSources):
        if(app.lightSources[i].intensity == 0):
            app.lightSources.pop(i)
            # print('# of active light soures: ',len(app.lightSources))
        else:
            app.lightSources[i].intensity = int(
                math.floor((app.lightSources[i].intensity * 
                            app.lightSources[i].fadeRate)*100)/100)
            i+=1

# draws the lightmap on the screen
def drawLightmap(app):
    drawImage(app.lightmapImage,
              (app.lightmapXPosition + app.screenShakeX),
              (app.lightmapYPosition + app.screenShakeY),
              width = (app.lightmapMatrixX * app.lightmapScalingFactor),
              height = (app.lightmapMatrixY * app.lightmapScalingFactor),
              opacity=app.lightmapOpacity)

# SPELL ORB
def updateSpellOrb(app):
    # update image
    if(app.spellOrbCharged):
        app.spellOrbImage = 'images/spellOrbs/spellOrbCharged.png'
    else:
        app.spellOrbImage = 'images/spellOrbs/spellOrbUncharged.png'

    # update position
    app.spellOrbXOffset += (
        (((app.player['x'].currentVelocity) / 
          app.spellOrbDampingCoefficient)) - 
        ((app.spellOrbInitialX-app.spellOrbXPosition) / 
         app.spellOrbDriftConstant))
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
    drawImage(app.spellOrbImage,
              (app.spellOrbXPosition + app.screenShakeX),
              (app.spellOrbYPosition + app.screenShakeY), 
              width = int(app.spellOrbImageSize * app.spellOrbScalingFactor), 
              height = int(app.spellOrbImageSize * app.spellOrbScalingFactor), 
              align = 'center', rotateAngle = app.spellOrbRotationAngle)

# SPELL CASTING
# gets the side of the orb that the mouse pointer is at the point of casting
def getMouseOrbSide(app,mouseX):
    if mouseX >= app.spellOrbXPosition:
        app.mouseOrbSide = 'right'
    else:
        app.mouseOrbSide = 'left'

# charges the spell, and initiates the spell in the active spells list
def chargeSpell(app,spellName):
    # if we have recieved cancel, the cancel combo must have been input, and 
    # we want to remove the currently charged spell, if there is one.
    # if the spell orb is charged, there must be a charged spell, and we can go
    # ahead with cancelling it, but if the spell orb is not charged, we don't
    # want to pass cancel in as a spell, so we return
    if(spellName == 'cancel'):
        if(app.spellOrbCharged):
            # find the currently charged spell, and remove it from it's
            # respective active spell list
            for spellType in app.spellTypes:
                if(len(app.spellData[spellType].activeSpell) == 1):
                    chargedSpell = app.spellData[spellType].activeSpell[0]
                    app.spellData[spellType].activeSpell = []
            # restore half the mana cost of the currently charged spell
            app.playerMana = min(
                (app.playerMana + int(chargedSpell.manaCost * 0.5), 
                 app.playerMaxMana))
            # uncharge the Spell Orb
            app.spellOrbCharged = False
            # return, so as to not try to charge spell 'cancel'
        return
    else:
        # don't charge spell if a spell is already charged
        if(app.spellOrbCharged):
            return
    
    # making sure the spell is acceptable, by attempting to reference it
    try:
        spellType = app.spells[spellName].spellType
    except:
        # if spell is invalid, report error and end the code 
        reportError('initiating spell', 'INVALID SPELL', 'chargeSpell', 
                    'spell name', (spellName), 
                    'reference appStart to find valid spells')
    
    # checking exceptions:
    # is there an active spell of this type already?
    # if so, tell that to the gui spell combo display and don't charge spell
    if(len(app.spellData[spellType].activeSpell) != 0):
        # print('overcharged!')
        app.comboShake += 15
        app.comboCounter = 20
        app.displayCombo = 'overcharged!'
        return
    
    # does the player not have enough mana to cast the spell?
    # if so, tell that to the gui spell combo display and don't charge spell
    if((app.playerMana - app.spells[spellName].manaCost) < 0):
        # print('not enough mana!')
        app.comboShake += 10    
        app.comboCounter = 20
        app.displayCombo = 'insufficient mana!'
        return
    
    # if all the prior conditions pass, cast the spell
    app.playerMana -= app.spells[spellName].manaCost
    app.spellData[spellType].activeSpell = [app.spells[spellName]]
    app.spellOrbCharged = True
    app.spellData[spellType].drawingSpell = False
    app.spells[spellName].xPosition = 0
    app.spells[spellName].yPosition = 0

# enables the spell casting animation itself, and calculates the apropriate 
# angle for the spell animation to cast
def initiateSpellCast(app,spellName,targetX,targetY):
    # checking to make sure we have a valid spell name by attempting to
    # access the value associated with it, and returning an error otherwise
    try:
        app.spells[spellName].targetX = targetX
        app.spells[spellName].targetY = targetY
        spellType = app.spells[spellName].spellType
    except:
        reportError('initiating spell', 
                        'INVALID SPELL', 'intiateSpellCast', 
                        'spell name', (spellName), 'reference appStart to ' \
                        'find valid spells')
    
    # do not initiate spell of this type if a spell 
    # of this type is already being cast
    if((app.spellData[spellType].spellCastingEnabler) and 
       (len(app.spellData[spellType].activeSpell) == 1)):
        return
    
    # initiating end effect spells
    if(app.spells[spellName].displayType == 'endEffect'):
        # setting up position and angle
        distanceToTarget = getDistance(
            app.spellOrbXPosition,app.spellOrbYPosition,targetX,targetY)
        dx = (targetX - app.spellOrbXPosition)
        if(dx == 0):
            dx = 0.00001
        dy = (targetY - app.spellOrbYPosition)
        displayAngle = math.degrees(math.atan(dy/dx))
        app.spells[spellName].displayAngle = displayAngle
        # print(app.spells[spellName].displayAngle)
        app.spells[spellName].displayWidth = distanceToTarget
        xPositionRotationOffset = (
            math.sin(math.atan(dy/dx)/2) * 
            math.sin(math.atan(dy/dx)/2) * 
            distanceToTarget)
        yPositionRotationOffset = (
            math.cos(math.atan(dy/dx)/2) * 
            math.sin(math.atan(dy/dx)/2) * 
            distanceToTarget)
        # ptc('xPositionRotationOffset',xPositionRotationOffset)
        # ptc('yPositionRotationOffset',yPositionRotationOffset)
        if(app.mouseOrbSide == "right"):
            app.spells[spellName].xPosition = (
                app.spellOrbXPosition - 
                xPositionRotationOffset + 
                (distanceToTarget)/2)
            app.spells[spellName].yPosition = (
                app.spellOrbYPosition + yPositionRotationOffset)
        else: 
            app.spells[spellName].xPosition = (
                app.spellOrbXPosition + 
                xPositionRotationOffset - 
                (distanceToTarget)/2)
            app.spells[spellName].yPosition = (
                app.spellOrbYPosition - yPositionRotationOffset)
        app.spells[spellName].displayHeight = app.spells[spellName].imageHeight
    
    # initiating shield spell
    elif(app.spells[spellName].displayType == 'shield'):
        # pick shield alignment depending on which 
        # sector of the screen the mouse is in
        # print(app.mouseScreenSector)
        app.spells[spellName].opacity = 100
        app.spells[spellName].xPosition = (
            app.shieldData[app.mouseScreenSector][0])
        app.spells[spellName].yPosition = (
            app.shieldData[app.mouseScreenSector][1])
        hitboxRotationAngle = app.shieldData[app.mouseScreenSector][2]
        width = int(app.spells[spellName].displayWidth * 0.3)
        height = int(app.spells[spellName].displayHeight * 1)
        [(x_1,y_1),(x_2,y_2),(x_3,y_3),(x_4,y_4)] = (
            applyRectangleRotation(app.spells[spellName].xPosition, 
                                   app.spells[spellName].yPosition, width, 
                                   height, hitboxRotationAngle))
        app.hitbox[spellName] = HitboxAngledRect(
            x_1,y_1,x_2,y_2,x_3,y_3,x_4,y_4,app.spells[spellName])
        h = app.hitbox[spellName]
        h.associatedObject = app.spells[spellName]
        h.belongsTo = 'player'

    # projectile-based spells
    elif((app.spells[spellName].displayType in app.projectileTypeList)):
        # get initial data from spell setup
        frames = app.spells[spellName].animationFrames
        width = app.spells[spellName].imageWidth
        height = app.spells[spellName].imageHeight
        scale = app.spells[spellName].imageScale
        drawBuffer = app.spells[spellName].drawBuffer
        initialX = app.spellOrbXPosition
        initialY = app.spellOrbYPosition

        # register each projectile as either a map or player projectile
        if(app.spells[spellName].displayType == 'mapProjectile'):
            app.activeMapProjectiles.append(spellName)
            # print('added projectile:',spellName,'to active map projectiles')
        elif(app.spells[spellName].displayType == 'playerProjectile'):
            app.activePlayerProjectiles.append(spellName)
            # print('added projectile:',
            #       spellName,'to active player projectiles')

        # create projectile instances using spell data
        # print('projectile Type:',app.spells[spellName].projectileType)
        if(app.spells[spellName].projectileType == 'linear'):
            app.projectile[spellName] = Linear(
                spellName,frames,width,height,scale,drawBuffer,0,initialX,
                (initialY-app.ti['ground'].yOffset),targetX,
                (targetY-app.ti['ground'].yOffset),True)
        elif(app.spells[spellName].projectileType == "pointHoming"):
            app.projectile[spellName] = PointHoming(
                spellName,frames,width,height,scale,drawBuffer,0,initialX,
                initialY,targetX,targetY,True)
        elif(app.spells[spellName].projectileType == "groundbounce"):
            app.projectile[spellName] = Groundbounce(
                spellName,frames,width,height,scale,drawBuffer,0,initialX,
                initialY,targetX,targetY,True)
        else:
            reportError('initiating projectile spell',
                        'INVALID PROJECTILE TYPE',
                        'initiateSpellCast',
                        'projectile type recieved',
                        app.spells[spellName].projectileType,None)
       
        # getting projectile data, and also initiating projectile hitbox
        initiateProjectile(app,spellName)

        # projectiles can optionally inherit player velocity on initiation
        if(app.projectile[spellName].inheritPlayerVelocity):
            if(app.playerFacing == 'right'):
                app.projectile[spellName].xVelocity = (
                    (app.player['x'].currentVelocity)/5)
                app.projectile[spellName].yVelocity = (
                    (-app.player['y'].currentVelocity)/5)
            else:
                app.projectile[spellName].xVelocity = (
                    -app.player['x'].currentVelocity)
                app.projectile[spellName].yVelocity = (
                    -app.player['y'].currentVelocity)
   
    # if no spell type has been recognized, report an error
    else:
        reportError('initiating spell', 'INVALID SPELL DISPLAY TYPE', 
                    'intiateSpellCast', 'display type', 
                    app.spells[spellName].displayType, None)
    
    # start casting spell 
    app.spellData[spellType].spellCastingEnabler = True
    app.spellOrbCharged = False
    app.displayCombo = ''

# plays the spell animation, and removes the spell from 
# app.activeAggressiveSpells when the spell is finished, 
# as well as calls activateSpellEffect ON THE LAST FRAME
def castSpell(app,spellName):
    # checking to make sure we have a valid spell name by attempting to
    # access the value associated with it, and returning an error otherwise
    try:
        spellType = app.spells[spellName].spellType
    except:
        reportError('casting spell', 'INVALID SPELL', 'castSpell', 
                    'spell name', (spellName), 
                    'reference appStart to find valid spells')
    
    # print('casting Spell')
    
    # casting end effect spells
    if(app.spells[spellName].displayType == 'endEffect'):
        spellDirection = app.mouseOrbSide[0].upper()+app.mouseOrbSide[1:]
        if(app.spells[spellName].animationCounter == (
            app.spells[spellName].animationFrames - 1)):

            activateSpellEffect(app,spellName)
        elif(app.spells[spellName].animationCounter == (
            app.spells[spellName].animationFrames)):

            app.spells[spellName].animationCounter = 0
            app.spellData[spellType].drawingSpell = False
            app.spellData[spellType].spellCastingEnabler = False
            app.spellData[spellType].activeSpell = []
            return
    
    # casting shield spell
    elif(app.spells[spellName].displayType == 'shield'):
        app.spells[spellName].animationCounter = 0
        spellDirection = app.mouseScreenSector
        if(app.removeShield):
            activateSpellEffect(app,spellName)
            app.spellData[spellType].drawingSpell = False
            app.spellData[spellType].spellCastingEnabler = False
            app.spellData[spellType].activeSpell = []
            del app.hitbox[spellName]
            app.removeShield = False
    
    # casting projectile type spells
    elif(app.spells[spellName].displayType in app.projectileTypeList):
        # if the spell's associated projectile has already been deleted 
        # (via hitbox collision), then just reset the remaining spell effects
        if((spellName not in app.activePlayerProjectiles) and 
           (spellName not in app.activeMapProjectiles)):
            app.spells[spellName].animationCounter = 0
            app.spellData[spellType].drawingSpell = False
            app.spellData[spellType].spellCastingEnabler = False
            app.spellData[spellType].activeSpell = []
            return
        # casting projectile spells
        else:
            app.spells[spellName].animationCounter %= (
                app.spells[spellName].animationFrames)
            if(app.spells[spellName].projectileType in 
               {'linear','pointHoming','groundbounce'}):
                endCondition = app.projectile[spellName].move()
                if(endCondition):
                    app.spells[spellName].animationCounter = 0
                    app.spellData[spellType].drawingSpell = False
                    app.spellData[spellType].spellCastingEnabler = False
                    app.spellData[spellType].activeSpell = []
                    app.projectile[spellName].deleteMe = True
                    return
            # determining spell travel direction, if it has different animations
            # for it's directions
            if(app.spells[spellName].directional):
                if(app.projectile[spellName].xVelocity >= 0):      
                    spellDirection = 'Right'
                else:
                    spellDirection = 'Left'
            else:
                spellDirection = ''
    # returning an error if the spell display type was not recognized
    else:
        reportError('initiating spell', 'INVALID SPELL DISPLAY TYPE', 
                    'castSpell', 'display type', 
                    app.spells[spellName].displayType, None)
        
    # print(spellDirection)
    # setting the spell's current image path
    spellImagePath = (f'images/spells/{spellName}{spellDirection}_' + 
                      f'{app.spells[spellName].animationCounter}.png')
    app.spellData[spellType].imagePath = spellImagePath
    if(app.spells[spellName].displayType in app.projectileTypeList):
        app.projectile[spellName].imagePath = spellImagePath
    app.spells[spellName].animationCounter += 1
    # print('spell animationCounter:', app.spells[spellName].animationCounter)
    app.spellData[spellType].drawingSpell = True

# actually draws the spell animation sprite
def drawSpell(app,spellName):
    spellType = app.spells[spellName].spellType
    spellImagePath = app.spellData[spellType].imagePath
    if((app.spells[spellName].projectileType == None) and onScreen(
        app, app.spells[spellName].xPosition,
        app.spells[spellName].yPosition,
        app.spells[spellName].drawBuffer)):

        s = app.spells[spellName]
        drawImage(spellImagePath,
                  (s.xPosition+app.screenShakeX),
                  (s.yPosition+app.screenShakeY),
                  width = s.displayWidth, 
                  height = s.displayHeight, 
                  align='center',rotateAngle = 
                  s.displayAngle, opacity = s.opacity)

# actually plays the effect of the spell, should it have an associated effect
# that needs to be handled as a spell specifically
def activateSpellEffect(app,spellName):
    if(spellName == 'testLightSpell'):
        app.lightSources.append(
            LightSource(
                3,
                255,
                (app.spells[spellName].targetX/app.lightmapScalingFactor),
                (app.spells[spellName].targetY/app.lightmapScalingFactor),
                0.95))
    
    elif(spellName == 'levelOneSlimeBall'):
        frameList = ['images/spells/levelOneSlimeBallEndAnimation_0.png' , 
                     'images/spells/levelOneSlimeBallEndAnimation_1.png' , 
                     'images/spells/levelOneSlimeBallEndAnimation_2.png'
                     ]
        displayWidth = app.spells[spellName].displayWidth
        displayHeight = app.spells[spellName].displayHeight
        rotation = app.spells[spellName].displayAngle
        xPosition = app.spells[spellName].xPosition
        yPosition = app.spells[spellName].yPosition
        app.simpleAnimations.append(
            SimpleAnimation(
                app,frameList,3,True,displayWidth,displayHeight,rotation,
                'center',xPosition,yPosition,True,10))

    elif(spellName == 'skySplitter'):
        app.lightSources.append(
            LightSource(
                10,
                255,
                (app.spells[spellName].targetX/app.lightmapScalingFactor),
                (app.spells[spellName].targetY/app.lightmapScalingFactor),
                0.98))
        imageWidth = 500
        imageHeight = 1000
        imageScale = 1
        displayHeight = int(imageHeight * imageScale)
        # print(app.spells[spellName].targetY)
        x = app.spells[spellName].targetX
        y = (app.spells[spellName].targetY - 
             int(displayHeight // 2) -
               app.ti['ground'].yOffset)
        app.projectile['skySplitterBolt'] = Stationary(
            'skySplitterBolt',27,imageWidth,imageHeight,
            imageScale,0,500,x,y,x,y,False,27)
        initiateProjectile(app,'skySplitterBolt')
        app.activeMapProjectiles.append('skySplitterBolt')
        app.screenShakeMagnitude += 15

# PROJECTILE MANAGEMENT
def drawProjectile(app,projectileName):
     if((app.projectile[projectileName].imagePath != None)):
        totalXPosition = (
            app.projectile[projectileName].xPosition + 
            app.projectile[projectileName].xOffset)
        totalYPosition = (
            app.projectile[projectileName].yPosition + 
            app.projectile[projectileName].yOffset)
        # print('totalYPosition:',totalYPosition)
        if((onScreen(app, totalXPosition, totalYPosition, 
                     app.projectile[projectileName].drawBuffer)) or 
                     app.projectile[projectileName].ignoreScreenBounds):
            # print(f'projectile: {projectileName},' + 
            #       f'image: {app.projectile[projectileName].imagePath}')
            # print('xPosition:',app.projectile[projectileName].xPosition)
            # print('yPosition:',app.projectile[projectileName].yPosition)
            drawImage(app.projectile[projectileName].imagePath,
                      (totalXPosition + app.screenShakeX),
                      (totalYPosition + app.screenShakeY),
                      width = app.projectile[projectileName].displayWidth, 
                      height = app.projectile[projectileName].displayHeight, 
                      align='center',
                      rotateAngle = app.projectile[projectileName].displayAngle)

def updateProjectiles(app):
    # update active map projectiles
    for projectileName in app.activeMapProjectiles:
        # updating projectiles that did not originate from player spells
        if(not app.projectile[projectileName].isPlayerSpell):
            endCondition = app.projectile[projectileName].update()
            if(endCondition):
                app.projectile[projectileName].deleteMe = True

        # running projectile deletion procedure for map projectiles
        if(app.projectile[projectileName].deleteMe):
            if(app.projectile[projectileName].isPlayerSpell):
                app.spells[projectileName].xPosition = (
                    app.projectile[projectileName].xPosition + 
                    app.projectile[projectileName].xOffset)
                app.spells[projectileName].yPosition = (
                    app.projectile[projectileName].yPosition)
                app.spells[projectileName].displayAngle = (
                    app.projectile[projectileName].displayAngle)
                activateSpellEffect(app,projectileName)
            elif('insidiousCreature' in app.enemies):
                enemy = app.enemies['insidiousCreature']
                if(projectileName in enemy.multiples['tooth'].checkSet):
                    instanceList = enemy.multiples['tooth'].activeInstances 
                    instanceList.remove(projectileName)
                elif(projectileName in enemy.activeLasers):
                    enemy.activeLasers[projectileName].deleteMe = True
                elif(projectileName in enemy.multiples['bigTooth'].checkSet):
                    instanceList = enemy.multiples['bigTooth'].activeInstances
                    instanceList.remove(projectileName)
            app.activeMapProjectiles.remove(projectileName)
            del app.projectile[projectileName]
            # print('removed map projectile:',projectileName)
            del app.hitbox[projectileName]
            # print('also removed hitbox', projectileName)

    # update active player projectiles
    for projectileName in app.activePlayerProjectiles:
        # updating projectiles that did not originate from player spells
        if(not app.projectile[projectileName].isPlayerSpell):
            endCondition = app.projectile[projectileName].update()
            if(endCondition):
                app.projectile[projectileName].deleteMe = True
            
        # running projectile deletion procedure for player projectiles
        if(app.projectile[projectileName].deleteMe):
            if(app.projectile[projectileName].isPlayerSpell):
                app.spells[projectileName].xPosition = (
                    app.projectile[projectileName].xPosition)
                app.spells[projectileName].yPosition = (
                    app.projectile[projectileName].yPosition)
                app.spells[projectileName].displayAngle = (
                    app.projectile[projectileName].displayAngle)
                activateSpellEffect(app,projectileName)
            app.activePlayerProjectiles.remove(projectileName)
            del app.projectile[projectileName]
            # print('removed player projectile:', projectileName)
            del app.hitbox[projectileName]
            # print('also removed hitbox', projectileName)

# assigning projectile-specific data and iniating it's associated hitbox
def initiateProjectile(app,projectileName):
    # setup for ghost sword player spell
    if(projectileName == 'ghostSword'):
        p = app.projectile[projectileName]
        p.directionalAcceleration = 10
        p.maxVelocity = 100
        p.damage = 25
        p.initialYOffset = app.ti['ground'].yOffset
        xAdjustment = int(p.displayWidth * 0.1)
        yAdjustment = int(p.displayWidth * 0.9)
        initiateHitbox(app,projectileName,p,'player',
                       xAdjustment,yAdjustment,'hitboxAngledRect')
    # setup for a tooth-type projectile from Insidious Creature
    elif(('insidiousCreature' in app.enemies) and 
         (projectileName in 
          app.enemies['insidiousCreature'].multiples['tooth'].checkSet)):
        p = app.projectile[projectileName]
        p.directionalAcceleration = 5
        p.maxVelocity = 100
        p.damage = 5
        p.initialYOffset = app.ti['ground'].yOffset
        xAdjustment = int(p.displayWidth * 0)
        yAdjustment = int(p.displayWidth * 0.75)
        # print('added new tooth!',projectileName)
        initiateHitbox(app,projectileName,p,'enemy',
                       xAdjustment,yAdjustment,'hitboxAngledRect')
    # setup for a laser type projectile from Insidious Creature
    elif(('insidiousCreature' in app.enemies) and 
         (projectileName in 
          app.enemies['insidiousCreature'].multiples['laser'].checkSet)):
        p = app.projectile[projectileName]
        p.directionalAcceleration = 10
        p.maxVelocity = 1000
        p.damage = 10
        p.initialYOffset = app.ti['ground'].yOffset
        xAdjustment = int(p.displayWidth * 0)
        yAdjustment = int(p.displayHeight * 0.7)
        # print('added new laser!',projectileName)
        initiateHitbox(app,projectileName,p,'enemy',
                       xAdjustment,yAdjustment,'hitboxAngledRect')
    # setup for the level one slime ball player spell
    elif(projectileName == 'levelOneSlimeBall'):
        p = app.projectile[projectileName]
        p.directionalVelocity = 10
        p.lifespan = app.stepsPerSecond * 3
        p.maxBounces = 5
        p.gravitationalAcceleration = 1
        p.initialYOffset = app.ti['ground'].yOffset
        p.groundYIndex = app.ti['ground'].initialTileYPosition
        p.reboundCoefficient = 0.8
        p.radius = int(p.imageScale * 100)
        p.damage = 10
        p.inheritPlayerVelocity = True
        initiateHitbox(app,projectileName,p,'player',0,0,'hitboxCircle')
    # setup for the test ball player spell
    elif(projectileName == 'testBall'):
        p = app.projectile[projectileName]
        p.directionalAcceleration = 0.5
        p.nearnessFactor = 15
        p.maxVelocity = 25
        p.initialYOffset = app.ti['ground'].yOffset
        p.radius = int(p.imageScale * 100)
        p.damping = 10
        initiateHitbox(app,projectileName,p,'player',0,0,'hitboxCircle')
    # setup for the sky splitter bolt projectile
    elif(projectileName == 'skySplitterBolt'):
        p = app.projectile[projectileName]
        p.damage = 8
        p.animationFrameList = [f'images/spells/skySplitterBolt_{i}.png'
                                 for i in range(p.animationFrames)]
        xAdjustment = int(p.displayWidth * 0.3)
        yAdjustment = int(p.displayHeight * 0)
        p.initialYOffset = app.ti['ground'].yOffset
        initiateHitbox(app,projectileName,p,'player',
                       xAdjustment,yAdjustment,'hitboxRect')
    # reporting an error should the projectile name be unrecognized
    else:
        reportError('getting projectile data','UNRECOGNIZED PROJECTILE',
                    'initiateProjectile',
                    'recieved unexpected projectile name',projectileName,None)

# ENEMIES
def initiateTheHideousBeast(app,Physics):
    # setting up position data
    initialX = 100
    initialY = app.ti['ground'].initialTileYPosition-80

    # making the hideous beast an entry in the app.enemies dictionary
    app.enemies['theHideousBeast'] = TheHideousBeast(
        'theHideousBeast',0,500,500,0.7,'center',100,0,
        initialX,initialY,500,10)

    # initiating hitbox for the hideous beast
    THBhitboxXAdjustmentConstant = (
        app.enemies['theHideousBeast'].displayWidth//7)
    THBhitboxYAdjustmentConstant = (
        app.enemies['theHideousBeast'].displayHeight//3)
    initiateHitbox(app,'theHideousBeast',app.enemies['theHideousBeast'],
                   'enemy',THBhitboxXAdjustmentConstant,
                   THBhitboxYAdjustmentConstant,'hitboxRect')

    # creating physics dictionary for the hideous beast
    app.THBPhysics = dict()

    # intiating the hideous beast's physics axes
    app.THBPhysics['x'] = Physics()
    app.THBPhysics['y'] = Physics()

    # tuning the hideous beast's physics parameters
    app.THBPhysics['x'].mass = 150
    app.THBPhysics['y'].mass = 150
    app.THBPhysics['x'].setThrust = 700
    app.THBPhysics['x'].setFrictionConstant = -20
    app.THBPhysics['x'].frictionConstant = -20
    app.THBPhysics['y'].setThrust = 700
    app.THBPhysics['y'].setFrictionConstant = -20
    app.THBPhysics['y'].frictionConstant = -20
    app.setGravity = -150

def initiateInsidiousCreature(app,Physics):
    # setting up initial position data
    initialX = app.screenWidth * 1.5
    initialY = app.ti['ground'].initialTileYPosition-80

    # making the Insidious Creature an entry in the app.enemies dictionary
    app.enemies['insidiousCreature'] = InsidiousCreature(
        'insidiousCreature',0,500,500,0.6,'center',100,0,
        initialX,initialY,1500,15)

    # establishing the hitbox radius for the Insidious Creature
    app.enemies['insidiousCreature'].radius = int(
        app.enemies['insidiousCreature'].displayWidth * 0.4)

    # initiating hitbox for the insidious creature)
    initiateHitbox(app,'insidiousCreature',app.enemies[
        'insidiousCreature'],'enemy',0,0,'hitboxCircle')

    # insidious creature will be shortened to ic for clarity

    # creating physics dictionary for the insidious creature
    app.icPhysics = dict()

    # intiating the insidious creature's physics axes
    app.icPhysics['x'] = Physics()
    app.icPhysics['y'] = Physics()

    # tuning the insidious creature's physics parameters
    app.icPhysics['x'].mass = 30
    app.icPhysics['y'].mass = 30
    app.icPhysics['x'].setThrust = 750
    app.icPhysics['x'].setFrictionConstant = -20
    app.icPhysics['x'].frictionConstant = -20
    app.icPhysics['y'].setThrust = 750
    app.icPhysics['y'].setFrictionConstant = -15
    app.icPhysics['y'].frictionConstant = -15

def updateEnemies(app):
    # initiating empty deletion set
    enemiesToDelete = set()
    # looping through currently active enemies
    for enemyName in app.enemies:
        enemy = app.enemies[enemyName]
        enemy.move(app)
        enemy.updateImage(app)
        enemy.updateState(app)
        # checking for deletion
        if(enemy.deleteMe):
            if(enemyName == app.currentBoss):
                app.currentBoss = None
            enemiesToDelete.add(enemyName)
    
    # deleting enemies
    for enemyToDelete in enemiesToDelete:
        del app.enemies[enemyToDelete]
        del app.hitbox[enemyToDelete]

def drawEnemies(app):
    for enemyName in app.enemies:
        enemy = app.enemies[enemyName]
        drawImage(enemy.imagePath, 
                  (enemy.xPosition+enemy.xOffset+app.screenShakeX), 
                  (enemy.yPosition+enemy.yOffset+app.screenShakeY), 
                  width = enemy.displayWidth, 
                  height = enemy.displayHeight, 
                  rotateAngle = enemy.displayAngle, 
                  align = enemy.alignment )

# GUI
def updateGui(app):
    if(app.gameState == 'main'):
        # fading out start cutscene once game has started
        if(app.startCutsceneOverlayOpacity > 5):
            app.startCutsceneOverlayOpacity = max(
                (app.startCutsceneOverlayOpacity*0.95), 0)
        else:
            app.startCutsceneOverlayOpacity = 0
        
        # recharging mana if player is not currently casting a spell
        if((app.playerMana < app.playerMaxMana) and 
           (not app.castingSpell)):
            if((app.playerManaRechargeCounter % app.playerManaRechargeSpeed) 
               == 0):
                app.playerMana += (app.playerManaRechargeCounter/100)
            app.playerManaRechargeCounter += 1
            if(app.playerMana >= app.playerMaxMana):
                app.playerManaRechargeCounter = 0
                app.playerMana = app.playerMaxMana
        
        # setting game state to 'dead' if player has died
        if(app.playerHealth == 0):
            app.gameState = 'dead'
        
        # changing position of spell scroll
        if((app.displaySpellScroll) and (
            app.gui['spellScroll'].yPosition > app.spellScrollTopYPosition)):
            
            app.gui['spellScroll'].yPosition = max(
                int(app.gui['spellScroll'].yPosition * app.scrollOpenSpeed)-1 , 
                app.spellScrollTopYPosition)
        
        elif((not(app.displaySpellScroll)) and (
            app.gui['spellScroll'].yPosition < app.spellScrollBottomYPosition)):
            
            app.gui['spellScroll'].yPosition = min(
                int(app.gui['spellScroll'].yPosition * app.scrollCloseSpeed)+1 ,
                app.spellScrollBottomYPosition)
        
        # indexing combo counter
        if(app.comboCounter != 0):
            app.comboCounter -= 1
        
        # adjusting combo shake
        if(app.comboShake > 0):
            app.comboShake = max(int(app.comboShake * 0.9)-1, 0)
        
        # updating edge darkness and timer
        if(abs(app.totalXOffset) > app.edgeFadeBounds):
            app.edgeDarknessOpacity = min(
                100, 
                int((abs(app.totalXOffset) - app.edgeFadeBounds) * 
                    app.edgeFadeRate))
            if(app.edgeDarknessOpacity == 100):
                app.edgeFadeDeathTimer += 1
            else:
                app.edgeFadeDeathTimer = 0
            if(app.edgeFadeDeathTimer >= 60):
                app.gameState = 'fadeCutscene'
            # print(app.edgeDarknessOpacity)
        else:
            app.edgeDarknessOpacity = max(
                ((app.edgeDarknessOpacity * 0.9) - 1), 0)
    
    # handling start button size change for mouse reactivity 
    # and image change if clicked
    elif((app.gameState == 'menu') or (app.gameState == 'startCutscene')):
        if(app.gui['menuPlayButton'].mouseOver):
            app.gui['menuPlayButton'].imageScale = (
                app.gui['menuPlayButton'].imageScale_2 * 1.1)
        else:
            app.gui['menuPlayButton'].imageScale = (
                app.gui['menuPlayButton'].imageScale_2)
        if(app.gameState == 'startCutscene'):
            if(app.gui['menuPlayButton'].imagePath == 
               'images/GUI/menuPlayButtonOff.png'):
               
                app.gui['menuPlayButton'].imagePath = (
                    'images/GUI/menuPlayButtonOn.png')
                app.startCutsceneOverlayOpacity = 1
            if(app.startCutsceneOverlayOpacity != 100):
                app.startCutsceneOverlayOpacity = min(
                    (app.startCutsceneOverlayOpacity*1.05), 100)
            else:
                app.gameState = 'main'
    
    # handling edge fade death cutscene
    elif(app.gameState == 'fadeCutscene'):
        # play crunch sounds
        app.edgeFadeDeathTimer += 1
        if(app.edgeFadeDeathTimer >= 150):
            app.playerHealth = 0
            app.gameState = 'dead'
    
    # handling death cutscene and restart logic
    elif(app.gameState == 'dead'):
        if(app.deathCutsceneOverlayOpacity < 100):
            if(app.deathCutsceneOverlayOpacity == 0):
                app.deathCutsceneOverlayOpacity = 0.1
            app.deathCutsceneOverlayOpacity = min(
                (app.deathCutsceneOverlayOpacity * 
                 ((0.1)+(50/(max(app.deathCutsceneOverlayOpacity-50, 50))))), 
                 100)
        else:
            gameSetup(app)

    # handling win cutscene
    elif(app.gameState == 'winCutscene'):
        # print(app.winTimer)
        if(app.winTimer >= (app.stepsPerSecond * 2)):
            app.winCutsceneOverlayOpacity = min(
                (app.winCutsceneOverlayOpacity * (1.1)), 100)
            if(app.winCutsceneOverlayOpacity == 100):
                app.gameState = 'win'
                app.gui['license'].displayAngle = 90
        app.winTimer += 1
    
    # handling win state and license animation
    if(app.gameState == 'win'):
        if(app.winCutsceneOverlayOpacity != 0):
            app.winCutsceneOverlayOpacity = max(
                ((app.winCutsceneOverlayOpacity * (0.95))-1), 0)
        if(app.gui['license'].imageScale != 1):
            app.gui['license'].imageScale = min(
                (app.gui['license'].imageScale * (1.05)), 1)
            app.gui['license'].displayAngle += app.lisenceRotationSpeed
            app.lisenceRotationSpeed *= 0.99
        else:
            if(app.gui['license'].displayAngle != 0):
                app.gui['license'].displayAngle = 0
                app.winTimer = 0
            if(app.winTimer > (app.stepsPerSecond * 5)):
                if(app.restartPromptOpacity != app.restartPromptMaxOpacity):
                    app.restartPromptOpacity += 1
        app.winTimer += 1    

def drawGuiElement(app,elementName,xOffset=0,yOffset=0):
    # establishing data
    path = app.gui[elementName].imagePath
    x = app.gui[elementName].xPosition + xOffset
    y = app.gui[elementName].yPosition + yOffset
    width = int(
        app.gui[elementName].imageWidth * app.gui[elementName].imageScale)
    height = int(
        app.gui[elementName].imageHeight * app.gui[elementName].imageScale)
    opacity = app.gui[elementName].opacity
    displayAngle = app.gui[elementName].displayAngle
    alignment = app.gui[elementName].alignment
    # drawing
    drawImage(path,x,y,width=width,height=height,rotateAngle=displayAngle,
              opacity=opacity,align=alignment)       

def drawCombo(app):
    # setting up initial data
    i = 0
    comboShakeX = random.randint(-app.comboShake, app.comboShake)
    comboShakeY = random.randint(-app.comboShake, app.comboShake)

    # initializing splash text dictionary, and respective entries
    splashTextDict = dict()
    splashTextDict['combo failed!'] = 'images/GUI/comboFailed.png'
    splashTextDict['overcharged!'] = 'images/GUI/comboOvercharged.png'
    splashTextDict['insufficient mana!'] = (
        'images/GUI/comboInsufficientMana.png')
    splashTextDict['cancel'] = 'images/GUI/comboChargeCancelled.png'

    # checking if the display combo is one of the special splash tects, and 
    # displaying the appopriate image from the splash text dictionary if so
    if(app.displayCombo in splashTextDict):
        if(app.comboCounter != 0):
            splashX = (
                app.comboImageTop + (i * app.comboImageSpacing) + comboShakeX)
            splashY = (app.comboImageLeft + comboShakeY)
            splashWidth = int(app.comboDetailTextWidth * app.comboImageScale)
            splashHeight = int(app.comboImageSize * app.comboImageScale)
            drawImage(splashTextDict[app.displayCombo], splashX, splashY, 
                      width = splashWidth, height = splashHeight)
    # otherwise, we loop through the characters in the display combo and display
    # their associated image
    else:
        for char in app.displayCombo:
            comboImagePath = f'images/GUI/combo_{char}.PNG'
            # if the image path does not exist, we report an error
            # this is likely the result of an improperly named image, or
            # an invalid combo
            if(not(os.path.exists(comboImagePath))):
                reportError('accessing desired combo indicator file', 
                            'IMAGE COULD NOT BE FOUND', 'drawCombo', 
                            'File name', comboImagePath, None)
            comboX = (
                app.comboImageTop + (i * app.comboImageSpacing) + comboShakeX)
            comboY = (app.comboImageLeft + comboShakeY)
            comboWidth = int(app.comboImageSize * app.comboImageScale)
            comboHeight = int(app.comboImageSize * app.comboImageScale)
            drawImage(comboImagePath, comboX, comboY, 
                      width = comboWidth, height = comboHeight)
            i += 1

def drawDRO(app):
    # drawing base element
    drawGuiElement(app,'wizardDRO')
    
    # establishing data
    droHeight = int(
        app.gui['wizardDRO'].imageHeight * app.gui['wizardDRO'].imageScale)
    droWidth = int(
        app.gui['wizardDRO'].imageWidth * app.gui['wizardDRO'].imageScale)
    droBarMaxWidth = 97
    droBarHeight = int(droHeight // 6)
    droHealthBarWidth = max(
        droBarMaxWidth*(app.playerHealth/app.playerMaxHealth),0.001)
    droManaBarWidth = droBarMaxWidth*(app.playerMana/app.playerMaxMana)
    droBarLeft = app.gui['wizardDRO'].xPosition + int(droWidth // 8.9) 
    droHealthBarTop = app.gui['wizardDRO'].yPosition + int(droHeight // 3)
    droManaBarTop = droHealthBarTop + int(droHeight // 2.5) 
    droBarOpacity = 50
    droBarFill = RGB(50,209,2)
    
    # drawing health and mana bars
    drawRect(droBarLeft,droHealthBarTop,droHealthBarWidth,droBarHeight,
             fill = droBarFill, opacity = droBarOpacity)
    drawRect(droBarLeft,droManaBarTop,droManaBarWidth,droBarHeight,
             fill = droBarFill, opacity = droBarOpacity)
    
    # drawing decorative grille over top
    drawGuiElement(app,'wizardDROGrille')

def drawBossBar(app):
    # establishing data
    enemy =  app.enemies[app.currentBoss]
    bossBarHeight = int(
        app.gui['bossBar'].imageHeight * app.gui['bossBar'].imageScale)
    bossBarWidth = int(
        app.gui['bossBar'].imageWidth * app.gui['bossBar'].imageScale)
    bossHealthMaxWidth = int(bossBarWidth * 0.85)
    bossHealthWidth = (bossHealthMaxWidth * enemy.health / enemy.maxHealth)
    bossHealthHeight = bossBarHeight * 0.09
    bossHealthLeft = app.gui['bossBar'].xPosition - (bossBarWidth * 0.42)
    bossHealthTop = app.gui['bossBar'].yPosition + (bossBarHeight * 0.1)
    
    # checking enemy health first
    if(enemy.health != 0):
        # drawing boss bar elements and rectangular bar itself
        drawGuiElement(app,'bossBarBackground')
        drawRect(bossHealthLeft, bossHealthTop, bossHealthWidth, 
                 bossHealthHeight, fill = 'crimson')
        drawGuiElement(app,f'{app.currentBoss}Title')
        drawGuiElement(app,'bossBar')
    else:
        # silly death mesage should the boss be dead
        print('he hath exploded')

def drawGui(app):
    # handling fade cutscene
    if(app.gameState == 'fadeCutscene'):
        drawRect(0,0,app.screenWidth,app.screenHeight,fill='black')
    
    if(app.gameState in {'main','dead','paused','winCutscene','win'}):
        if(app.gameState != 'fadeCutscene'):
            # drawing wizard dro, the health and mana indicator
            drawDRO(app)
            
            # drawing current combo
            drawCombo(app)
            
            # drawing boss bar 
            if(app.currentBoss != None):
                drawBossBar(app)

            if(app.gameState != 'paused'):
                # displaying spell scroll
                if(((app.displaySpellScroll) and (
                    app.gui['spellScroll'].yPosition >= 
                    app.spellScrollTopYPosition)) or 
                    ((not(app.displaySpellScroll)) and 
                     (app.gui['spellScroll'].yPosition < 
                      app.spellScrollBottomYPosition))):
                    scrollXOffset = random.randint(
                        -app.scrollShakeMagnitude,app.scrollShakeMagnitude)
                    scrollYOffset = random.randint(
                        -app.scrollShakeMagnitude,app.scrollShakeMagnitude)
                    drawGuiElement(
                        app,'spellScroll',scrollXOffset,scrollYOffset)
        
        # displaying edge overlay
        if(app.edgeDarknessOpacity != 0):
            drawRect(0,0,app.screenWidth,app.screenHeight,
                     fill =' black',opacity = app.edgeDarknessOpacity)

        # displaying tutorial tip
        drawLabel('press SPACE for tutorial',10,(app.screenHeight-10),
                  fill = 'lightGray',align='left-bottom')
        
        # displaying pause screen
        if(app.gameState == 'paused'):
            drawRect(0,0,app.screenWidth,app.screenHeight,
                     fill = 'black', opacity = app.pauseScreenOpacity)
            drawGuiElement(app,'pauseText')
        
        # displaying death screen
        elif(app.gameState == 'dead'):
            drawRect(0,0,app.screenWidth,app.screenHeight,
                     fill = 'black', opacity = app.deathCutsceneOverlayOpacity) 
            drawGuiElement(app,'deathText')

    # displaying start menu elements
    elif(app.gameState in {'menu','startCutscene'}):
        drawGuiElement(app,'titleScreen')
        drawGuiElement(app,'menuPlayButton')
    
    # displaying tutorial
    elif(app.gameState == 'tutorial'):
        drawGuiElement(app,'tutorial')

    # displaying win screen and win cutscene overlay
    if(app.gameState in {'win', 'winCutscene'}):
        if(app.gameState == 'win'):
            drawGuiElement(app,'winScreen')
            drawGuiElement(app,'license')
            if(app.restartPromptOpacity != 0):
                drawLabel("press 'r' to restart",(app.screenWidth // 2), 
                          (app.screenHeight - 15), fill = 'white', 
                          size = 15, align = 'center', 
                          opacity = app.restartPromptOpacity)
        if(app.winCutsceneOverlayOpacity != 0):
            drawRect(0,0,app.screenWidth,app.screenHeight,
                     fill = 'black', opacity = app.winCutsceneOverlayOpacity)

    # displaying start cutscene overlay
    if(app.startCutsceneOverlayOpacity != 0):
        drawRect(0,0,app.screenWidth,app.screenHeight,
                 fill = 'black', opacity = app.startCutsceneOverlayOpacity)  

# PICKUPS
def deletePickups(app):
    deleteSet = set()
    for pickup in app.pickups:
        if(app.pickups[pickup].deleteMe):
            deleteSet.add(pickup)
    for pickup in deleteSet:
        del app.hitbox[pickup]
        del app.pickups[pickup]

# SCREEN SHAKE
def updateScreenShake(app):
    if(app.screenShakeMagnitude != 0):

        app.screenShakeX = random.randint(
            -app.screenShakeMagnitude,app.screenShakeMagnitude)
        app.screenShakeY = random.randint(
            -app.screenShakeMagnitude,app.screenShakeMagnitude)

        if((app.screenShakeCounter % app.screenShakeDissapationSpeed) == 0):
            app.screenShakeMagnitude = int(app.screenShakeMagnitude * 0.9)
        app.screenShakeCounter += 1
    else:
        app.screenShakeCounter = 0

# HITBOX & HITBOX MANAGEMENT
def initiateHitbox(app,name,associatedObject,belongsTo,
                   xAdjustment,yAdjustment,hitboxType):
    # initiating cuircular hitboxes
    if(hitboxType == 'hitboxCircle'):
        # print('initiated circle')
        x = associatedObject.xPosition
        y = associatedObject.yPosition
        radius = associatedObject.radius
        app.hitbox[name] = HitboxCircle(x,y,radius)
        h = app.hitbox[name]
        h.associatedObject = associatedObject
        h.belongsTo = belongsTo

    # initiating rectangular hitboxes that are not rotated
    elif(hitboxType == 'hitboxRect'):
        # these calculations work for objects that are 
        # displayed relative to their CENTER
        left = (associatedObject.xPosition - 
                (associatedObject.displayWidth//2) + 
                xAdjustment)
        right = (associatedObject.xPosition + 
                 (associatedObject.displayWidth//2) - 
                 xAdjustment)
        top = (associatedObject.yPosition - 
               (associatedObject.displayHeight//2) + 
               yAdjustment)
        bottom = (associatedObject.yPosition + 
                  (associatedObject.displayHeight//2) - 
                  yAdjustment)
        app.hitbox[name] = HitboxRect(left,right,top,bottom)
        h = app.hitbox[name]
        h.xAdjustment = xAdjustment
        h.yAdjustment = yAdjustment
        h.associatedObject = associatedObject
        h.belongsTo = belongsTo

    # iniating angled rectangular hitboxes
    elif(hitboxType == 'hitboxAngledRect'):
        # print('initiated AngledRect')
        centerX = associatedObject.xPosition
        centerY = associatedObject.yPosition
        targetX = associatedObject.targetX
        targetY = associatedObject.targetY
        # print(associatedObject.initialYOffset)
        # print(centerX, centerY)
        width = associatedObject.displayWidth - xAdjustment
        height = int(associatedObject.displayHeight) - yAdjustment
        dx = targetX - centerX
        dy = targetY - centerY
        rotationAngle = getAngle(dx, dy, 'degrees')
        # ptc('rotationAngle',rotationAngle)
        [(x_1,y_1),(x_2,y_2),(x_3,y_3),(x_4,y_4)] = applyRectangleRotation(
            centerX, centerY, width, height, rotationAngle)
        app.hitbox[name] = HitboxAngledRect(
            x_1,y_1,x_2,y_2,x_3,y_3,x_4,y_4,associatedObject)
        h = app.hitbox[name]
        h.belongsTo = belongsTo
        # print('coordinates:',p.x_1,p.y_1,p.x_2,p.y_2,p.x_3,p.y_3,p.x_4,p.y_4)
    
    # reporting an error if hitbox type is not recognized
    else:
        reportError('attempting to initiate hitbox',
                    'UNRECOGNIZED HITBOX TYPE',
                    'initiateHitbox',
                    'recieved hitbox type',
                    type(hitboxType),None)
    
def updateHitbox(app,hitbox):
    # updating circular hitboxes
    if(isinstance(hitbox,HitboxCircle)):
        hitbox.align(hitbox.associatedObject)
    
    # updating rectangular hitboxes, except if they are the player's, since
    # in that case there is no associated object to align to
    elif(isinstance(hitbox,HitboxRect)):
        if(hitbox == app.hitbox['player']):
            return
        else:
            hitbox.align(hitbox.associatedObject)
    
    # updating angled rectangular hitboxes
    elif(isinstance(hitbox,HitboxAngledRect)):
        hitbox.align(hitbox.associatedObject)
   
   # reporting an error if hitbox type is unrecognized
    else:
        reportError('attempting to update hitbox',
                    'UNRECOGNIZED HITBOX TYPE',
                    'updateHitbox',
                    'recieved hitbox type',
                    type(hitbox),None)

def displayHitbox(app,hitbox):
    # displaying circular hitboxes
    if(isinstance(hitbox,HitboxCircle)):
        x = hitbox.xPosition + hitbox.xOffset
        y = hitbox.yPosition + hitbox.yOffset
        radius = hitbox.radius
        # ptc('x',x)
        # ptc('y',y)
        # ptc('radius',radius)
        drawCircle(x, y, radius, fill = None, border = 'cyan' )
    
    # displaying rectangular hitboxes
    elif(isinstance(hitbox,HitboxRect)):
        width = hitbox.right - hitbox.left
        height = hitbox.bottom - hitbox.top
        x = hitbox.left + hitbox.xOffset
        y = hitbox.top + hitbox.yOffset
        drawRect(x, y, width, height, fill = None, border = 'red')
    
    # displaying angled rectangular hitboxes
    elif(isinstance(hitbox,HitboxAngledRect)):
        drawPolygon((hitbox.x_1 + hitbox.xOffset), 
                    (hitbox.y_1 + hitbox.yOffset), 
                    (hitbox.x_2 + hitbox.xOffset), 
                    (hitbox.y_2 + hitbox.yOffset), 
                    (hitbox.x_3 + hitbox.xOffset), 
                    (hitbox.y_3 + hitbox.yOffset), 
                    (hitbox.x_4 + hitbox.xOffset), 
                    (hitbox.y_4 + hitbox.yOffset), 
                    fill = None, border = 'magenta')
    
    # returning an error if hitbox type is unrecognized
    else:
        reportError('attempting to display hitbox',
                    'UNRECOGNIZED HITBOX TYPE',
                    'displayHitbox',
                    'recieved hitbox type',
                    type(hitbox),None)

def triggerPlayerCollision(app,hitbox_1,hitbox_2):
    # determining hitbox ownership
    if(hitbox_1.associatedObject == app.playerObject):
        otherHitbox = hitbox_2
    else:
        otherHitbox = hitbox_1
    if(otherHitbox.belongsTo == 'player'):
        # player's projectiles that collide with themselves should not have 
        # adverse effects
        return
    # if either the enemy or the enemy's projectiles hit the player we want
    # to specify their effects
    elif(otherHitbox.belongsTo == 'enemy'):
        # if the enemy's hitbox collides with the player:
        if(isinstance(otherHitbox.associatedObject, TheHideousBeast) or 
           isinstance(otherHitbox.associatedObject, InsidiousCreature)):
            if(app.playerImmunityFrames == 0):
                app.playerHealth =  max(
                    (app.playerHealth - 
                     otherHitbox.associatedObject.playerDamageOnHit), 0)
                app.playerImmunityFrames = (
                    otherHitbox.associatedObject.playerDamageOnHit)
                app.screenShakeMagnitude += 4
        # if an enemy's projectile collides with the player
        elif(isinstance(otherHitbox.associatedObject, Projectile)):
            app.playerHealth = max(
                (app.playerHealth - otherHitbox.associatedObject.damage), 0)
            otherHitbox.associatedObject.deleteMe = True
            app.screenShakeMagnitude += 2
            # if the enemy projectile is a laser we w
            # ant to delete the laser object too
            # print(otherHitbox.associatedObject.name)
            if('insidiousCreature' in app.enemies):
                enemy = app.enemies['insidiousCreature']
                if(otherHitbox.associatedObject.name in 
                   enemy.multiples['laser'].activeInstances):
                    name = otherHitbox.associatedObject.name
                    enemy.activeLasers[name].deleteMe = True
                # print('removed laser on hit')
    # check collisions with pickups
    elif(otherHitbox.belongsTo == 'pickup'):
        pickup = otherHitbox.associatedObject
        # check mana pickup
        if(pickup.pickupType == 'manaPickup'):
            # print('collided with mana pickup!')
            app.playerMana = min(
                app.playerMana + pickup.restorationAmmount, app.playerMaxMana)
            pickup.deleteMe = True
        # check health pickup
        elif(pickup.pickupType == 'healthPickup'):
            # print('collided with health pickup!')
            app.playerHealth = min(
                app.playerHealth + 
                pickup.restorationAmmount, app.playerMaxHealth)
            pickup.deleteMe = True

def triggerEnemyCollision(app,hitbox_1,hitbox_2):
    if(isinstance(hitbox_1.associatedObject, Enemy) and 
       (not (isinstance(hitbox_2.associatedObject, Enemy)))):
        enemyHitbox = hitbox_1    
        otherHitbox = hitbox_2
    elif(isinstance(hitbox_2.associatedObject, Enemy) and 
         (not (isinstance(hitbox_1.associatedObject, Enemy)))):
        enemyHitbox = hitbox_2
        otherHitbox = hitbox_1
    else:
        return
    # check if the enemy has collided with a projectile
    if(isinstance(otherHitbox.associatedObject, Projectile)):
        # if the projectile belongs to the player, 
        # we want to apply the apropriate effect
        if((otherHitbox.belongsTo == 'player') and 
           (not enemyHitbox.associatedObject.invulnerable)):
            # print('contact!:',otherHitbox.associatedObject.name)
            enemyHitbox.associatedObject.health = max(
                enemyHitbox.associatedObject.health - 
                otherHitbox.associatedObject.damage, 0)
            if(not (otherHitbox.associatedObject.name == 'skySplitterBolt')):
                otherHitbox.associatedObject.deleteMe = True
        else:
            return

def triggerShieldCollision(app,hitbox_1,hitbox_2):
    # shield collisions we care about are when the enemy collides with the
        # shield, or if the enemy's projectile collides with the shield
        # we want the shield to break when the enemy collides with it
        # and we want the shield to break when the enemy projectile collides 
        # with it, but to also delete the projectile
        # first we want to check which hitbox belongs to the shield
        if((isinstance(hitbox_1.associatedObject, Spell)) and 
           (hitbox_1.associatedObject.name == 'shield')):
            # print('shield hitbox is one')
            shieldHitbox = hitbox_1
            otherHitbox = hitbox_2
        elif((isinstance(hitbox_2.associatedObject, Spell)) and 
             (hitbox_2.associatedObject.name == 'shield')):
            # print('shield hitbox is two')
            shieldHitbox = hitbox_2
            otherHitbox = hitbox_1
        else:
            return
        # we don't want to consider collisions between the shield, and player
        # related hitboxes, only collisions between the shield and the enemy
        # or an enemy projectile
        if(otherHitbox.belongsTo == 'enemy'):
            if(isinstance(otherHitbox.associatedObject, Enemy)):
                shieldHitbox.associatedObject.opacity = 0
                app.removeShield = True
            elif(isinstance(otherHitbox.associatedObject, Projectile)):
                # removing shield if contacted laser or big tooth
                if('insidiousCreature' in app.enemies):
                    enemy = app.enemies['insidiousCreature']
                    if(not((otherHitbox.associatedObject.name in 
                            enemy.multiples['laser'].activeInstances) or 
                            (otherHitbox.associatedObject.name in 
                             enemy.multiples['bigTooth'].activeInstances))):
                        otherHitbox.associatedObject.deleteMe = True
                        app.removeShield = True
                else:
                    otherHitbox.associatedObject.deleteMe = True
                shieldHitbox.associatedObject.opacity -= 50
                if(shieldHitbox.associatedObject.opacity <= 0):
                    shieldHitbox.associatedObject.opacity = 0
                    app.removeShield = True
                # print('shield collided with enemy projectile!')
        else:
            return   

def triggerCollisionEffect(app,hitbox_1,hitbox_2):
    # check collisions with player
    if((hitbox_1.associatedObject == app.playerObject) or 
       (hitbox_2.associatedObject == app.playerObject)):
        triggerPlayerCollision(app,hitbox_1,hitbox_2)
    
    # check collisions with enemy
    elif(isinstance(hitbox_1.associatedObject, Enemy) or 
         isinstance(hitbox_2.associatedObject, Enemy)):
        triggerEnemyCollision(app,hitbox_1,hitbox_2)

    # check collisions with the player's shield
    if(app.spells['shield'] in app.spellData['defensive'].activeSpell):
        triggerShieldCollision(app,hitbox_1,hitbox_2)    

def checkCollisionType(hitbox_1, hitbox_2):
    result = set()
    for hitbox in [hitbox_1, hitbox_2]:
        if(isinstance(hitbox,HitboxCircle)):
            result.add('hitboxCircle')
        elif(isinstance(hitbox,HitboxRect)):
            result.add('hitboxRect')
        elif((isinstance(hitbox,HitboxAngledRect))):
            result.add('hitboxAngledRect')
        else:
            reportError('attempting to register collisiontype',
                        'UNRECOGNIZED HITBOX TYPE','checkCollisionType',
                        'recieved hitbox type',type(hitbox),None)
    return(result)
    
def runCollisionCalculations(app, hitboxName_1, hitboxName_2):
    # print(app.hitbox)
    hitbox_1 = app.hitbox[hitboxName_1]
    hitbox_2 = app.hitbox[hitboxName_2]
    # print(f'hitbox pair: {hitboxName_1} and {hitboxName_2}')
    # print(f'types: {type(hitbox_1)} and {type(hitbox_2)}')
    # print(f'hitbox_1 type: {type(hitbox_1)}')
    # print(f'hitbox_2 type: {type(hitbox_2)}')

    # check what kind of collision we have to run the calculations for
    collisionType = checkCollisionType(hitbox_1, hitbox_2)

    # collision between two circles
    if(collisionType == {'hitboxCircle'}):
        x_1 = hitbox_1.xPosition + hitbox_1.xOffset
        y_1 = hitbox_1.yPosition + hitbox_1.yOffset
        x_2 = hitbox_2.xPosition + hitbox_2.xOffset
        y_2 = hitbox_2.yPosition + hitbox_2.yOffset
        if(getDistance(x_1,y_1,x_2,y_2) <= (hitbox_1.radius + hitbox_2.radius)):
            triggerCollisionEffect(app, hitbox_1, hitbox_2)
    
    # collision between two rectangles
    elif(collisionType == {'hitboxRect'}):
        left_1 = hitbox_1.left + hitbox_1.xOffset
        right_1 = hitbox_1.right + hitbox_1.xOffset
        top_1 = hitbox_1.top + hitbox_1.yOffset
        bottom_1 = hitbox_1.bottom + hitbox_1.yOffset
        left_2 = hitbox_2.left + hitbox_2.xOffset
        right_2 = hitbox_2.right + hitbox_2.xOffset
        top_2 = hitbox_2.top + hitbox_2.yOffset
        bottom_2 = hitbox_2.bottom + hitbox_2.yOffset
        xOverlap = ((left_1 <= left_2 <= right_1) or 
                    (left_2 <= left_1 <= right_2))
        yOverlap = ((top_1 <= top_2 <= bottom_1) or
                     (top_2 <= top_1 <= bottom_2))
        # print('')
        # ptc('hitbox_1.left',hitbox_1.left)
        # ptc('hitbox_1.xOffset',hitbox_1.xOffset)
        # ptc('left_1',left_1)
        # ptc('right_1',right_1)
        # ptc('hitbox_2.left',hitbox_2.left)
        # ptc('hitbox_2.xOffset', hitbox_2.xOffset)
        # ptc('left_2',left_2)
        # ptc('right_2',right_2)
        # ptc('xOverlap',xOverlap)
        # ptc('yOverlap',yOverlap)
        if(xOverlap and yOverlap):
            triggerCollisionEffect(app, hitbox_1, hitbox_2)
            # print('both rectangles')
    
    # collision between two angled rectangles
    elif(collisionType == {'hitboxAngledRect'}):
        hVertList_1 = []
        for i in hitbox_1.getVertList():
            hVertList_1.append(
                [(i[0] + hitbox_1.xOffset),(i[1] + hitbox_1.yOffset)])
        hVertList_2 = []
        for i in hitbox_2.getVertList():
            hVertList_2.append(
                [(i[0] + hitbox_2.xOffset),(i[1] + hitbox_2.yOffset)])
        if(checkConvexPolygonIntersection(hVertList_1,hVertList_2) or 
           checkConvexPolygonIntersection(hVertList_2,hVertList_1)):
            triggerCollisionEffect(app, hitbox_1, hitbox_2)      
    
    # collision between one circle and one rectangle
    elif(collisionType == {'hitboxCircle', 'hitboxRect'}):
        if(isinstance(hitbox_1,HitboxCircle)):
            hitboxCircle = hitbox_1
            hitboxRect = hitbox_2
        else:
            hitboxCircle = hitbox_2
            hitboxRect = hitbox_1
        left = hitboxRect.left - hitboxCircle.radius + hitboxRect.xOffset
        right = hitboxRect.right + hitboxCircle.radius + hitboxRect.xOffset
        top = hitboxRect.top - hitboxCircle.radius + hitboxRect.yOffset
        bottom = hitboxRect.bottom + hitboxCircle.radius + hitboxRect.yOffset
        x = hitboxCircle.xPosition + hitboxCircle.xOffset
        y = hitboxCircle.yPosition + hitboxCircle.yOffset
        if((left <= x <= right) and (top <= y <= bottom)):
            triggerCollisionEffect(app, hitbox_1, hitbox_2)
            # print('one circle, one rectangle')
    
    # collision between one circle and one angled rectangle
    elif(collisionType == {'hitboxCircle', 'hitboxAngledRect'}):
        if(isinstance(hitbox_1,HitboxCircle)):
            hitboxCircle = hitbox_1
            hitboxAngledRect = hitbox_2
        else:
            hitboxCircle = hitbox_2
            hitboxAngledRect = hitbox_1
        hARVertList = []
        for i in hitboxAngledRect.getVertList():
            hARVertList.append([(i[0] + hitboxAngledRect.xOffset),
                                (i[1] + hitboxAngledRect.yOffset)])
        circleVert = [[(hitboxCircle.xPosition + hitboxCircle.xOffset),
                       (hitboxCircle.yPosition + hitboxCircle.yOffset)]] 
        distanceCheck = False
        for [hARx,hARy] in hARVertList:
            if(getDistance(hARx,hARy,circleVert[0][0],circleVert[0][1]) <= 
               hitboxCircle.associatedObject.radius):
                distanceCheck = True
        if(checkConvexPolygonIntersection(circleVert,hARVertList) or 
           distanceCheck):
            triggerCollisionEffect(app, hitbox_1, hitbox_2)
    
    # collision between one rectangle and one angled rectangle
    elif(collisionType == {'hitboxRect', 'hitboxAngledRect'}):
        if(isinstance(hitbox_1,HitboxRect)):
            hitboxRect = hitbox_1
            hitboxAngledRect = hitbox_2
        else:
            hitboxRect = hitbox_2
            hitboxAngledRect = hitbox_1

        hARVertList = []
        # print('hAR before:',hARVertList)
        for i in hitboxAngledRect.getVertList():
            hARVertList.append([(i[0] + hitboxAngledRect.xOffset),
                                (i[1] + hitboxAngledRect.yOffset)])
        # print('hAR after:',hARVertList)

        hRVertList = []
        for i in hitboxRect.getVertList():
            hRVertList.append([(i[0] + hitboxRect.xOffset),
                               (i[1] + hitboxRect.yOffset)])
        # print(hRVertList)
   
        if(checkConvexPolygonIntersection(hARVertList,hRVertList) or 
           checkConvexPolygonIntersection(hRVertList,hARVertList)):
            triggerCollisionEffect(app, hitbox_1, hitbox_2)
    
    # report an error if collision type is unrecognized
    else:
        reportError('attempting to run collision calculations',
                    'UNRECOGNIZED COLLISION TYPE','runCollisionCalculations',
                    'recieved collision type',collisionType,None)

def checkCollisions(app):
    # temporary debugging slowdown for collision checks
    # if((app.hitboxCounter % 20) != 0):
    #     app.hitboxCounter += 1
    #     return

    for hitboxName_1 in app.hitbox:
        for hitboxName_2 in app.hitbox:
            if(hash(hitboxName_1) > hash(hitboxName_2)):
                runCollisionCalculations(app, hitboxName_1, hitboxName_2)

    # part of debug slowdown
    # app.hitboxCounter += 1  

    # THEORY FOR METHOD                
    # loop through every pair of projectiles that currently exist
    # for A in dict:
    #    for B in dict:
    #        if hash(A) > hash(B) (will avoid checking if it collides with self)
    # check all collisions except if keys are indentical
    # dont double check collisions, it's likely that hash of each name will be
    # different, so ONLY check the ones where hash(A) > hash(B) for isntance

# COMBO MANAGEMENT
def setupCombos(app):
    # initializing combo data sets
    app.fullComboSet = set()
    app.fullLetterSet = set()
    # getting the combos from all created spells and adding them to the 
    # combo data sets as appropriate
    for spell in app.spells:
        currentCombo = app.spells[spell].combo
        # print('current spell:',app.spells[spell].name)
        for letter in currentCombo:
            app.fullLetterSet.add(letter)
        app.fullComboSet.add(currentCombo)

    # adding cancel combo
    for letter in app.cancelCombo:
        app.fullLetterSet.add(letter)
    app.fullComboSet.add(app.cancelCombo)

    # ptc('app.fullComboSet',app.fullComboSet)
    # ptc('app.fullLetterSet',app.fullLetterSet)

# helper function to detect if our combo in progress is part of any 
# full combo that we actually have
def matchesCombo(app):
    combosIn = 0
    for possibleCombo in app.fullComboSet:
        letterMatch = True
        # checking letter order
        for i in range(len(app.comboInProgress)):
            if(app.comboInProgress[i] != possibleCombo[i]):
                letterMatch = False
                break
        if(letterMatch):
            combosIn += 1
            # print(f'comboInProgrgress {app.comboInProgress}' + 
            #       f'is in full combo {possibleCombo}!')
            if(app.comboInProgress == possibleCombo):
                # print('combo complete!',app.comboInProgress
                #       ,'is',possibleCombo)
                # for spellType in app.spellTypes:
                #     print(spellType)
                #     print('drawing:',app.spellData[spellType].drawingSpell)
                    # print('casting enabler:',
                    #       app.spellData[spellType].spellCastingEnabler)
                return app.comboInProgress
    return(combosIn > 0)

def detectCombos(app,currentKey):
    # don't run combo detection if the spell orb is charged, or if the combo
    # we want is part of the cancel combo
    if((not app.spellOrbCharged) or (currentKey in app.cancelCombo)):
        app.comboShake = 0
        app.comboInProgress += currentKey
        app.displayCombo = app.comboInProgress
        # ptc('comboInProgress',app.comboInProgress)
        comboMatched = matchesCombo(app)
        # invalid combo recieved
        if(comboMatched == False):
            app.comboCounter = 30
            app.comboShake += 10
            app.displayCombo = 'combo failed!'
            app.comboInProgress = ''
        elif(comboMatched != True):
            # cancel combo recieved
            if(comboMatched == app.cancelCombo):
                # print('charged Spell Canceled')
                chargeSpell(app,'cancel')
                app.comboCounter = 30
                app.comboShake += 10
                app.displayCombo = 'cancel'
                app.comboInProgress = ''
            for spell in app.spells:
                if(comboMatched == app.spells[spell].combo):
                    # print(f'charging spell {app.spells[spell].name}' + 
                    #       f'with corresponding combo {comboMatched}. ' + 
                    #       f'({comboMatched} = {app.spells[spell].combo})')
                    chargeSpell(app,app.spells[spell].name)
                    app.comboInProgress = ''

# APP EVENT HANDLERS
def onKeyPress(app,key):
    if(app.gameState == 'main'):
        # registeing keypresses for combos
        if(key in app.fullLetterSet):
            detectCombos(app,key)
        
        # checking if debug features should be enabled
        if(key == '?'):
            if(app.debugFeaturesEnabled):
                app.debugFeaturesEnabled = False
                app.debugFeatureDisplayText = []
            else:
                app.debugFeaturesEnabled = True
                app.debugFeatureDisplayText.append('debug features enabled!')
        
        # debug features
        if(app.debugFeaturesEnabled):
            # make the player basically unkillable
            if(key == ']'):
                app.playerHealth = 10000
                app.playerMaxHealth = 10000
                playerHealthString = ('player health set to ' + 
                                      f'{app.playerMaxHealth}')
                if(not (playerHealthString in app.debugFeatureDisplayText)):
                    app.debugFeatureDisplayText.append(playerHealthString)
            # put insidious creature one attack away 
            # from the next phase checkpoint
            if(key == '['):
                app.enemies['insidiousCreature'].health = (
                    app.enemies['insidiousCreature'].phaseCheckpoint + 5)
                insidiousCreatureHealthString = (
                    'insidiousCreature health set to' + 
                    f'{app.enemies['insidiousCreature'].health}')
                if(not (insidiousCreatureHealthString in 
                        app.debugFeatureDisplayText)):
                    app.debugFeatureDisplayText.append(
                        insidiousCreatureHealthString)
            # display hitboxes
            if(key == "'"):
                if(app.displayHitboxes):
                    app.displayHitboxes = False
                    app.debugFeatureDisplayText.remove('displaying hitboxes')
                else:
                    app.displayHitboxes = True
                    app.debugFeatureDisplayText.append('displaying hitboxes')
            # display the screen zones
            if(key == ';'):
                if(app.displayScreenZones):
                    app.displayScreenZones = False
                    app.debugFeatureDisplayText.remove(
                        'displaying screen zones')
                else:
                    app.displayScreenZones = True
                    app.debugFeatureDisplayText.append(
                        'displaying screen zones')
            # display shield positions on the screen
            if(key == '.'):
                if(app.displayShieldPositions):
                    app.displayShieldPositions = False
                    app.debugFeatureDisplayText.remove(
                        'displaying shield positions')
                else:
                    app.displayShieldPositions = True
                    app.debugFeatureDisplayText.append(
                        'displaying shield positions')
            # print mouse screen sector on click
            if(key == ','):
                if(app.printMouseScreenSector):
                    app.printMouseScreenSector = False
                    app.debugFeatureDisplayText.remove(
                        'will display mouse screen sector on click')
                else:
                    app.printMouseScreenSector = True
                    app.debugFeatureDisplayText.append(
                        'will display mouse screen sector on click')
    
    # checking for pause button
    if(app.gameState in {'main', 'paused'}):
        if(key == 'escape'):
            if(app.gameState == 'paused'):
                app.gameState = 'main'
            else:
                app.gameState = 'paused'

    # checking for tutorial button
    if(app.gameState in {'main', 'paused', 'tutorial'}):
        if(key == 'space'):
            if(app.gameState in {'main', 'paused'}):
                app.gameState = 'tutorial'
            elif(app.gameState == 'tutorial'):
                app.gameState = 'main'

    # checking for reset button
    if(app.gameState == 'win'):
        if(key == 'r'):
            gameSetup(app)

def onKeyHold(app,keys):
    if(app.gameState == 'main'):
        # SHORTEN ONCE FINISHED
        # check to update the lightmap if any of the keys have been pressed
        if((('d' in keys) or ('a' in keys)) or 
           (('w' in keys) or ('s' in keys))):
            updateLightmap(app,False)
        
        # X movement - keys d and a
        if(('d' in keys) or ('a' in keys)):
            
            # if both d and a are pressed, cancel the thrust
            if(('d' in keys) and ('a' in keys)):
                app.player['x'].currentThrust = 0
                # check altitude
                if(app.ti['ground'].yOffset > app.currentPlayerGroundYOffset):
                    app.player['x'].frictionConstant = (
                        app.player['y'].setFrictionConstant)
                else:
                    app.player['x'].frictionConstant = (
                        app.player['x'].setFrictionConstant)
            
            # if just d is pressed, apply thrust to the right
            elif(('d' in keys) and (not('a' in keys))):
                app.playerFacing = 'right'
                # check for slide condition
                if(app.playerState != 'slide'):
                    app.player['x'].currentThrust = app.player['x'].setThrust 
                    # check altitude
                    if(app.ti['ground'].yOffset > 
                       app.currentPlayerGroundYOffset):
                        app.player['x'].frictionConstant = (
                            app.player['y'].setFrictionConstant)
                    else:
                        app.player['x'].frictionConstant = (
                            app.player['x'].setFrictionConstant)
                else:
                    app.player['x'].currentThrust = (
                        app.player['x'].setThrust/10)
                    app.player['x'].frictionConstant = (
                        app.player['x'].setFrictionConstant/100)
            
            # if just a is pressed, apply thrust to the left
            else:
                app.playerFacing = 'left'
                # check for slide condition
                if(app.playerState != 'slide'):
                    app.player['x'].currentThrust = -app.player['x'].setThrust
                    # check altitude 
                    if(app.ti['ground'].yOffset > 
                       app.currentPlayerGroundYOffset):
                        app.player['x'].frictionConstant = (
                            app.player['y'].setFrictionConstant)
                    else:
                        app.player['x'].frictionConstant = (
                            app.player['x'].setFrictionConstant)
                else:   
                    app.player['x'].currentThrust = -(
                        app.player['x'].setThrust/10)
                    app.player['x'].frictionConstant = (
                        app.player['x'].setFrictionConstant/100)
        
        # Y movement - keys w and s
        if(('w' in keys) or ('s' in keys)):
            
            # if both w and s are pressed, 
            # apply glide thrust at appropriate altitude
            if(('w' in keys) and ('s' in keys)):
                # check altitude
                if(app.ti['ground'].yOffset > app.currentPlayerGroundYOffset):
                    app.player['y'].currentThrust = app.playerGlideThrust
                app.player['y'].frictionConstant = (
                    app.player['y'].setFrictionConstant)
                # register s pressed
                app.sPressed = True
            
            # if just w is pressed
            # apply upwards thrust as long as wing counter allows
            elif(('w' in keys) and (not('s' in keys))):
                # check wing counter
                if(app.playerWingCounter < app.maxPlayerWingCounter):
                    app.player['y'].currentThrust = (
                        app.player['y'].setThrust-
                        int((app.playerWingCounter/
                             (app.maxPlayerWingCounter/10))**3)-app.setGravity)
                    app.playerWingCounter += 50
                # check altitude
                elif(app.ti['ground'].yOffset > app.currentPlayerGroundYOffset):
                    app.player['y'].currentThrust = app.playerGlideThrust
                else: 
                    app.player['y'].currentThrust = 0
                app.player['y'].frictionConstant = (
                    app.player['y'].setFrictionConstant)
            
            # if just s is pressed, apply glide thrust at appropriate altitude
            else:
                # check altitude
                if(app.ti['ground'].yOffset > app.currentPlayerGroundYOffset):
                    app.player['y'].currentThrust = app.playerGlideThrust
                else: 
                    app.player['y'].currentThrust = 0
                app.player['y'].frictionConstant = (
                    app.player['y'].setFrictionConstant)
                # register s key is pressed
                app.sPressed = True
        
        # check for spell scroll activation key
        if('tab' in keys):
            app.displaySpellScroll = True

def onKeyRelease(app,key):
    # force lowercase to avoid any interference from accidentally holding the
    # shift button
    key = key.lower()
    
    if(app.gameState == 'main'):
        # remove x thrust
        if((key == 'a') or (key == 'd')):
            app.player['x'].currentThrust = 0
        # remove y thrust
        if((key == 'w') or (key == 's')):
            app.player['y'].currentThrust = 0
            app.player['y'].frictionConstant = -1
        # update s key press
        if(key == 's'):
            app.sPressed = False
        # update spell scroll display
        if(key == 'tab'):
            app.displaySpellScroll = False

    # setting values that need to be released during game states that prohibit
    # the registration of key presses to 0, otherwise, their values persist
    # even when the keys that need to be held to active them are no longer held
    elif(app.gameState in {'paused', 'tutorial'}):
        app.player['x'].currentThrust = 0
        app.player['y'].currentThrust = 0
        app.player['y'].frictionConstant = -1
        app.sPressed = False
        app.displaySpellScroll = False

def onMousePress(app,mouseX,mouseY,button):
    if(app.gameState == 'main'):

        # debug feature
        if(app.printMouseScreenSector):
            getMouseScreenSector(app,mouseX,mouseY)
            print(app.mouseScreenSector)
        
        # right click to cast aggressive spells
        if((button == 0) and 
           (len(app.spellData['aggressive'].activeSpell) == 1) and 
           app.spellOrbCharged):
            # print('iniating aggressive spell cast')
            app.playerManaRechargeCounter = 0
            initiateSpellCast(app,
                              app.spellData['aggressive'].activeSpell[0].name,
                              mouseX,mouseY)
        
        # left click to cast defensive spells
        elif((button == 2) and 
             (len(app.spellData['defensive'].activeSpell) == 1) and 
             (app.spellData['defensive'].drawingSpell == False) and 
             app.spellOrbCharged):
            # print('iniating defensive spell cast')
            app.playerManaRechargeCounter = 0
            getMouseScreenSector(app,mouseX,mouseY)
            initiateSpellCast(app,
                              app.spellData['defensive'].activeSpell[0].name,
                              mouseX,mouseY)
            
        # if button 2 is pressed and the shield spell has already been cast
        # deactivate shield spell
        elif((button == 2) and 
             (len(app.spellData['defensive'].activeSpell) == 1) and 
             (app.spellData['defensive'].activeSpell[0].name == 'shield') and 
             (not app.spellOrbCharged)):
            app.playerMana = min(
                (app.playerMana + app.spells['shield'].manaCost), 
                app.playerMaxMana)
            app.removeShield = True

    elif(app.gameState == 'menu'):
        # getting play button alignment
        playButtonWidth = int(
            app.gui['menuPlayButton'].imageWidth * 
            app.gui['menuPlayButton'].imageScale)
        playButtonHeight = int(
            app.gui['menuPlayButton'].imageHeight * 
            app.gui['menuPlayButton'].imageScale)
        playButtonLeft = (
            app.gui['menuPlayButton'].xPosition - (playButtonWidth // 2))
        playButtonRight = (
            app.gui['menuPlayButton'].xPosition + (playButtonWidth // 2))
        playButtonTop = (
            app.gui['menuPlayButton'].yPosition - (playButtonHeight // 2))
        playButtonBottom = (
            app.gui['menuPlayButton'].yPosition + (playButtonHeight // 2))
        # checking for play button click
        if((playButtonLeft < mouseX < playButtonRight) and 
           (playButtonTop < mouseY < playButtonBottom)):
            app.gameState = 'startCutscene'
            
def onMouseMove(app,mouseX,mouseY):
    # using mouse positioning to get the side of the spell orb that the mouse 
    # is on
    if(app.gameState == 'main'):
        for spellType in app.spellTypes:
            if(not(app.spellData[spellType].spellCastingEnabler)):
                getMouseOrbSide(app,mouseX)

    # checking for mouseover play button during title screen
    elif(app.gameState == 'menu'):
        playButtonWidth = int(
            app.gui['menuPlayButton'].imageWidth * 
            app.gui['menuPlayButton'].imageScale)
        playButtonHeight = int(
            app.gui['menuPlayButton'].imageHeight * 
            app.gui['menuPlayButton'].imageScale)
        playButtonLeft = (
            app.gui['menuPlayButton'].xPosition - (playButtonWidth // 2))
        playButtonRight = (
            app.gui['menuPlayButton'].xPosition + (playButtonWidth // 2))
        playButtonTop = (
            app.gui['menuPlayButton'].yPosition - (playButtonHeight // 2))
        playButtonBottom = (
            app.gui['menuPlayButton'].yPosition + (playButtonHeight // 2))
        if((playButtonLeft < mouseX < playButtonRight) and 
           (playButtonTop < mouseY < playButtonBottom)):
            app.gui['menuPlayButton'].mouseOver = True
        else:
            app.gui['menuPlayButton'].mouseOver = False

def onStep(app):
    # GUI
    updateGui(app)

    if(app.gameState == 'main'):
        # PLAYER
        updatePlayerImage2(app)
        updatePlayerVelocity(app)
        
        # TILEABLE IMAGES
        for tileableImageName in app.tileableImageList:
            updateTiles(app,tileableImageName)
        
        # LIGHTING
        updateLightmap(app,False)
        updateLightsources(app)
        
        # SPELLS
        for spellType in app.spellTypes:
            if(len(app.spellData[spellType].activeSpell) == 1):
                if(app.spellData[spellType].spellCastingEnabler):
                    for spell in app.spellData[spellType].activeSpell:
                        castSpell(app,spell.name)
            else:
                app.spellData[spellType].spellCastingEnabler = False
        app.castingSpell = (app.spellData['aggressive'].spellCastingEnabler or 
                            app.spellData['defensive'].spellCastingEnabler)
        
        # SPELL ORB
        updateSpellOrb(app)
        
        # PROJECTILES
        updateProjectiles(app)
        
        # ENEMIES
        updateEnemies(app)
        
        # HITBOXES
        if(app.boundingBox != None):
            app.boundingBox.checkPlayerLocation(app)
        for hitboxName in app.hitbox:
            updateHitbox(app,app.hitbox[hitboxName])
        checkCollisions(app)
        
        # PICKUPS
        deletePickups(app)
        
        # PLAYER IMMUNITY FRAMES
        if(app.playerImmunityFrames != 0):
            app.playerImmunityFrames -= 1
        
        # SCREEN SHAKE
        updateScreenShake(app)
    
    # SIMPLE ANIMATIONS
    if(app.gameState in 'main','winCutscene'):
        for i in app.simpleAnimations:
            i.update(app)

def redrawAll(app): 
    if(app.gameState in {'main','paused','dead','winCutscene'}):
        # TILEABLE IMAGES
        for tileableImageName in app.tileableImageList:
            drawTiles(app,tileableImageName)
        
        # OVERLAY
        for overlay in app.overlays:
            app.overlays[overlay].draw(app)
        
        # PICKUPS
        for pickup in app.pickups:
            app.pickups[pickup].draw(app)
        
        # LASERS!!
        if('insidiousCreature' in app.enemies):
            app.enemies['insidiousCreature'].drawLasers()
        
        # PLAYER
        drawPlayer(app)
        
        # SPELL ORB
        drawSpellOrb(app)
        
        # ENEMIES
        drawEnemies(app)
        
        # SIMPLE ANIMATIONS
        for i in app.simpleAnimations:
            i.draw(app)
    
    if(app.gameState == 'main'):
        # SPELLS
        for spellType in app.spellTypes:
            for spell in app.spellData[spellType].activeSpell:
                if(app.spellData[spellType].drawingSpell):
                    drawSpell(app,spell.name)
        
        # PROJECTILES
        for projectile in app.projectile:
            drawProjectile(app,app.projectile[projectile].name)
        
        # HITBOXES
        if(app.displayHitboxes):
            for hitboxName in app.hitbox:
                displayHitbox(app,app.hitbox[hitboxName])

    if(app.gameState in {'main','paused','dead','winCutscene'}):
        # LIGHTING
        drawLightmap(app)
        
        # DEBUG - optional
        if(app.debugFeaturesEnabled):
            displayDebugFeatures(app) 

    # BOUNDING BOX     
    if((app.gameState == 'main') and (app.boundingBox != None)):
        app.boundingBox.draw()
    
    # GUI
    drawGui(app) 

# GAME SETUP
def gameSetup(app):
    # ---- WINDOW SETUP ----
    # establishing screen width
    app.screenWidth = 1000
    app.screenHeight = 750

    # setting the left and right bounds of the screen
    # should be set a little ways beyond the visible edge of the screen
    # to ensure tiles are displayed properly
    app.screenLeft = -255
    app.screenRight = app.screenWidth + 5
    app.screenTop = 0
    app.screenBottom = app.screenHeight

    # setting the background color
    app.background = "blue"

    # ---- TILEABLE IMAGE SETUP ----
    # establishing tileable image class
    class TileableImage:
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
    app.ti['background'] = TileableImage()
    app.ti['midground'] = TileableImage()
    app.ti['ground'] = TileableImage()

    # establishing tiling widths 
    # THESE ARE MANUALLY SET ACCORDING TO THE IMAGES
    app.ti['background'].tileWidth = 250
    app.ti['midground'].tileWidth = 150
    app.ti['ground'].tileWidth = 100

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

     # establishing initial y offsets
    app.ti['background'].initialTileYPosition = -600
    app.ti['midground'].initialTileYPosition = 125
    app.ti['ground'].initialTileYPosition = 406

    # split images into tiles and save the tiles as seperate images
    app.tileableImageList = ['background','midground','ground']
    for tileableImageName in app.tileableImageList:
        tileImage(app,app.ti[tileableImageName].image,
                  app.ti[tileableImageName].tileWidth,
                  tileableImageName)

    # establishign the platform images using a loop, since it's more efficient
    # that way
    app.numberOfPlatforms = 3
    app.platformInitialYPoition = 50
    platformY = app.platformInitialYPoition
    platformHeight = 498
    for i in range(app.numberOfPlatforms):
        platform = (f'platform_{i+1}')
        app.ti[platform] = TileableImage()
        app.ti[platform].tileWidth = 250
        app.ti[platform].image = (f'images/{platform}/{platform}.png')
        app.ti[platform].parallaxCoefficient = 1
        app.ti[platform].opacity = 100
        tileImage(
            app,app.ti[platform].image,app.ti[platform].tileWidth,platform)
        app.tileableImageList.insert(-1,platform)
        app.ti[platform].initialTileYPosition = platformY
        platformY -= platformHeight

    # ---- PHYSICS SETUP ----
    # initiating the physics class
    class Physics:
        def __init__(self):
            self.mass = 0
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

    # ---- HITBOX SETUP ----
    # initializing hitbox dictionary
    app.hitbox = dict()

    # ---- PLAYER SETUP ----
    # initiating player object
    class PlayerObject:
        def __init__(self):
            self.displayWidth = 0
            self.displayHeight = 0
            self.xPosition = 0
            self.yPosition = 0
            self.xOffset = 0
            self.yOffset = 0
            self.centerX = 0
            self.centerY = 0
            self.headX = 0
            self.headY = 0

    app.playerObject = PlayerObject

    # initializing player image and positioning data
    app.playerScale = 0.15
    # width of actual player sprite image - same for wings
    playerSpriteWidth = 500
    # height of actual player sprite image - same for wings
    playerSpriteHeight = 500
    app.playerWingWidth = int(playerSpriteWidth*app.playerScale)
    app.playerWingHeight = int(playerSpriteHeight*app.playerScale)

    app.playerObject.displayWidth = int(playerSpriteWidth*app.playerScale)
    app.playerObject.displayHeight = int(playerSpriteHeight*app.playerScale)
    app.playerObject.xPosition = int(
        (app.screenWidth-app.playerObject.displayWidth)/2)
    app.playerObject.yPosition = int(
        (app.screenHeight-app.playerObject.displayHeight)/2)
    app.playerObject.centerX = (
        app.playerObject.xPosition + (app.playerObject.displayWidth // 2))
    app.playerObject.centerY = (
        app.playerObject.yPosition + (app.playerObject.displayHeight // 2))
    app.playerObject.headX = app.screenWidth//2
    app.playerObject.headY = (
        app.playerObject.yPosition + int(app.playerObject.displayHeight/10))

    # sets first player image to show
    app.playerImageIndex = [0,0,-1]

    # sets first player wing image to show, and establishing X and Y offsets
    app.playerWingImageIndex = [0,0,-1]
    app.playerWingXOffset = 0
    app.playerWingYOffset = 0

    # intiates player physics dictionary
    app.player = dict()

    # intiating player physics axes
    app.player['x'] = Physics()
    app.player['y'] = Physics()

    # the following parameters are tuned by feel, and cannot be determined
    # mathematically
    app.player['x'].mass = 30
    app.player['y'].mass = 30
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

    # initiaizling player health and mana
    app.playerHealth = 100
    app.playerMaxHealth = 100
    app.playerMana = 100
    app.playerMaxMana = 100
    app.playerManaRechargeSpeed = 5
    app.playerManaRechargeCounter = 0

    # intializing player physics hitbox
    playerHitboxXAdjustmentConstant = playerSpriteWidth//25
    left = app.playerObject.xPosition + playerHitboxXAdjustmentConstant
    right = (app.playerObject.xPosition + 
             app.playerObject.displayWidth - 
             playerHitboxXAdjustmentConstant)
    top = app.playerObject.yPosition
    bottom = app.playerObject.yPosition + app.playerObject.displayHeight
    app.hitbox['player'] = HitboxRect(left,right,top,bottom)
    app.hitbox['player'].associatedObject = app.playerObject
    app.hitbox['player'].belongsTo = 'player'

    # initializing player inmmunity frame counter
    app.playerImmunityFrames = 0

    # initializing player ground y coordinate list
    app.playerGroundYOffsets = [0]
    for i in range(app.numberOfPlatforms):
        platform = (f'platform_{i+1}')
        app.playerGroundYOffsets.append(app.ti['ground'].initialTileYPosition - 
                                        app.ti[platform].initialTileYPosition)

    # # adding an arbitrary very large value to the end
    # app.playerGroundYOffsets.append(3000)

    # print(app.playerGroundYOffsets)

    # setting up current player ground Y coordinate indicator
    app.currentPlayerGroundYOffset = 0

    # adding a specific parameter to tell if the s key is pressed, and 
    # if so use the next applicable ground Y coordinate
    app.sPressed = False
    
    # ---- SPELL ORB SETUP ----
    # establshing charged state of spell orb
    app.spellOrbCharged = False

    # initializing spell orb offset and position variables
    app.spellOrbXPosition = 0
    app.spellOrbYPosition = 0
    app.spellOrbXOffset = 0
    app.spellOrbYOffset = 0
    app.spellOrbInitialX = (app.screenWidth // 2)
    app.spellOrbInitialY = app.playerObject.yPosition - 25

    # setting up spell orb rotation
    app.spellOrbRotationAngle = 0
    app.spellOrbRotationSpeed = 1

    # spell orb drift constant, controls how far away the orb drifts from the 
    # player when they are moving - larger = farther drift
    app.spellOrbDriftConstant = 5

    # spell orb damping constant, controls how much the player's velocity 
    # affects the orb, higher is less effect
    app.spellOrbDampingCoefficient = 5

    # setting up image paramanetrs for spell orb
    app.spellOrbImageSize = 500 # 500 x 500 pixel square
    app.spellOrbScalingFactor = 0.04

    # ---- SPELL CASTING SETUP ---
    # initializing spell class
    # DEFINED GLOBALLY 

    # initializing spell dictionary
    app.spells = dict()

    class SpellData:
        def __init__(self):
            # setting up the list of currently active spells
            # list should only ever contain currently active spell or no spells
            self.activeSpell = []
            # establishing the spell drawing enabler
            self.drawingSpell = False
            # establishing the spell casting enabler
            self.spellCastingEnabler = False
            # setting up path to display image
            app.spellImagePath = ''

    # initiating list of aviablable spell types
    app.spellTypes = {'aggressive','defensive'}

    # initiating spellData dictionary
    app.spellData = dict()

    # initiating instances of the spellData class 
    # for active and defensive spells
    for spellType in app.spellTypes:
        app.spellData[spellType] = SpellData()

    # establishing usable spells
    app.spells['testLightSpell'] = Spell(
        'aggressive','rfv','testLightSpell','endEffect',9,500,250,1,0,50)
    
    # app.spells['testBall'] = Spell(
    #     'aggressive','rtf','testBall','playerProjectile',2,250,250,0.25,0,10)
    # app.spells['testBall'].projectileType = 'pointHoming'
    # app.spells['testBall'].directional = True
    
    app.spells['levelOneSlimeBall'] = Spell('aggressive','grtf',
                                            'levelOneSlimeBall',
                                            'mapProjectile',1,250,250,0.1,5,10)
    app.spells['levelOneSlimeBall'].projectileType = 'groundbounce'
    
    app.spells['shield'] = Spell(
        'defensive','zr','shield','shield',1,250,250,0.3,15,0)
    
    app.spells['ghostSword'] = Spell(
        'aggressive','1g43t','ghostSword','mapProjectile',1,250,250,0.5,15,10)
    app.spells['ghostSword'].projectileType = 'linear'
    
    app.spells['skySplitter'] = Spell(
        'aggressive','ztqv14gr23','skySplitter','endEffect',10,500,200,1,0,50)
    
    # establishing signifier that tells which side of the screen the mouse is on
    app.mouseOrbSide = 'right'

    # initiating combo in progress tracker
    app.comboInProgress = ''

    # setting up spell cancel combo
    # NO OTHER COMBO SHOULD START WITH THE SAME LETTER AS THE CANCEL COMBO
    # this allows combo detection to work properly
    app.cancelCombo = 'ff'

    # establishing general spell casting tracker
    app.castingSpell = False

    # setting up dictionary of shield positions depending on its alignment
    # positions are stored as tuples in the form (x,y), and are determined
    # using trigonometry
    potentialAlignments = ['ssRight',
                           'ssUpRight',
                           'ssUp',
                           'ssUpLeft',
                           'ssLeft',
                           'ssDown'
                           ]
    app.shieldData = dict()
    
    # preparing for calculations:
    # setting up shield offset from player
    shieldOffset = 50
    # setting up list of shield angles that correspond with order of alignments
    shieldAngleList = [0, -45, -90, -135, 180, 90]
    for i in range(len(shieldAngleList)):
        shieldAngle = shieldAngleList[i]
        alignment = potentialAlignments[i]

        shieldX = (app.playerObject.centerX + 
                   shieldOffset * math.cos(math.radians(shieldAngle)))
        shieldY = (app.playerObject.centerY + 
                   shieldOffset * math.sin(math.radians(shieldAngle)))
        
        app.shieldData[alignment] = (shieldX,shieldY,shieldAngle)

    # setting up shield removing indicator
    app.removeShield = False

    # ---- PROJECTILE SETUP ----
    # PROJECTILE CLASSES ARE ESTABLISHED GLOBALLY  

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
    app.backgroundBrightness = 200

    # ---- GUI SETUP ----
    class GuiElement:
        def __init__(self,imagePath,xPosition,yPosition,imageWidth,
                     imageHeight,imageScale,displayAngle,opacity,alignment):
            self.imagePath = imagePath
            self.xPosition = xPosition
            self.yPosition = yPosition
            self.imageWidth = imageWidth
            self.imageHeight = imageHeight
            self.imageScale = imageScale
            self.imageScale_2 = imageScale
            self.displayAngle = displayAngle
            self.opacity = opacity
            self.alignment = alignment
            self.mouseOver = False
    
    # initializing gui dictionary
    app.gui = dict()

    # establishing gui elements as instances of the guiElement class within 
    # the gui dictionary
    app.gui['wizardDRO'] = GuiElement(
        'images/GUI/wizardDRO.png',app.screenWidth-150,0,500,500,0.25,0,100,
        'left-top')
    
    app.gui['wizardDROGrille'] = GuiElement(
        'images/GUI/wizardDROGrille.png',app.screenWidth-150,0,500,500,0.25,0,
        100,'left-top')
    
    app.gui['titleScreen'] = GuiElement(
        'images/GUI/titleScreen.png',0,0,1000,750,1,0,100,'left-top')
    
    app.gui['menuPlayButton'] = GuiElement(
        'images/GUI/menuPlayButtonOff.png',(app.screenWidth//2),
        int(app.screenHeight*0.875),500,500,0.25,0,100,'center')
    
    app.gui['deathText'] = GuiElement(
        'images/GUI/deathText.png',(app.screenWidth//2),
        (app.screenHeight//2),500,500,1,0,100,'center')
    
    app.gui['bossBar'] = GuiElement(
        'images/GUI/bossBar.png',(app.screenWidth//2),
        int(app.screenHeight*0.875),500,500,0.75,0,100,'center')
    
    app.gui['bossBarBackground'] = GuiElement(
        'images/GUI/bossBarBackground.png',(app.screenWidth//2),
        int(app.screenHeight*0.875),500,500,app.gui['bossBar'].imageScale,
        0,100,'center')
    
    app.gui['theHideousBeastTitle'] = GuiElement(
        'images/GUI/theHideousBeastTitle.png',(app.screenWidth//2),
        int(app.screenHeight*0.875),500,500,app.gui['bossBar'].imageScale,
        0,100,'center')
    
    app.gui['insidiousCreatureTitle'] = GuiElement(
        'images/GUI/insidiousCreatureTitle.png',(app.screenWidth//2),
        int(app.screenHeight*0.875),500,500,app.gui['bossBar'].imageScale,
        0,100,'center')
    
    app.spellScrollBottomYPosition = (app.screenHeight-5)
    app.spellScrollTopYPosition = int(app.screenHeight*0.0625) 
    app.gui['spellScroll'] = GuiElement(
        'images/GUI/spellScroll.png',app.screenWidth,
        app.spellScrollBottomYPosition,500,1000,0.75,0,100,'top-right')
    
    app.gui['pauseText'] = GuiElement(
        'images/GUI/pauseText.png',(app.screenWidth//2),
        (app.screenHeight//2),500,500,1,0,100,'center')
    
    app.gui['tutorial'] = GuiElement(
        'images/GUI/tutorial.png',(app.screenWidth//2),
        (app.screenHeight//2),1000,750,1,0,100,'center')
    
    app.gui['license'] = GuiElement(
        'images/GUI/license.png',(app.screenWidth//2),
        (app.screenHeight//2),1000,750,0.1,0,100,'center')
    
    app.gui['winScreen'] = GuiElement(
        'images/GUI/winScreen.png',(app.screenWidth//2),
        (app.screenHeight//2),1000,750,1,0,100,'center')

    # setting opacities for certain gui elements
    app.startCutsceneOverlayOpacity = 0
    app.deathCutsceneOverlayOpacity = 0
    app.pauseScreenOpacity = 50
    app.edgeDarknessOpacity = 0

    # establishing counter for spell scroll
    app.spellScrollCounter = 0
    
    # establishing display indicator for spell scroll
    app.displaySpellScroll = False

    # establishing speed factors for scroll opening and closing
    app.scrollOpenSpeed = 0.65 # 0 > x > 1
    app.scrollCloseSpeed = 1.5 # 1 > x > 2

    # establishing constant for how much the scroll should shake while held
    app.scrollShakeMagnitude = 2

    # setting up seperate display combo for combo indicator
    app.displayCombo = ''
    
    # establishing origin coordinates for combo indicator
    app.comboImageTop = 10
    app.comboImageLeft = 10

    # establishing size and scale of the combo images to be displayed
    app.comboImageSize = 100
    app.comboDetailTextWidth = 500
    app.comboImageScale = 0.5

    # setting spacing between combo images
    app.comboImageSpacing = int(app.comboImageSize * app.comboImageScale * 0.7)

    # setting up combo counter
    app.comboCounter = 0

    # setting up shake parameter for combo indicator
    app.comboShake = 0

    # setting up total x offset for edge fade effect
    app.totalXOffset = 0

    # setting up bounds for edge fade effect
    app.edgeFadeBounds = 100000
    
    # setting up rate of fade for edge fade bounds
    app.edgeFadeRate = 0.05

    app.edgeFadeDeathTimer = 0

    # setting up timer and data for win cutscene
    app.winTimer = 0

    app.winCutsceneOverlayOpacity = 1

    # setting up license spin speed
    app.lisenceRotationSpeed = 100

    # setting up restart prompt opacity
    app.restartPromptMaxOpacity = 30
    app.restartPromptOpacity = 0

    # ---- SCREEN SECTOR SETUP ----
    # six screen sectors, ssDown, ssLeft, ssRight, ssUpLeft, ssUpRight, ssUp

    # establishing the angles associated with each of the screen sectors
    # the angles are attributed according to a counterclockwise rotation
    # such that each sector can be described as the area covered by a line
    # swept counterclockwise, starting at the first angle and ending at the
    # second angle. 

    # this angular definition system was suggested by Professor Mike Taylor

    # the angles, along with the apropriate names for the sectors, are stored
    # in a dictionary
    app.sectorAngles = dict()

    # map of relative angle locations
    #               ssUp
    #      ssUpLeft      ssUpRight
    # ssLeft                    ssRight  - this is where 0 degrees is
    #               ssDown
    #      this is where 90 degrees is

    # setting angles (in degrees)
    # the reason I am referencing a bunch of the other angles already set
    # is so that you only have to change as few values as possible to 
    # influence the overall divisions of the screen sectors
    # the only values you have to change are the two in ssRight and the last one
    # in ssUpRight. All the other values are either mirrored, or can be 
    # found through subtraction, so I wrote the code to autofill them
    # all values should be justified such that they are within 0 - 360
    app.sectorAngles['ssRight'] = [40,340]
    app.sectorAngles['ssUpRight'] = [app.sectorAngles['ssRight'][1],300]
    app.sectorAngles['ssUp'] = [
        app.sectorAngles['ssUpRight'][1],
        (360 + 180 - app.sectorAngles['ssUpRight'][1])]
    app.sectorAngles['ssUpLeft'] = [
        app.sectorAngles['ssUp'][1],
        (360 + 180 - app.sectorAngles['ssUpRight'][0])]
    app.sectorAngles['ssLeft'] = [
        (360 + 180 - app.sectorAngles['ssRight'][1]),(
            180 - app.sectorAngles['ssRight'][0])]
    app.sectorAngles['ssDown'] = [(
        180 - app.sectorAngles['ssRight'][0]),
        app.sectorAngles['ssRight'][0]]
    
    # indicate angles
    # for sector in app.sectorAngles:
        # ptc('sector',sector)
        # ptc('angles',app.sectorAngles[sector])
    
    # setting up screen sector indicator
    app.mouseScreenSector = 'ssRight'

    # ---- SCREEN SHAKE SETUP ----
    # dictates the magnitude of the screen shake currently applied
    app.screenShakeMagnitude = 0
    
    # indicates the x and y offsets of the screen shake
    app.screenShakeX = 0
    app.screenShakeY = 0

    # counter and speed for screen shake effect
    app.screenShakeCounter = 0
    app.screenShakeDissapationSpeed = 5
    
    # ---- ENEMY SETUP ----
    # initializing enemies dictionary
    app.enemies = dict()
    
    # initializing test boss, The Hideous Beast
    # initiateTheHideousBeast(app,Physics)

    # initializing the final boss, Insidious Creature
    initiateInsidiousCreature(app,Physics)
      
    # ---- BOUNDING BOX SETUP ---
    # establishing bounding box existence variable
    app.boundingBox = None

    # ---- GAME STATE SETUP ----
    # initializing game state
    # current available game states are:
    # - 'menu'
    # - 'startCutscene'
    # - 'main'
    # - 'dead'
    # - 'paused'
    # - 'fadeCutscene'
    # - 'tutorial
    # - 'winCutscene'
    # - 'win'
    # the game starts in the menu state
    app.gameState = 'menu'

    app.currentBoss = None 
    
    # ---- SIMPLE ANIMATION SETUP ----
    # setting up simple animations list
    app.simpleAnimations = []

    # ---- OVERLAY SETUP ----
    # initiating overlay dictionary
    app.overlays = dict()

    # initiating overlay that goes below the insidious creature
    floorBloodX = app.enemies['insidiousCreature'].xPosition + 20
    floorBloodY = app.ti['ground'].initialTileYPosition
    app.overlays['floorBlood'] = Overlay(
        'images/insidiousCreature/floorBlood.png',
        1000,125,1.25,0,floorBloodX,floorBloodY,0,0,60,'top')

    # ---- PICKUP SETUP ----
    # initialzing pickups dictionary 
    app.pickups = dict()

    # ---- APP SETUP ----
    # setting the framerate
    app.stepsPerSecond = 60
    
    # ---- DEBUG SETUP ----
    # misc testing setup
    # app.testWalkSpeed = 10
    # app.screenLeft = 100
    # app.screenRight = app.screenWidth - 100

    app.debugFeatureDisplayText = []

    app.debugFeaturesEnabled = False

    app.displayReadout = False

    app.displayHitboxes = False

    app.hitboxCounter = 0

    app.displayScreenZones = False

    app.transparencyTest = False

    app.displayShieldPositions = False

    app.printMouseScreenSector = False

    # ---- FINALIZATION ----
    # calling several of the update functions, to ensure everything is
    # set up prior to the first draw call
    updatePlayerImage2(app)
    for tileableImageName in app.tileableImageList:
        updateTiles(app, tileableImageName)
    updatePlayerVelocity(app)
    lightmapSetup(app)
    app.lightSources.append(LightSource(1,0,0,0,0.9))
    updateLightmap(app,False)
    updateSpellOrb(app)
    setupCombos(app)
    updateEnemies(app)

def appSetup(app):
    gameSetup(app)

# MAIN()
def main():
    appSetup(app)
    runApp(width = app.screenWidth, height = app.screenHeight)

main()

# total hours spent working here: ~130