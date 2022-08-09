import sys
import os
import itertools

from perlinNoise import initPerlinNoise, generatePerlinNoise, freePerlinNoise, perlinVector2
from PIL import Image

def random():
    global _seed
    _seed = (-2836 * (_seed // 127773) + 16807 * (_seed % 127773)) & 0xFFFFFFFF
    return _seed / 4294967296
    
def saveMismatch(state, seed, bmpWidth, bmpHeight, flashIm):
    im = Image.new("RGBA", (bmpWidth*2, bmpHeight))
    im.paste(flashIm, (0, 0))
    
    pix = im.load()
    for x, y in itertools.product(range(bmpWidth), range(bmpHeight)):
        color = generatePerlinNoise(state, x, y)
        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        alpha = color >> 24
        
        pix[bmpWidth+x, y] = (red, green, blue, alpha)
        
    im.save("cperlin-" + str(seed) + ".png")
    
path = os.path.join(os.environ["AppData"], "perlinTest", "Local Store", "generated")

seedList = []

for file in os.listdir(path):
    if not (file.startswith("perlin-") and file.endswith(".png")):
        continue
        
    seedList.append(int(file[7:-4]))
    
for idx, seed in enumerate(seedList):
    _seed = seed
    
    bmpWidth = int(100 + random() * 100)
    bmpHeight = int(100 + random() * 100)
    baseX = random() * 400
    baseY = random() * 400
    numOctaves = int(random() * 32)
    
    if random() < 0.5:
        randomSeed = int(random() * -0x80000000 - 1)
    else:
        randomSeed = int(random() * 0x80000000)
    
    stitch = random() >= 0.5
    fractalNoise = random() >= 0.5
    channelOptions = int(random() * 16)
    grayScale = random() >= 0.75
    offsets = (perlinVector2 * numOctaves)()
    
    for i in range(numOctaves):
        x, y = random() * 200 - 100, random() * 200 - 100
        offsets[i] = perlinVector2(x, y)
    
    state = initPerlinNoise(bmpWidth, bmpHeight, baseX, baseY, numOctaves, randomSeed, stitch, fractalNoise, channelOptions, grayScale, offsets)
    
    im = Image.open(os.path.join(path, "perlin-" + str(seed) + ".png"))
    pix = im.load()
    
    for x, y in itertools.product(range(bmpWidth), range(bmpHeight)):
        color = generatePerlinNoise(state, x, y)
        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        alpha = color >> 24
        
        if pix[x, y] != (red, green, blue, alpha):
            print("Mismatch! Pixel %d, %d, got %r - expected %r" % (x, y, (red, green, blue, alpha), pix[x, y]))
            saveMismatch(state, seed, bmpWidth, bmpHeight, im)
            break
    else:
        print(str(idx) + "/" + str(len(seedList)), end="   \r")
        
    freePerlinNoise(state)