#include <stdbool.h>
#include <inttypes.h>

#ifndef AS3_PERLIN_NOISE_H
#define AS3_PERLIN_NOISE_H
typedef struct _perlinNoiseState *perlinNoiseState;

perlinNoiseState initPerlinNoise(
        uint32_t width, uint32_t height,
        double baseX, double baseY,
        uint32_t numOctaves, int32_t randomSeed,
        bool stitch, bool fractalNoise,
        uint8_t channelOptions, bool grayScale,
        double* offsetsX, double* offsetsY);

uint32_t generatePerlinNoise(perlinNoiseState state, uint32_t x, uint32_t y);

void freePerlinNoise(perlinNoiseState state);
#endif