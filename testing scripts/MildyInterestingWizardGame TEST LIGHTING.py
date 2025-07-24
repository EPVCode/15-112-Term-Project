import numpy
from PIL import Image

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

# contains truples with x,y,and intensity of light source
lightSources = []
lightSources.append(lightSource(10,10,25,25,0,0.95))
lightSources.append(lightSource(10,10,45,25,0,0.95))
imageWidth = 100
imageHeight = 150
# tune value (radius)
lightmapMatrixX = imageWidth
lightmapMatrixY = imageHeight
lightmapMatrix = numpy.array([[255,255] * lightmapMatrixX]*lightmapMatrixY, dtype=numpy.uint8)
def calculateGaussian(x,y,lightSources):
    lightsourceMaxIntensity = 255
    opacity = 255
    for lightSource in lightSources:
        opacity -= int((lightsourceMaxIntensity)*((lightSource.intensity)**((-1*(((x-lightSource.x)**2)/(2*((lightSource.spread)**2))))-(((y-lightSource.y )**2)/(2*((lightSource.spread)**2))))))
    return [255,max(opacity,0)]

for y in range(lightmapMatrixY):
    for x in range(lightmapMatrixX):
        lightmapMatrix[y,x] = calculateGaussian(x,y,lightSources)


lightmap = Image.fromarray(lightmapMatrix, mode = "LA")
lightmap.show()