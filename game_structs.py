import ctypes


class Vector3(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float)
    ]


class Rotator(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('pitch', ctypes.c_float),
        ('yaw', ctypes.c_float),
        ('roll', ctypes.c_float)
    ]


class Physics(ctypes.Structure):
    _fields_ = [("location", Vector3),
                ("rotation", Rotator),
                ("velocity", Vector3),
                ("angular_velocity", Vector3)]


class Entity(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('IsCar', ctypes.c_int32),
        ('Team', ctypes.c_int32),
        ('IsSelf', ctypes.c_int32),
        ('IsBall', ctypes.c_int32),
        ('IsBoostpad', ctypes.c_int32),
        ('Physics', Physics),
        ('BoostAmount', ctypes.c_float),
        ('DemoTimer', ctypes.c_float),
        ('OnGround', ctypes.c_int32),
        ('HasFlip', ctypes.c_int32)
    ]


class VehicleInputs(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('Throttle', ctypes.c_float),
        ('Steer', ctypes.c_float),
        ('Pitch', ctypes.c_float),
        ('Yaw', ctypes.c_float),
        ('Roll', ctypes.c_float),
        ('Jump', ctypes.c_int),
        ('Boost', ctypes.c_int),
        ('Handbrake', ctypes.c_int)
    ]
