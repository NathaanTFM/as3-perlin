import math
from PIL import Image

def unmultiplyColor(color):
    if (color[3] != 255):
        val = 0xFF00 // color[3] if color[3] else 0
        
        red = ((val * (color[0] & 0xFF) + 0x7F) >> 8)
        green = ((val * (color[1] & 0xFF) + 0x7F) >> 8)
        blue = ((val * (color[2] & 0xFF) + 0x7F) >> 8)
        return (red, green, blue, color[3])
        
    return color
    
    
def generateRandomArrays(randomSeed):
    doubleArrays = [
        [0] * 512
        for _ in range(4)
    ]

    if randomSeed <= 0:
        randomSeed = abs(randomSeed) + 1
        
    elif randomSeed == 0x7FFFFFFF:
        randomSeed = 0x7FFFFFFE
        
    for doubleArray in doubleArrays:
        for v19 in range(0, 512, 2):
            for j in range(2):
                randomSeed = -2836 * (randomSeed // 127773) + 16807 * (randomSeed % 127773)
                
                if randomSeed <= 0:
                    randomSeed += 0x7FFFFFFF
                    
                doubleArray[v19 + j] = (randomSeed % 512 - 256) / 256
                
            v22 = math.sqrt(doubleArray[v19] ** 2 + doubleArray[v19+1] ** 2) # !! Idk what happens if it reaches 0
            doubleArray[v19] = doubleArray[v19] / v22 if v22 else 0
            doubleArray[v19 + 1] = doubleArray[v19+1] / v22 if v22 else 0
    
    
    intArray = list(range(256))
    for v25 in reversed(range(1, 256)):
        randomSeed = -2836 * (randomSeed // 127773) + 16807 * (randomSeed % 127773)
        if randomSeed <= 0:
            randomSeed += 0x7FFFFFFF
        
        intArray[v25], intArray[randomSeed % 256] = intArray[randomSeed % 256], intArray[v25]
    
    return intArray, doubleArrays
    


def interpolate(a0, a1, w):
    return (a1 - a0) * (3.0 - w * 2.0) * w * w + a0
    

def perlinNoise(width, height, baseX, baseY, numOctaves, randomSeed, stitch, fractalNoise, channelOptions, grayScale):
    offsetsX = [0] * numOctaves
    offsetsY = [0] * numOctaves
    
    intArray, doubleArrays = generateRandomArrays(randomSeed)

    # okay let's start doing it
    baseX = 1 / abs(baseX) if baseX else 0
    baseY = 1 / abs(baseY) if baseY else 0

    lrint = round # might be int?
    
    im = Image.new("RGBA", (width, height))
    pix = im.load()

    if stitch:
        if baseX:
            tmp1 = math.floor(baseX * width) / width
            tmp2 = math.ceil(baseX * width) / width
            
            if not tmp1 or baseX / tmp1 >= tmp2 / baseX:
                baseX = tmp2
            else:
                baseX = tmp1
                
        if baseY:
            tmp1 = math.floor(baseY * height) / height
            tmp2 = math.ceil(baseY * height) / height
            
            if not tmp1 or baseY / tmp1 >= tmp2 / baseY:
                baseY = tmp2
            else:
                baseY = tmp1
        
        tmp1 = lrint(width * baseX)
        tmp2 = lrint(height * baseY)
        v35_orig = [
            tmp1, tmp2
        ]
        
    if grayScale:
        nbRgbChannels = 1
        
    else:
        nbRgbChannels = ((channelOptions >> 1) & 1) + (channelOptions & 1) + ((channelOptions >> 2) & 1)
        
    hasNoAlpha = (channelOptions & 8) == 0
    hasNoAlpha = hasNoAlpha # False if has no alpha channel
    # might be only if has alpha channel on image
    nbRgbChannels += (channelOptions >> 3) & 1

    res_octave = [0, 0, 0, 0]
    
    for y in range(height):
        for x in range(width):
            res = [0, 0, 0, 0]
            important = 255
            
            baseX_2 = baseX
            baseY_2 = baseY
            
            # default values
            red, green, blue, alpha = 0, 0, 0, 255
            
            if stitch:
                v35 = v35_orig[:]
            
            for octave in range(numOctaves):
                offsetX = (x + offsetsX[octave]) * baseX_2 + 4096.0
                offsetY = (y + offsetsY[octave]) * baseY_2 + 4096.0
                
                # checked; should be OK
                v47 = lrint(offsetX - 0.5)
                v46 = v47 + 1
                
                v44 = lrint(offsetY - 0.5)
                v43 = v44 + 1
                
                v100 = offsetX - v47
                v45 = v100 - 1.0
                
                v48 = offsetY - v44
                v49 = v48 - 1.0
                
                if stitch:
                    tmp1 = v35[0] + 4096
                    tmp2 = v35[1] + 4096
                    
                    if v47 >= tmp1:
                        v47 -= v35[0]
                        
                    if v46 >= tmp1:
                        v46 -= v35[0]
                        
                    if v44 >= tmp2:
                        v44 -= v35[1]
                        
                    if v43 >= tmp2:
                        v43 -= v35[1]
                    
                idx1 = intArray[v47 & 255]
                idx2 = intArray[v46 & 255]
                
                v58 = 2 * intArray[((v44 & 255) + idx1) & 255]
                v59 = 2 * intArray[((v44 & 255) + idx2) & 255]
                v60 = 2 * intArray[((v43 & 255) + idx1) & 255]
                v61 = 2 * intArray[((v43 & 255) + idx2) & 255]
                
                for channel in range(nbRgbChannels):
                    doubleArray = doubleArrays[channel]
                    
                    v66 = doubleArray[v58] * v100 + doubleArray[v58 + 1] * v48
                    v67 = doubleArray[v59] * v45 + doubleArray[v59 + 1] * v48
                    v68 = doubleArray[v60] * v100 + doubleArray[v60 + 1] * v49
                    tmp3 = doubleArray[v61] * v45 + doubleArray[v61 + 1] * v49
                    
                    tmp4 = interpolate(v66, v67, v100)
                    tmp5 = interpolate(v68, tmp3, v100)
                    res_octave[channel] = interpolate(tmp4, tmp5, v48)
                
                if fractalNoise:
                    for channel in range(nbRgbChannels):
                        res[channel] += res_octave[channel] * important
                else:
                    for channel in range(nbRgbChannels):
                        res[channel] += abs(res_octave[channel]) * important
                        
                important *= 0.5
                baseX_2 *= 2
                baseY_2 *= 2
                if stitch:
                    v35[0] *= 2
                    v35[1] *= 2
                
            if grayScale:
                red = green = blue = (lrint(res[0] + 255.0) >> 1) if fractalNoise else lrint(res[0])
                nextChannel = 1
            
            else:
                nextChannel = 0
                if channelOptions & 1:
                    red = (lrint(res[nextChannel] + 255.0) >> 1) if fractalNoise else lrint(res[nextChannel])
                    nextChannel += 1
                    
                if channelOptions & 2:
                    green = (lrint(res[nextChannel] + 255.0) >> 1) if fractalNoise else lrint(res[nextChannel])
                    nextChannel += 1
                    
                if channelOptions & 4:
                    blue = (lrint(res[nextChannel] + 255.0) >> 1) if fractalNoise else lrint(res[nextChannel])
                    nextChannel += 1
                    
            if channelOptions & 8:
                alpha = (lrint(res[nextChannel] + 255.0) >> 1) if fractalNoise else lrint(res[nextChannel])
            
            alpha = min(max(alpha, 0), 255)
            red = min(max(red, 0), alpha)
            green = min(max(green, 0), alpha)
            blue = min(max(blue, 0), alpha)
            
            color = unmultiplyColor((red, green, blue, alpha))
            pix[x, y] = color
            
    return im

