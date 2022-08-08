#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <fenv.h>
#include "perlinNoise.h"

#define max(a,b)             \
({                           \
    __typeof__ (a) _a = (a); \
    __typeof__ (b) _b = (b); \
    _a > _b ? _a : _b;       \
})

#define min(a,b)             \
({                           \
    __typeof__ (a) _a = (a); \
    __typeof__ (b) _b = (b); \
    _a < _b ? _a : _b;       \
})

typedef struct {
    double x;
    double y;
} vector2;

struct _perlinNoiseState {
    //uint32_t width;
    //uint32_t height;
    
    double baseX;
    double baseY;
    
    uint32_t numOctaves;
    
    uint8_t* permutations;
    vector2* vectors;
    
    bool stitch;
    uint32_t stitchArr[2];
    
    bool fractalNoise;
    
    uint8_t channelOptions;
    uint8_t channelCount;
    bool grayScale;
    
    double* offsetsX;
    double* offsetsY;  
};

static inline double interpolate(double a0, double a1, double w) {
    return (a1 - a0) * (3.0 - w * 2.0) * w * w + a0;
}

static inline uint32_t unmultiplyColor(uint32_t color) {
    uint8_t alpha = (color >> 24);
    if (alpha == 255) {
        return color;
    }
    
    uint16_t val = alpha ? 0xFF00 / alpha : 0;
    uint8_t red = (val * ((color >> 16) & 0xFF) + 0x7F) >> 8;
    uint8_t green = (val * ((color >> 8) & 0xFF) + 0x7F) >> 8;
    uint8_t blue = (val * (color & 0xFF) + 0x7F) >> 8;
    
    return (alpha << 24) | (red << 16) | (green << 8) | blue;
}

static inline int32_t getNextRandomValue(int32_t randomSeed) {
    randomSeed = -2836 * (randomSeed / 127773) + 16807 * (randomSeed % 127773);
    if (randomSeed <= 0) {
        randomSeed += 0x7FFFFFFF; // what if it's equals to -0x80000000?? 
    }
    
    return randomSeed;
};

static void generateRandom(int32_t randomSeed, uint8_t** permutations, vector2** vectors) {
    *permutations = malloc(256);
    *vectors = malloc(sizeof(vector2) * 256 * 4);
    
    if (randomSeed <= 0) {
        randomSeed = abs(randomSeed - 1);
    }
    else if (randomSeed == 0x7FFFFFFF) {
        --randomSeed;
    }
    
    for (int i = 0; i < 4; ++i) {
        vector2* vectorArray = &(*vectors)[i * 256];
        
        for (int j = 0; j < 256; ++j) {
            vector2* vector = &vectorArray[j];
            
            randomSeed = getNextRandomValue(randomSeed);
            vector->x = (randomSeed % 512 - 256) / 256.0;
            
            randomSeed = getNextRandomValue(randomSeed);
            vector->y = (randomSeed % 512 - 256) / 256.0;
            
            double dist = sqrt(pow(vector->x, 2) + pow(vector->y, 2));
            vector->x /= dist ? dist : 1; // fail-proof if 0, but might be inaccurate
            vector->y /= dist ? dist : 1; // same
        }
    }
    
    for (int i = 0; i < 256; ++i) {
        (*permutations)[i] = i;
    }
    
    for (int i = 255; i >= 1; --i) {
        randomSeed = getNextRandomValue(randomSeed);
        
        uint8_t temp = (*permutations)[randomSeed & 255];
        (*permutations)[randomSeed & 255] = (*permutations)[i];
        (*permutations)[i] = temp;
    }
}

perlinNoiseState initPerlinNoise(
        uint32_t width, uint32_t height,
        double baseX, double baseY,
        uint32_t numOctaves, int32_t randomSeed,
        bool stitch, bool fractalNoise,
        uint8_t channelOptions, bool grayScale,
        double* offsetsX, double* offsetsY) {
    
    if (!width || !height)
        return NULL;
    
    perlinNoiseState state = malloc(sizeof(*state));
    //state->width = width;
    //state->height = height;
    
    if (baseX)
        baseX = 1.0 / fabs(baseX);
    
    if (baseY)
        baseY = 1.0 / fabs(baseY);
        
    state->numOctaves = numOctaves;
    
    generateRandom(randomSeed, &state->permutations, &state->vectors);
    
    state->stitch = stitch;
    if (stitch) {
        if (baseX) {
            double tmp1 = floor(baseX * width) / width;
            double tmp2 = ceil(baseX * width) / width;
            
            if (!tmp1 || baseX / tmp1 >= tmp2 / baseX) {
                baseX = tmp2;
            } else {
                baseX = tmp1;
            }
        }
        
        if (baseY) {
            double tmp1 = floor(baseY * height) / height;
            double tmp2 = ceil(baseY * height) / height;
            
            if (!tmp1 || baseY / tmp1 >= tmp2 / baseY) {
                baseY = tmp2;
            } else {
                baseY = tmp1;
            }
        }
        
        state->stitchArr[0] = round(width * baseX);
        state->stitchArr[1] = round(height * baseY);
    }
    
    // saving it now because
    state->baseX = baseX;
    state->baseY = baseY;
    state->fractalNoise = fractalNoise;
    
    state->channelOptions = channelOptions;
    state->grayScale = grayScale;
    
    if (grayScale)
        state->channelCount = 1;
    else
        state->channelCount = ((channelOptions) & 1) + ((channelOptions >> 1) & 1) + ((channelOptions >> 2) & 1);
    
    state->channelCount += ((channelOptions >> 3) & 1);
    
    state->offsetsX = calloc(numOctaves, sizeof(double));
    state->offsetsY = calloc(numOctaves, sizeof(double));
    
    if (offsetsX)
        memcpy(state->offsetsX, offsetsX, sizeof(double) * numOctaves);
        
    if (offsetsY)
        memcpy(state->offsetsY, offsetsY, sizeof(double) * numOctaves);
    
    return state;
}

uint32_t generatePerlinNoise(perlinNoiseState state, uint32_t x, uint32_t y) {
    double channelsOctave[4];
    double channels[4] = {0.0, 0.0, 0.0, 0.0};
    uint32_t stitchArr[2];
    
    uint8_t* permutations = state->permutations;
    vector2* vectors = state->vectors;
    
    double channelAlpha = 255;
    uint8_t red = 0, green = 0, blue = 0, alpha = 255;
    
    if (state->stitch) {
        memcpy(stitchArr, state->stitchArr, sizeof(stitchArr));
    }
    
    double baseX = state->baseX;
    double baseY = state->baseY;
    
    for (uint32_t octave = 0; octave < state->numOctaves; ++octave) {
        double offsetX = (state->offsetsX[octave] + x) * baseX + 4096.0;
        double offsetY = (state->offsetsY[octave] + y) * baseY + 4096.0;
        
        int x0 = floor(offsetX);
        int x1 = x0 + 1;
        
        int y0 = floor(offsetY);
        int y1 = y0 + 1;
        
        if (state->stitch) {
            int tmp1 = stitchArr[0] + 4096;
            int tmp2 = stitchArr[1] + 4096;
            
            if (x0 >= tmp1)
                x0 -= stitchArr[0];
            
            if (x1 >= tmp1)
                x1 -= stitchArr[0];
            
            if (y0 >= tmp2)
                y0 -= stitchArr[1];
            
            if (y1 >= tmp2)
                y1 -= stitchArr[1];
        }
        
        int idx1 = permutations[x0 & 255];
        int idx2 = permutations[x1 & 255];
        
        int v1 = permutations[((y0 & 255) + idx1) & 255];
        int v2 = permutations[((y0 & 255) + idx2) & 255];
        int v3 = permutations[((y1 & 255) + idx1) & 255];
        int v4 = permutations[((y1 & 255) + idx2) & 255];
        
        double dx0 = offsetX - floor(offsetX); // sx
        double dx1 = dx0 - 1.0;
        
        double dy0 = offsetY - floor(offsetY); // sy
        double dy1 = dy0 - 1.0;
        
        for (uint8_t channel = 0; channel < state->channelCount; ++channel) {
            double n0, n1;
            vector2* vectorArray = &vectors[channel * 256];
            
            n0 = vectorArray[v1].x * dx0 + vectorArray[v1].y * dy0;
            n1 = vectorArray[v2].x * dx1  + vectorArray[v2].y * dy0;
            double ix1 = interpolate(n0, n1, dx0);
            
            n0 = vectorArray[v3].x * dx0 + vectorArray[v3].y * dy1;
            n1 = vectorArray[v4].x * dx1  + vectorArray[v4].y * dy1;
            double ix2 = interpolate(n0, n1, dx0);
            
            channelsOctave[channel] = interpolate(ix1, ix2, dy0);
        }
        
        if (state->fractalNoise) {
            for (uint8_t channel = 0; channel < state->channelCount; ++channel) {
                channels[channel] += channelsOctave[channel] * channelAlpha;
            }
        } else {
            for (uint8_t channel = 0; channel < state->channelCount; ++channel) {
                channels[channel] += fabs(channelsOctave[channel]) * channelAlpha;
            }
        }
        
        channelAlpha *= 0.5;
        baseX *= 2.0;
        baseY *= 2.0;
        
        if (state->stitch) {
            stitchArr[0] *= 2;
            stitchArr[1] *= 2;
        }
    }
        
    uint8_t nextChannel = 0;
    if (state->grayScale) {
        red = state->fractalNoise ? ((int)round(channels[nextChannel++] + 255.0) >> 1) : round(channels[nextChannel++]);
        green = red;
        blue = red;
        
    } else {
        nextChannel = 0;
        if (state->channelOptions & 1)
            red = state->fractalNoise ? ((int)round(channels[nextChannel++] + 255.0) >> 1) : round(channels[nextChannel++]);
        if (state->channelOptions & 2)
            green = state->fractalNoise ? ((int)round(channels[nextChannel++] + 255.0) >> 1) : round(channels[nextChannel++]);
        if (state->channelOptions & 4)
            blue = state->fractalNoise ? ((int)round(channels[nextChannel++] + 255.0) >> 1) : round(channels[nextChannel++]);
    }
    
    if (state->channelOptions & 8)
        alpha = state->fractalNoise ? ((int)round(channels[nextChannel] + 255.0) >> 1) : round(channels[nextChannel]);
    
    alpha = min(max(alpha, 0U), 255U);
    red = min(max(red, 0U), alpha);
    green = min(max(green, 0U), alpha);
    blue = min(max(blue, 0U), alpha);
    
    uint32_t color = (alpha << 24) | (red << 16) | (green << 8) | blue;
    return unmultiplyColor(color);
}

void freePerlinNoise(perlinNoiseState state) {
    free(state->permutations);
    free(state->vectors);
    free(state->offsetsX);
    free(state->offsetsY);
    free(state);
}