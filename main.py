import mmap
import ctypes
import time
from nexto import Nexto
from game_structs import VehicleInputs
import datetime
import logging
logging.basicConfig(filename='BOT_LOG6.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

ntdll = ctypes.WinDLL('NTDLL.DLL')
kernel32 = ctypes.WinDLL('Kernel32.DLL')


def set_timer_resolution():
    local_resolution = ctypes.c_long(int(5000))
    local_current = ctypes.c_long()
    ntdll.NtSetTimerResolution(local_resolution, 1, ctypes.byref(local_current))


def query_performance_counter():
    local_timer = ctypes.c_longlong()
    kernel32.QueryPerformanceCounter(ctypes.byref(local_timer))
    return float(local_timer.value)


def query_performance_frequency():
    local_frequency = ctypes.c_longlong()
    kernel32.QueryPerformanceFrequency(ctypes.byref(local_frequency))
    return float(local_frequency.value)


# Create memory mapped file handle
buffer = mmap.mmap(-1, 0x8000, 'ThoramiBotMMF', access=mmap.ACCESS_WRITE)
bufferObj = ctypes.py_object(buffer)
bufferAddress = ctypes.c_void_p()
bufferLength = ctypes.c_ssize_t()
ctypes.pythonapi.PyObject_AsReadBuffer(bufferObj, ctypes.byref(bufferAddress), ctypes.byref(bufferLength))
bufferCursor = bufferAddress.value

total_boosts = ctypes.c_int32.from_address(bufferCursor + 4).value
total_players = ctypes.c_int32.from_address(bufferCursor + 8).value
bot = Nexto(bufferCursor, total_boosts, total_players)
bot.initialize_agent()

interval = 1.0 / 120.0
frequency = query_performance_frequency()

while True:
    start_time = query_performance_counter()
    controls = bot.get_output()
    data = VehicleInputs()
    data.Throttle = controls.throttle
    data.Steer = controls.steer
    data.Pitch = controls.pitch
    data.Yaw = controls.yaw
    data.Roll = controls.roll
    logging.warning(f'\n\n ------------- Nexto TIME {start_time}-----------\n\n')   
    
    if controls.jump:
        data.Jump = 1
    else:
        data.Jump = 0

    if controls.boost:
        data.Boost = 1
    else:
        data.Boost = 0

    if controls.handbrake:
        data.Handbrake = 1
    else:
        data.Handbrake = 0

    buffer.seek(0x7000)
    towrite = bytearray(data)
    buffer.write(towrite)
    end_time = query_performance_counter()
    timeout = interval - (end_time - start_time) / frequency - 0.0015

    if timeout > 0.0:
        time.sleep(timeout)

    while interval - ((end_time - start_time) / frequency) > 0.0:
        end_time = query_performance_counter()
