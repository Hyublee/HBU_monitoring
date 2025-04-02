import ctypes

hxapi = ctypes.CDLL("HXApi")

class HX_ComType():
    HX_ETHERNET = 0
    HXRTX       = 1

hxapi.HxInitialize2.argtypes = []