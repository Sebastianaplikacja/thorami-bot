import math
import numpy as np
from game_structs import Physics, Vector3, Rotator


class PhysicsObject:
    def __init__(self, position=None, euler_angles=None, linear_velocity=None, angular_velocity=None):
        self.position: np.ndarray = position if position else np.zeros(3)

        # ones by default to prevent mathematical errors when converting quat to rot matrix on empty physics state
        self.quaternion: np.ndarray = np.ones(4)

        self.linear_velocity: np.ndarray = linear_velocity if linear_velocity else np.zeros(3)
        self.angular_velocity: np.ndarray = angular_velocity if angular_velocity else np.zeros(3)
        self._euler_angles: np.ndarray = euler_angles if euler_angles else np.zeros(3)
        self._rotation_mtx: np.ndarray = np.zeros((3, 3))
        self._has_computed_rot_mtx = False

        self._invert_vec = np.asarray([-1, -1, 1])
        self._invert_pyr = np.asarray([0, math.pi, 0])

    def decode_car_data(self, car_data: Physics):
        self.position = self._vector_to_numpy(car_data.location)
        self._euler_angles = self._rotator_to_numpy(car_data.rotation)
        self.linear_velocity = self._vector_to_numpy(car_data.velocity)
        self.angular_velocity = self._vector_to_numpy(car_data.angular_velocity)

    def decode_ball_data(self, ball_data: Physics):
        self.position = self._vector_to_numpy(ball_data.location)
        self.linear_velocity = self._vector_to_numpy(ball_data.velocity)
        self.angular_velocity = self._vector_to_numpy(ball_data.angular_velocity)

    def invert(self, other):
        self.position = other.position * self._invert_vec
        self._euler_angles = other.euler_angles() + self._invert_pyr
        self.linear_velocity = other.linear_velocity * self._invert_vec
        self.angular_velocity = other.angular_velocity * self._invert_vec

    # pitch, yaw, roll
    def euler_angles(self) -> np.ndarray:
        return self._euler_angles

    def pitch(self):
        return self._euler_angles[0]

    def yaw(self):
        return self._euler_angles[1]

    def roll(self):
        return self._euler_angles[2]

    def rotation_mtx(self) -> np.ndarray:
        if not self._has_computed_rot_mtx:
            self._rotation_mtx = self._euler_to_rotation(self._euler_angles)
            self._has_computed_rot_mtx = True

        return self._rotation_mtx

    def forward(self) -> np.ndarray:
        return self.rotation_mtx()[:, 0]

    def right(self) -> np.ndarray:
        return self.rotation_mtx()[:, 1] * -1  # These are inverted compared to rlgym because rlbot reasons

    def left(self) -> np.ndarray:
        return self.rotation_mtx()[:, 1]

    def up(self) -> np.ndarray:
        return self.rotation_mtx()[:, 2]

    @staticmethod
    def _vector_to_numpy(vector: Vector3):
        return np.asarray([vector.x, vector.y, vector.z])

    @staticmethod
    def _rotator_to_numpy(rotator: Rotator):
        return np.asarray([rotator.pitch, rotator.yaw, rotator.roll])

    @staticmethod
    def _euler_to_rotation(pyr: np.ndarray):
        cp = math.cos(pyr[0])
        sp = math.sin(pyr[0])
        cy = math.cos(pyr[1])
        sy = math.sin(pyr[1])
        cr = math.cos(pyr[2])
        sr = math.sin(pyr[2])

        theta = np.empty((3, 3))

        # front direction
        theta[0, 0] = cp * cy
        theta[1, 0] = cp * sy
        theta[2, 0] = sp

        # left direction
        theta[0, 1] = cy * sp * sr - cr * sy
        theta[1, 1] = sy * sp * sr + cr * cy
        theta[2, 1] = -cp * sr

        # up direction
        theta[0, 2] = -cr * cy * sp - sr * sy
        theta[1, 2] = -cr * sy * sp + sr * cy
        theta[2, 2] = cp * cr

        return theta
