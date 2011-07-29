import unittest
from pelita.player import *
from pelita.datamodel import create_CTFUniverse, north, stop
from pelita.game_master import GameMaster
from pelita.viewer import AsciiViewer

class TestAbstractPlayer(unittest.TestCase):

    def test_convenience(self):

        test_layout = (
        """ ##################
            #0#.  .  # .     #
            #2#####    #####1#
            #     . #  .  .#3#
            ################## """)

        game_master = GameMaster(test_layout, 4, 200)
        universe = game_master.universe
        player_0 = StoppingPlayer()
        player_1 = TestPlayer([stop, north])
        player_2 = StoppingPlayer()
        player_3 = StoppingPlayer()
        game_master.register_player(player_0)
        game_master.register_player(player_1)
        game_master.register_player(player_2)
        game_master.register_player(player_3)

        self.assertEqual(universe.bots[0], player_0.me)
        self.assertEqual(universe.bots[1], player_1.me)
        self.assertEqual(universe.bots[2], player_2.me)
        self.assertEqual(universe.bots[3], player_3.me)

        self.assertEqual(universe, player_1.current_uni)
        self.assertEqual([universe.bots[0]], player_2.team_bots)
        self.assertEqual([universe.bots[1]], player_3.team_bots)
        self.assertEqual([universe.bots[2]], player_0.team_bots)
        self.assertEqual([universe.bots[3]], player_1.team_bots)
        self.assertEqual([universe.bots[i] for i in (1, 3)], player_0.enemy_bots)
        self.assertEqual([universe.bots[i] for i in (0, 2)], player_1.enemy_bots)
        self.assertEqual([universe.bots[i] for i in (1, 3)], player_2.enemy_bots)
        self.assertEqual([universe.bots[i] for i in (0, 2)], player_3.enemy_bots)
        self.assertEqual(universe.bots[1].current_pos, player_1.current_pos)
        self.assertEqual(universe.bots[1].initial_pos, player_1.initial_pos)

        game_master.play_round(0)
        game_master.play_round(1)
        self.assertEqual(universe, player_1.current_uni)
        self.assertEqual((16, 1), player_1.current_pos)
        self.assertEqual((16, 2), player_1.previous_pos)
        self.assertNotEqual(player_1.current_uni, player_1.universe_states[-2])

class TestBFS_Player(unittest.TestCase):

    def test_adjacency_bfs(self):
        test_layout = (
        """ ##################
            #0#.  .  # .     #
            # #####    ##### #
            #     . #  .  .#1#
            ################## """)
        game_master = GameMaster(test_layout, 2, 200)
        bfs = BFSPlayer()
        stopping = StoppingPlayer()
        game_master.register_player(bfs)
        game_master.register_player(stopping)
        adjacency_target = {(7, 3): [(7, 2), (7, 3), (6, 3)],
         (1, 3): [(1, 2), (2, 3), (1, 3)],
         (12, 1): [(13, 1), (12, 1), (11, 1)],
         (16, 2): [(16, 3), (16, 1), (16, 2)],
         (15, 1): [(16, 1), (15, 1), (14, 1)],
         (5, 1): [(6, 1), (5, 1), (4, 1)],
         (10, 3): [(10, 2), (11, 3), (10, 3), (9, 3)],
         (7, 2): [(7, 3), (7, 1), (8, 2), (7, 2)],
         (1, 2): [(1, 3), (1, 1), (1, 2)],
         (3, 3): [(4, 3), (3, 3), (2, 3)],
         (13, 3): [(14, 3), (13, 3), (12, 3)],
         (8, 1): [(8, 2), (8, 1), (7, 1)],
         (16, 3): [(16, 2), (16, 3)],
         (6, 3): [(7, 3), (6, 3), (5, 3)],
         (14, 1): [(15, 1), (14, 1), (13, 1)],
         (11, 1): [(12, 1), (11, 1), (10, 1)],
         (4, 1): [(5, 1), (4, 1), (3, 1)],
         (1, 1): [(1, 2), (1, 1)],
         (12, 3): [(13, 3), (12, 3), (11, 3)],
         (8, 2): [(8, 1), (9, 2), (8, 2), (7, 2)],
         (7, 1): [(7, 2), (8, 1), (7, 1), (6, 1)],
         (9, 3): [(9, 2), (10, 3), (9, 3)],
         (2, 3): [(3, 3), (2, 3), (1, 3)],
         (10, 1): [(10, 2), (11, 1), (10, 1)],
         (5, 3): [(6, 3), (5, 3), (4, 3)],
         (13, 1): [(14, 1), (13, 1), (12, 1)],
         (9, 2): [(9, 3), (10, 2), (9, 2), (8, 2)],
         (6, 1): [(7, 1), (6, 1), (5, 1)],
         (3, 1): [(4, 1), (3, 1)],
         (11, 3): [(12, 3), (11, 3), (10, 3)],
         (16, 1): [(16, 2), (16, 1), (15, 1)],
         (4, 3): [(5, 3), (4, 3), (3, 3)],
         (14, 3): [(14, 3), (13, 3)],
         (10, 2): [(10, 3), (10, 1), (10, 2), (9, 2)]}
        self.assertEqual(adjacency_target, bfs.adjacency)
        path_target = [(11, 3), (10, 3), (10, 2), (9, 2), (8, 2), (7, 2), (7,
            3), (6, 3), (5, 3), (4, 3), (3, 3), (2, 3), (1, 3), (1,2)]
        self.assertEqual(path_target, bfs.current_path)
        for i in range(len(path_target)):
            path_target.pop()
            game_master.play_round(i)
            self.assertEqual(path_target, bfs.current_path)
        game_master.play_round(i)
        self.assertEqual([(14, 3), (13, 3)], bfs.current_path)
        game_master.play_round(i+1)
        self.assertEqual([(14, 3)], bfs.current_path)
        game_master.play_round(i+2)
        self.assertEqual([], bfs.current_path)
