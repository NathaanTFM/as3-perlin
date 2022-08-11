import ctypes
import os
import itertools
import queue
import threading
import multiprocessing
import time

from perlinNoise import initPerlinNoise, generatePerlinNoise, freePerlinNoise, perlinVector2
from PIL import Image
    
def saveMismatch(state, seed, bmpWidth, bmpHeight, flashIm):
    im = Image.new("RGBA", (bmpWidth*2, bmpHeight))
    im.paste(flashIm, (0, 0))
    
    pix = im.load()
    for x, y in itertools.product(range(bmpWidth), range(bmpHeight)):
        color = colors[y * bmpWidth + x]
        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        alpha = color >> 24
        
        pix[bmpWidth+x, y] = (red, green, blue, alpha)
        
    im.save("cperlin-" + str(seed) + ".png")

def testSeed(seed):
    def random():
        nonlocal seed
        seed = (-2836 * (seed // 127773) + 16807 * (seed % 127773)) & 0xFFFFFFFF
        return seed / 4294967296
    
    path = os.path.join(root, "perlin-" + str(seed) + ".png")
    
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
    
    im = Image.open(path)
    pix = im.load()
    
    colors = (ctypes.c_uint32 * (bmpWidth * bmpHeight))()
    generatePerlinNoise(state, bmpWidth, bmpHeight, ctypes.byref(colors))
    
    for x, y in itertools.product(range(bmpWidth), range(bmpHeight)):
        color = colors[y * bmpWidth + x]
        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        alpha = color >> 24
        
        if pix[x, y] != (red, green, blue, alpha):
            print("Mismatch! Pixel %d, %d, got %r - expected %r" % (x, y, (red, green, blue, alpha), pix[x, y]))
            saveMismatch(state, seed, bmpWidth, bmpHeight, im)
            break
        
    freePerlinNoise(state)
    

def threadfunc(seedList):
    while True:
        try:
            seed = seedList.get(block=False)
        except queue.Empty:
            break
            
        testSeed(seed)
        
root = os.path.join(os.environ["AppData"], "perlinTest", "Local Store", "generated")

if __name__ == "__main__":
    seedList = multiprocessing.Queue()

    for file in os.listdir(root):
        if not (file.startswith("perlin-") and file.endswith(".png")):
            continue
            
        seedList.put(int(file[7:-4]))
        
    origLength = seedList.qsize()

    for n in range(2):
        proc = multiprocessing.Process(target=threadfunc, args=(seedList,))
        proc.start()
        
    try:
        while True:
            print(str(origLength - seedList.qsize()) + "/" + str(origLength))
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("STOP")
        while True:
            try:
                seed = seedList.get(block=False)
            except queue.Empty:
                break