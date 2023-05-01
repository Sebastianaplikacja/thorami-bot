import numpy as np
from game_state import GameState
from nexto_obs import NextoObsBuilder
from controller_state import SimpleControllerState
from agent import Agent
import random
import math

import logging
logging.basicConfig(filename='BOT_LOG6.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



from rlbot.utils.structures.game_data_struct import GameTickPacket
# from rlbot.utils.structures.quick_chats import QuickChats


KICKOFF_CONTROLS = (
        11 * 4 * [SimpleControllerState(throttle=1, boost=True)]
        + 4 * 4 * [SimpleControllerState(throttle=1, boost=True, steer=-1)]
        + 2 * 4 * [SimpleControllerState(throttle=1, jump=True, boost=True)]
        + 1 * 4 * [SimpleControllerState(throttle=1, boost=True)]
        + 1 * 4 * [SimpleControllerState(throttle=1, yaw=0.8, pitch=-0.7, jump=True, boost=True)]
        + 13 * 4 * [SimpleControllerState(throttle=1, pitch=1, boost=True)]
        + 10 * 4 * [SimpleControllerState(throttle=1, roll=1, pitch=0.5)]
)

KICKOFF_NUMPY = np.array([
    [scs.throttle, scs.steer, scs.pitch, scs.yaw, scs.roll, scs.jump, scs.boost, scs.handbrake]
    for scs in KICKOFF_CONTROLS
])


class Nexto:
    def __init__(self, buffer_cursor, total_boosts, total_players):
        self.team = 0
        self.index = 0
        self.obs_builder = None
        self.buffer_cursor = buffer_cursor
        self.total_boosts = total_boosts
        self.total_players = total_players
        self.game_state: GameState = GameState(total_boosts)
        self.controls = None
        self.action = None
        self.agent = Agent()
        self.hardcoded_kickoffs = True
        self.stochastic_kickoffs = True    

    def initialize_agent(self):
        temp_gamestate = GameState(self.total_boosts)
        temp_gamestate.decode(self.buffer_cursor)
        self.obs_builder = NextoObsBuilder(self.total_players, self.total_boosts, self.buffer_cursor)
        self.game_state = GameState(self.total_boosts)
        self.index = temp_gamestate.index
        self.team = temp_gamestate.players[self.index].team_num
        self.controls = SimpleControllerState()
        self.action = np.zeros(8)


    def get_output(self) -> SimpleControllerState:
        self.game_state = GameState(self.total_boosts)
        self.game_state.decode(self.buffer_cursor)

        player = self.game_state.players[self.index]
        teammates = [p for p in self.game_state.players if p.team_num == self.team and p != player]
        opponents = [p for p in self.game_state.players if p.team_num != self.team]

        self.game_state.players = [player] + teammates + opponents

        obs = self.obs_builder.build_obs(player, self.game_state, self.action)

        self.action, weights = self.agent.act(obs, 1)
        self.update_controls(self.action)
        
        #for i in range(168):
#         action = KICKOFF_NUMPY[150]
#         # logging.warning(f'\n\n ------------- Nexto KICKOFFFF {action}-----------\n\n')  
#         self.action = action            
#         self.update_controls(self.action) 
#         if self.hardcoded_kickoffs: 
#              #logging.warning(f'\n\n ------------- Nexto KICKOFFFF {self.game_state.ball.position[1]}-----------\n\n')
#              if self.game_state.ball.position[1] == 0 or self.game_state.ball.position[1] == 0.0 :
#                 #  logging.warning(f'\n\n ------------- Nexto KICKOFFFF ss {self.game_state.ball.position[1]} -----------\n\n')
#                   for i in  range(len(KICKOFF_NUMPY)): 
#                      action = KICKOFF_NUMPY[i]
#                 #     logging.warning(f'\n\n ------------- Nexto KICKOFFFF ss3 {action}-----------\n\n')
#                      self.action = action
#                      self.update_controls(self.action)        

        return self.controls

    def update_controls(self, action):
        self.controls.throttle = action[0]
        self.controls.steer = action[1]
        self.controls.pitch = action[2]
        self.controls.yaw = action[3]
        self.controls.roll = action[4]
        self.controls.jump = action[5] > 0
        self.controls.boost = action[6] > 0
        self.controls.handbrake = action[7] > 0
