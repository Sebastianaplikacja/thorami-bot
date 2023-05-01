from typing import List
import numpy as np
import ctypes as ctypes

from game_structs import Entity

from physics_object import PhysicsObject
from player_data import PlayerData


class GameState:
    def __init__(self, total_boostpads: int):
        self.blue_score = 0
        self.orange_score = 0
        self.index = 0
        self.players: List[PlayerData] = []

        self.ball: PhysicsObject = PhysicsObject()
        self.inverted_ball: PhysicsObject = PhysicsObject()

        # List of "booleans" (1 or 0)
        self.boost_pads: np.ndarray = np.zeros(total_boostpads, dtype=np.float32)
        self.inverted_boost_pads: np.ndarray = np.zeros_like(self.boost_pads, dtype=np.float32)

    def decode(self, buffer_cursor: int):
        entity_size = ctypes.sizeof(Entity)
        # total_entities = ctypes.c_int32.from_address(buffer_cursor).value
        buffer_cursor += 4
        total_boosts = ctypes.c_int32.from_address(buffer_cursor).value
        buffer_cursor += 4
        total_players = ctypes.c_int32.from_address(buffer_cursor).value
        buffer_cursor += 4

        self.blue_score = ctypes.c_int32.from_address(buffer_cursor).value
        buffer_cursor += 4
        self.orange_score = ctypes.c_int32.from_address(buffer_cursor).value
        buffer_cursor += 4

        # Get Ball
        entity = Entity.from_address(buffer_cursor)
        self.ball.decode_ball_data(entity.Physics)
        self.inverted_ball.invert(self.ball)
        buffer_cursor += entity_size

        # Get Boosts
        for i in range(total_boosts):
            entity = Entity.from_address(buffer_cursor)
            buffer_cursor += entity_size
            self.boost_pads[i] = not entity.DemoTimer < 1.0

        self.inverted_boost_pads[:] = self.boost_pads[::-1]

        # Get Players
        for i in range(total_players):
            entity = Entity.from_address(buffer_cursor)
            buffer_cursor += entity_size
            self.players.append(self._decode_player(entity, i))
            if entity.IsSelf:
                self.index = i

    @staticmethod
    def _decode_player(entity: Entity, index: int) -> PlayerData:
        player_data = PlayerData()

        player_data.car_data.decode_car_data(entity.Physics)
        player_data.inverted_car_data.invert(player_data.car_data)

        player_data.car_id = index
        player_data.team_num = entity.Team
        player_data.is_demoed = entity.DemoTimer < 1.0
        player_data.on_ground = entity.OnGround > 0
        player_data.ball_touched = False
        player_data.has_flip = entity.HasFlip
        player_data.has_jump = player_data.on_ground and entity.HasFlip
        player_data.boost_amount = entity.BoostAmount

        return player_data
