import ctypes, os

perlinNoise = ctypes.CDLL(os.path.abspath("perlinNoise.dll"))

initPerlinNoise = perlinNoise.initPerlinNoise
initPerlinNoise.argtypes = (ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_double, ctypes.c_double,
                            ctypes.c_uint32, ctypes.c_int32,
                            ctypes.c_bool, ctypes.c_bool,
                            ctypes.c_uint8, ctypes.c_bool,
                            ctypes.POINTER(ctypes.c_double),
                            ctypes.POINTER(ctypes.c_double))
initPerlinNoise.restype = ctypes.c_void_p

generatePerlinNoise = perlinNoise.generatePerlinNoise
generatePerlinNoise.argtypes = (ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32)
generatePerlinNoise.restype = ctypes.c_uint32

freePerlinNoise = perlinNoise.freePerlinNoise
freePerlinNoise.argtypes = (ctypes.c_void_p,)
freePerlinNoise.restype = None