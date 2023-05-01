from typing import Any
import numpy as np
from game_state import GameState
from player_data import PlayerData
import ctypes as ctypes
from game_structs import Entity
from physics_object import PhysicsObject

BOOST_LOCATIONS = (
    (0.0, -4240.0, 70.0),
    (-1792.0, -4184.0, 70.0),
    (1792.0, -4184.0, 70.0),
    (-3072.0, -4096.0, 73.0),
    (3072.0, -4096.0, 73.0),
    (- 940.0, -3308.0, 70.0),
    (940.0, -3308.0, 70.0),
    (0.0, -2816.0, 70.0),
    (-3584.0, -2484.0, 70.0),
    (3584.0, -2484.0, 70.0),
    (-1788.0, -2300.0, 70.0),
    (1788.0, -2300.0, 70.0),
    (-2048.0, -1036.0, 70.0),
    (0.0, -1024.0, 70.0),
    (2048.0, -1036.0, 70.0),
    (-3584.0, 0.0, 73.0),
    (-1024.0, 0.0, 70.0),
    (1024.0, 0.0, 70.0),
    (3584.0, 0.0, 73.0),
    (-2048.0, 1036.0, 70.0),
    (0.0, 1024.0, 70.0),
    (2048.0, 1036.0, 70.0),
    (-1788.0, 2300.0, 70.0),
    (1788.0, 2300.0, 70.0),
    (-3584.0, 2484.0, 70.0),
    (3584.0, 2484.0, 70.0),
    (0.0, 2816.0, 70.0),
    (- 940.0, 3310.0, 70.0),
    (940.0, 3308.0, 70.0),
    (-3072.0, 4096.0, 73.0),
    (3072.0, 4096.0, 73.0),
    (-1792.0, 4184.0, 70.0),
    (1792.0, 4184.0, 70.0),
    (0.0, 4240.0, 70.0),
)


def rotation_to_quaternion(m: np.ndarray) -> np.ndarray:
    trace = np.trace(m)
    q = np.zeros(4)

    if trace > 0:
        s = (trace + 1) ** 0.5
        q[0] = s * 0.5
        s = 0.5 / s
        q[1] = (m[2, 1] - m[1, 2]) * s
        q[2] = (m[0, 2] - m[2, 0]) * s
        q[3] = (m[1, 0] - m[0, 1]) * s
    else:
        if m[0, 0] >= m[1, 1] and m[0, 0] >= m[2, 2]:
            s = (1 + m[0, 0] - m[1, 1] - m[2, 2]) ** 0.5
            inv_s = 0.5 / s
            q[1] = 0.5 * s
            q[2] = (m[1, 0] + m[0, 1]) * inv_s
            q[3] = (m[2, 0] + m[0, 2]) * inv_s
            q[0] = (m[2, 1] - m[1, 2]) * inv_s
        elif m[1, 1] > m[2, 2]:
            s = (1 + m[1, 1] - m[0, 0] - m[2, 2]) ** 0.5
            inv_s = 0.5 / s
            q[1] = (m[0, 1] + m[1, 0]) * inv_s
            q[2] = 0.5 * s
            q[3] = (m[1, 2] + m[2, 1]) * inv_s
            q[0] = (m[0, 2] - m[2, 0]) * inv_s
        else:
            s = (1 + m[2, 2] - m[0, 0] - m[1, 1]) ** 0.5
            inv_s = 0.5 / s
            q[1] = (m[0, 2] + m[2, 0]) * inv_s
            q[2] = (m[1, 2] + m[2, 1]) * inv_s
            q[3] = 0.5 * s
            q[0] = (m[1, 0] - m[0, 1]) * inv_s

    # q[[0, 1, 2, 3]] = q[[3, 0, 1, 2]]

    return -q


def encode_gamestate(state: GameState):
    state_vals = [0, state.blue_score, state.orange_score]
    state_vals += state.boost_pads.tolist()

    for bd in (state.ball, state.inverted_ball):
        state_vals += bd.position.tolist()
        state_vals += bd.linear_velocity.tolist()
        state_vals += bd.angular_velocity.tolist()

    for p in state.players:
        state_vals += [p.car_id, p.team_num]
        for cd in (p.car_data, p.inverted_car_data):
            state_vals += cd.position.tolist()
            state_vals += rotation_to_quaternion(cd.rotation_mtx()).tolist()
            state_vals += cd.linear_velocity.tolist()
            state_vals += cd.angular_velocity.tolist()
        state_vals += [
            0,
            0,
            0,
            0,
            0,
            p.is_demoed,
            p.on_ground,
            p.ball_touched,
            p.has_flip,
            p.boost_amount
        ]
    return state_vals


class BatchedObsBuilder:
    def __init__(self):
        super().__init__()
        self.current_state = None
        self.current_obs = None

    def batched_build_obs(self, encoded_states: np.ndarray) -> Any:
        raise NotImplementedError

    def add_actions(self, obs: Any, previous_actions: np.ndarray, player_index=None):
        raise NotImplementedError

    def _reset(self, initial_state: GameState):
        raise NotImplementedError

    def reset(self, initial_state: GameState):
        self.current_state = False
        self.current_obs = None
        self._reset(initial_state)

    def build_obs(self, player: PlayerData, state: GameState, previous_action: np.ndarray) -> Any:
        # if state != self.current_state:
        self.current_obs = self.batched_build_obs(
            np.expand_dims(encode_gamestate(state), axis=0)
        )
        self.current_state = state

        for i, p in enumerate(state.players):
            if p == player:
                self.add_actions(self.current_obs, previous_action, i)
                return self.current_obs[i]


IS_SELF, IS_MATE, IS_OPP, IS_BALL, IS_BOOST = range(5)
POS = slice(5, 8)
LIN_VEL = slice(8, 11)
FW = slice(11, 14)
UP = slice(14, 17)
ANG_VEL = slice(17, 20)
BOOST, DEMO, ON_GROUND, HAS_FLIP = range(20, 24)
ACTIONS = range(24, 32)

BALL_STATE_LENGTH = 18
PLAYER_CAR_STATE_LENGTH = 13
PLAYER_TERTIARY_INFO_LENGTH = 10
PLAYER_INFO_LENGTH = 2 + 2 * PLAYER_CAR_STATE_LENGTH + PLAYER_TERTIARY_INFO_LENGTH


class NextoObsBuilder(BatchedObsBuilder):
    _invert = np.array([1] * 5 + [-1, -1, 1] * 5 + [1] * 4)
    _norm = np.array([1.] * 5 + [2300] * 6 + [1] * 6 + [5.5] * 3 + [1] * 4)

    def __init__(self, n_players=None, n_boosts=None, buffer_cursor=None):
        super().__init__()
        self.n_players = n_players
        self.n_boosts = n_boosts
        self._boost_locations = np.empty([n_boosts, 3])
        # self._boost_locations =  np.array(BOOST_LOCATIONS)

        entity_size = ctypes.sizeof(Entity)
        buffer_cursor += 20 + entity_size

        # Get Boosts
        for i in range(n_boosts):
            entity = Entity.from_address(buffer_cursor)
            buffer_cursor += entity_size
            location = entity.Physics.location
            testing = [location.x, location.y, location.z]
            self._boost_locations[i] = [location.x, location.y, location.z]

        boosts_heights = self._boost_locations[:, 2]
        boosts_heights_min = np.amin(boosts_heights)
        boosts_heights_max = np.amax(boosts_heights)

        self._boost_types = abs(boosts_heights - boosts_heights_max) < abs(boosts_heights - boosts_heights_min)
        test = 0

    @staticmethod
    def _quats_to_rot_mtx(quats: np.ndarray) -> np.ndarray:
        # From rlgym.utils.math.quat_to_rot_mtx
        w = -quats[:, 0]
        x = -quats[:, 1]
        y = -quats[:, 2]
        z = -quats[:, 3]

        theta = np.zeros((quats.shape[0], 3, 3))

        norm = np.einsum("fq,fq->f", quats, quats)

        sel = norm != 0

        w = w[sel]
        x = x[sel]
        y = y[sel]
        z = z[sel]

        s = 1.0 / norm[sel]

        # front direction
        theta[sel, 0, 0] = 1.0 - 2.0 * s * (y * y + z * z)
        theta[sel, 1, 0] = 2.0 * s * (x * y + z * w)
        theta[sel, 2, 0] = 2.0 * s * (x * z - y * w)

        # left direction
        theta[sel, 0, 1] = 2.0 * s * (x * y - z * w)
        theta[sel, 1, 1] = 1.0 - 2.0 * s * (x * x + z * z)
        theta[sel, 2, 1] = 2.0 * s * (y * z + x * w)

        # up direction
        theta[sel, 0, 2] = 2.0 * s * (x * z + y * w)
        theta[sel, 1, 2] = 2.0 * s * (y * z - x * w)
        theta[sel, 2, 2] = 1.0 - 2.0 * s * (x * x + y * y)

        return theta

    @staticmethod
    def convert_to_relative(q, kv):
        # kv[..., POS.start:LIN_VEL.stop] -= q[..., POS.start:LIN_VEL.stop]
        kv[..., POS] -= q[..., POS]
        forward = q[..., FW]
        theta = np.arctan2(forward[..., 0], forward[..., 1])
        theta = np.expand_dims(theta, axis=-1)
        ct = np.cos(theta)
        st = np.sin(theta)
        xs = kv[..., POS.start:ANG_VEL.stop:3]
        ys = kv[..., POS.start + 1:ANG_VEL.stop:3]
        # Use temp variables to prevent modifying original array
        nx = ct * xs - st * ys
        ny = st * xs + ct * ys
        kv[..., POS.start:ANG_VEL.stop:3] = nx  # x-components
        kv[..., POS.start + 1:ANG_VEL.stop:3] = ny  # y-components

    def batched_build_obs(self, encoded_states: np.ndarray):
        ball_start_index = 3 + len(self._boost_locations)
        players_start_index = ball_start_index + BALL_STATE_LENGTH
        player_length = PLAYER_INFO_LENGTH

        n_players = (encoded_states.shape[1] - players_start_index) // player_length
        lim_players = n_players if self.n_players is None else self.n_players
        n_entities = lim_players + 1 + self.n_boosts

        # SELECTORS
        sel_players = slice(0, lim_players)
        sel_ball = sel_players.stop
        sel_boosts = slice(sel_ball + 1, None)

        # MAIN ARRAYS
        q = np.zeros((n_players, encoded_states.shape[0], 1, 32))
        kv = np.zeros((n_players, encoded_states.shape[0], n_entities, 24))  # Keys and values are (mostly) shared
        m = np.zeros((n_players, encoded_states.shape[0], n_entities))  # Mask is shared

        # BALL
        kv[:, :, sel_ball, 3] = 1
        kv[:, :, sel_ball, np.r_[POS, LIN_VEL, ANG_VEL]] = encoded_states[:, ball_start_index: ball_start_index + 9]

        # BOOSTS
        kv[:, :, sel_boosts, IS_BOOST] = 1
        kv[:, :, sel_boosts, POS] = self._boost_locations
        kv[:, :, sel_boosts, BOOST] = 0.12 + 0.88 * self._boost_types
        kv[:, :, sel_boosts, DEMO] = encoded_states[:, 3:3 + self.n_boosts]  # FIXME boost timer

        # PLAYERS
        teams = encoded_states[0, players_start_index + 1::player_length]
        kv[:, :, :n_players, IS_MATE] = 1 - teams  # Default team is blue
        kv[:, :, :n_players, IS_OPP] = teams
        for i in range(n_players):
            encoded_player = encoded_states[:, players_start_index + i * player_length: players_start_index + (i + 1) * player_length]

            kv[i, :, i, IS_SELF] = 1
            kv[:, :, i, POS] = encoded_player[:, 2: 5]  # TODO constants for these indices
            kv[:, :, i, LIN_VEL] = encoded_player[:, 9: 12]
            quats = encoded_player[:, 5: 9]
            rot_mtx = self._quats_to_rot_mtx(quats)
            kv[:, :, i, FW] = rot_mtx[:, :, 0]
            kv[:, :, i, UP] = rot_mtx[:, :, 2]
            kv[:, :, i, ANG_VEL] = encoded_player[:, 12: 15]
            kv[:, :, i, BOOST] = encoded_player[:, 37]
            kv[:, :, i, DEMO] = encoded_player[:, 33]  # FIXME demo timer
            kv[:, :, i, ON_GROUND] = encoded_player[:, 34]
            kv[:, :, i, HAS_FLIP] = encoded_player[:, 36]

        kv[teams == 1] *= self._invert
        kv[np.argwhere(teams == 1), ..., (IS_MATE, IS_OPP)] = kv[
            np.argwhere(teams == 1), ..., (IS_OPP, IS_MATE)]  # Swap teams

        kv /= self._norm

        for i in range(n_players):
            q[i, :, 0, :kv.shape[-1]] = kv[i, :, i, :]

        self.convert_to_relative(q, kv)
        # kv[:, :, :, 5:11] -= q[:, :, :, 5:11]

        # MASK
        m[:, :, n_players: lim_players] = 1

        return [(q[i], kv[i], m[i]) for i in range(n_players)]

    def add_actions(self, obs: Any, previous_actions: np.ndarray, player_index=None):
        if player_index is None:
            for (q, kv, m), act in zip(obs, previous_actions):
                q[:, 0, ACTIONS] = act
        else:
            q, kv, m = obs[player_index]
            q[:, 0, ACTIONS] = previous_actions

    def _reset(self, initial_state: GameState):
        return
