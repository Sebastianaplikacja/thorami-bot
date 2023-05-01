import flatbuffers
from flatbuffers import Builder


class SimpleControllerState:
    def __init__(self,
                 steer: float = 0.0,
                 throttle: float = 0.0,
                 pitch: float = 0.0,
                 yaw: float = 0.0,
                 roll: float = 0.0,
                 jump: bool = False,
                 boost: bool = False,
                 handbrake: bool = False):
        self.steer = steer
        self.throttle = throttle
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        self.jump = jump
        self.boost = boost
        self.handbrake = handbrake

    def to_flatbuffer(self):
        mybuilder = flatbuffers.Builder(100)
        ControllerState.ControllerStateStart(mybuilder)
        ControllerState.ControllerStateAddSteer(mybuilder, self.steer)
        ControllerState.ControllerStateAddThrottle(mybuilder, self.throttle)
        ControllerState.ControllerStateAddPitch(mybuilder, self.pitch)
        ControllerState.ControllerStateAddYaw(mybuilder, self.yaw)
        ControllerState.ControllerStateAddRoll(mybuilder, self.roll)
        ControllerState.ControllerStateAddJump(mybuilder, self.jump)
        ControllerState.ControllerStateAddBoost(mybuilder, self.boost)
        ControllerState.ControllerStateAddHandbrake(mybuilder, self.handbrake)
        ControllerState.ControllerStateEnd(mybuilder)
        return mybuilder


class ControllerState(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsControllerState(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ControllerState()
        x.Init(buf, n + offset)
        return x

    # ControllerState
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # /// -1 for full reverse, 1 for full forward
    # ControllerState
    def Throttle(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

    # /// -1 for full left, 1 for full right
    # ControllerState
    def Steer(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

    # /// -1 for nose down, 1 for nose up
    # ControllerState
    def Pitch(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

    # /// -1 for full left, 1 for full right
    # ControllerState
    def Yaw(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

    # /// -1 for roll left, 1 for roll right
    # ControllerState
    def Roll(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

    # /// true if you want to press the jump button
    # ControllerState
    def Jump(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos)
        return 0

    # /// true if you want to press the boost button
    # ControllerState
    def Boost(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos)
        return 0

    # /// true if you want to press the handbrake button
    # ControllerState
    def Handbrake(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos)
        return 0

    def ControllerStateStart(mybuilder):
        mybuilder.StartObject(8)

    def ControllerStateAddThrottle(builder, throttle):
        builder.PrependFloat32Slot(0, throttle, 0.0)

    def ControllerStateAddSteer(builder, steer):
        builder.PrependFloat32Slot(1, steer, 0.0)

    def ControllerStateAddPitch(builder, pitch):
        builder.PrependFloat32Slot(2, pitch, 0.0)

    def ControllerStateAddYaw(builder, yaw):
        builder.PrependFloat32Slot(3, yaw, 0.0)

    def ControllerStateAddRoll(builder, roll):
        builder.PrependFloat32Slot(4, roll, 0.0)

    def ControllerStateAddJump(builder, jump):
        builder.PrependBoolSlot(5, jump, 0)

    def ControllerStateAddBoost(builder, boost):
        builder.PrependBoolSlot(6, boost, 0)

    def ControllerStateAddHandbrake(builder, handbrake):
        builder.PrependBoolSlot(7, handbrake, 0)

    def ControllerStateEnd(builder):
        return builder.EndObject()
