#include <stdbool.h>
#include <inttypes.h>

#ifndef AS3_PERLIN_NOISE_H
#define AS3_PERLIN_NOISE_H

typedef struct {
    double x;
    double y;
} perlinVector2;

typedef struct _perlinState *perlinState;

perlinState initPerlinNoise(
        uint32_t width, uint32_t height,
        double baseX, double baseY,
        uint32_t numOctaves, int32_t randomSeed,
        bool stitch, bool fractalNoise,
        uint8_t channelOptions, bool grayScale,
        perlinVector2* offsets);

uint32_t generatePerlinNoise(perlinState state, uint32_t width, uint32_t height, uint32_t* out);

void freePerlinNoise(perlinState state);
#endif