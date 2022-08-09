import ctypes, os
from pyPerlinNoise import perlinNoise as pythonPerlinNoise

class perlinVector2(ctypes.Structure):
    _fields_= [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double)
    ]
    
perlinNoise = ctypes.CDLL(os.path.abspath("perlinNoise.dll"))

initPerlinNoise = perlinNoise.initPerlinNoise
initPerlinNoise.argtypes = (ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_double, ctypes.c_double,
                            ctypes.c_uint32, ctypes.c_int32,
                            ctypes.c_bool, ctypes.c_bool,
                            ctypes.c_uint8, ctypes.c_bool,
                            ctypes.POINTER(perlinVector2))
initPerlinNoise.restype = ctypes.c_void_p

generatePerlinNoise = perlinNoise.generatePerlinNoise
generatePerlinNoise.argtypes = (ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32)
generatePerlinNoise.restype = ctypes.c_uint32

freePerlinNoise = perlinNoise.freePerlinNoise
freePerlinNoise.argtypes = (ctypes.c_void_p,)
freePerlinNoise.restype = None
