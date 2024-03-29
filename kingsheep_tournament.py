"""
Kingsheep

A simple adverserial game based on the Java version https://github.com/uzh/PAI-Kingsheep.

Version: 0.1

Date: 2.1.2019

Authors:
    - Abraham Bernstein
    - Suzanne Tolmeijer

License: (c) By University of Zurich, Dynamic and Distributed Systems Group ddis.ch
         All rights reserved

"""

import copy
import argparse
import importlib
import random
import time
import configparser
import os.path
from config import *
from multiprocessing import Pool, TimeoutError


# --- CLASSES ---

class KsField:
    """Implements a Kingsheep Game Field"""

    def __init__(self, filepath):
        # initialize the field with empty cells.
        self.field = [[CELL_EMPTY for x in range(FIELD_WIDTH)] for y in range(FIELD_HEIGHT)]
        self.read_field(filepath)
        self.score1 = 0
        self.score2 = 0
        self.grading1 = 0
        self.grading2 = 0
        self.name1 = 'Player 1'
        self.name2 = 'Player 2'
        self.verbosity = 1000

    # Field related functions

    def read_field(self, fp):
        file = open(fp, 'r')
        for lineno, line in enumerate(file, 1):
            # turn the line into a string, strip the tangling \n and then assign it to the field variable
            self.field[lineno - 1] = list(str(line).strip('\n'))

    def get_field(self):
        return copy.deepcopy(self.field)

    def print_ks(self):
        if verbosity > 3:
            i = -1
            for line in self.field:
                i = i + 1
                # print('{:2d}  {}'.format(i, ''.join(line)))
            # print('    0123456789012345678')

        # if verbosity > 0:
        # print('Scores: {}: {:3d}   {}: {:3d}'.format(self.name1, self.score1, self.name2, self.score2))

    # Movement

    def get_position(self, figure):
        # Next statement is a list comprehension.
        # it first generated a list of all x's in self. field, where figure is in that particular x
        # it then returns the first element (which is the row that contaions the figure),
        # as we know that there is only one of each of these figures
        x = [x for x in self.field if figure in x][0]
        return (self.field.index(x), x.index(figure))

    def new_position(self, x_old, y_old, move):
        if move == MOVE_LEFT:
            return (x_old, y_old - 1)
        elif move == MOVE_RIGHT:
            return (x_old, y_old + 1)
        elif move == MOVE_UP:
            return (x_old - 1, y_old)
        elif move == MOVE_DOWN:
            return (x_old + 1, y_old)

    def valid(self, figure, x_new, y_new):
        # Rule book valid moves

        # Neither the sheep nor the wolf, can step on a square outside the map. Imagine the map is surrounded by fences.
        if x_new > FIELD_HEIGHT - 1:
            return False
        elif x_new < 0:
            return False
        elif y_new > FIELD_WIDTH - 1:
            return False
        elif y_new < 0:
            return False

        # Neither the sheep nor the wolf, can enter a square with a fence on.
        if self.field[x_new][y_new] == CELL_FENCE:
            return False

        # Wolfs can not step on squares occupied by the opponents wolf (wolfs block each other).
        # Wolfs can not step on squares occupied by the sheep of the same player .
        if figure == CELL_WOLF_1:
            if self.field[x_new][y_new] == CELL_WOLF_2:
                return False
            elif self.field[x_new][y_new] == CELL_SHEEP_1:
                return False
        elif figure == CELL_WOLF_2:
            if self.field[x_new][y_new] == CELL_WOLF_1:
                return False
            elif self.field[x_new][y_new] == CELL_SHEEP_2:
                return False

        # Sheep can not step on squares occupied by the wolf of the same player.
        # Sheep can not step on squares occupied by the opposite sheep.
        if figure == CELL_SHEEP_1:
            if self.field[x_new][y_new] == CELL_SHEEP_2 or \
                    self.field[x_new][y_new] == CELL_WOLF_1:
                return False
        elif figure == CELL_SHEEP_2:
            if self.field[x_new][y_new] == CELL_SHEEP_1 or \
                    self.field[x_new][y_new] == CELL_WOLF_2:
                return False

        return True

    def award(self, figure):
        if figure == CELL_RHUBARB:
            return AWARD_RHUBARB
        elif figure == CELL_GRASS:
            return AWARD_GRASS
        else:
            return 0

    def move(self, figure, move, reason):
        if move != MOVE_NONE:
            (x_old, y_old) = self.get_position(figure)
            (x_new, y_new) = self.new_position(x_old, y_old, move)

            if self.valid(figure, x_new, y_new):
                target_figure = self.field[x_new][y_new]

                # wolf of player1 catches the sheep of player2 the game ends immediately and player1 wins and
                # is awarded all the points for the current run and vice versa

                # If the sheep steps on a food object, the food object is consumed (removed from the map) and a score
                # is awarded.

                if figure == CELL_SHEEP_1:
                    if target_figure == CELL_WOLF_2:
                        self.field[x_old][y_old] = CELL_SHEEP_1_d
                        self.score2 += self.score1
                        self.score1 = 0
                        return True, 'sheep1 suicide'
                    else:
                        self.score1 += self.award(target_figure)

                elif figure == CELL_SHEEP_2:
                    if target_figure == CELL_WOLF_1:
                        self.field[x_old][y_old] = CELL_SHEEP_2_d
                        self.score1 += self.score2
                        self.score2 = 0
                        return True, 'sheep2 suicide'
                    else:
                        self.score2 += self.award(target_figure)

                # If the wolf steps on a food object, the food object gets removed but no score is awarded.

                elif figure == CELL_WOLF_1:
                    if target_figure == CELL_SHEEP_2:
                        self.field[x_new][y_new] = CELL_SHEEP_2_d
                        self.score1 += self.score2
                        self.score2 = 0
                        return True, 'sheep1 eaten'

                elif figure == CELL_WOLF_2:
                    if target_figure == CELL_SHEEP_1:
                        self.field[x_new][y_new] = CELL_SHEEP_1_d
                        self.score2 += self.score1
                        self.score1 = 0
                        return True, 'sheep2 eaten'

                # actual figure move
                self.field[x_new][y_new] = figure
                self.field[x_old][y_old] = CELL_EMPTY
                return False, reason

            else:  # if move is not valid
                return False, reason

        else:  # if move = none
            return False, reason


#   --- GAME PLAY ---   ----------------------------

def kingsheep_iteration(i, ks, player1, player2, reason):
    game_over = False

    # each move is placed in a pool to limit the think time the agent gets

    # sheep1 move
    p1 = Pool()
    r1 = p1.apply_async(player1.move_sheep, (1, ks.get_field()))
    try:
        if ks.name1 == 'Keyboard Player':
            move1 = player1.move_sheep()
        else:
            move1 = r1.get(MAX_CALC_TIME)
        result1_game_over, result1_reason = ks.move(CELL_SHEEP_1, move1, reason)
        if result1_reason != '':
            reason = result1_reason
        game_over = game_over or result1_game_over
    except TimeoutError:
        game_over = True
        reason = 'timeout1'
    p1.close()
    p1.terminate()
    p1.join()

    # sheep2 move
    p2 = Pool()
    r2 = p2.apply_async(player2.move_sheep, (2, ks.get_field()))
    try:
        if ks.name2 == 'Keyboard Player':
            move2 = player2.move_sheep()
        else:
            move2 = r2.get(MAX_CALC_TIME)
        result2_game_over, result2_reason = ks.move(CELL_SHEEP_2, move2, reason)
        if result2_reason != '':
            reason = result2_reason
        game_over = game_over or result2_game_over
    except TimeoutError:
        game_over = True
        reason = 'timeout2'
    p2.close()
    p2.terminate()
    p2.join()

    if i % 2 == 0 and not game_over:
        # wolf1 move
        p3 = Pool()
        r3 = p3.apply_async(player1.move_wolf, (1, ks.get_field()))
        try:
            if ks.name1 == 'Keyboard Player':
                move3 = player1.move_wolf()
            else:
                move3 = r3.get(MAX_CALC_TIME)
            result3_game_over, result3_reason = ks.move(CELL_WOLF_1, move3, reason)
            if result3_reason != '':
                reason = result3_reason
            game_over = game_over or result3_game_over
        except TimeoutError:
            game_over = True
            reason = 'timeout1'
        p3.close()
        p3.terminate()
        p3.join()

        # wolf2 move
        p4 = Pool()
        r4 = p4.apply_async(player2.move_wolf, (2, ks.get_field()))
        try:
            if ks.name2 == 'Keyboard Player':
                move4 = player2.move_wolf()
            else:
                move4 = r4.get(MAX_CALC_TIME)
            result4_game_over, result4_reason = ks.move(CELL_WOLF_2, move4, reason)
            if result4_reason != '':
                reason = result4_reason
            game_over = game_over or result4_game_over
        except TimeoutError:
            game_over = True
            reason = 'timeout2'
        p4.close()
        p4.terminate()
        p4.join()

    if debug:
        # print("\nIteration " + str(i) + " of " + str(NO_ITERATIONS))
        ks.print_ks()
        time.sleep(slowdown)

    return game_over, reason


def kingsheep_play(player1class, player2class, map_name):
    """ Main method """

    #   --- SET UP GAME ---

    # if verbosity > 2:
    # print('\n >>> Starting up Kingsheep\n')

    # init field

    ks = KsField(map_name)
    player1 = player1class()
    player2 = player2class()

    ks.name1 = player1.name
    ks.name2 = player2.name

    ks.verbosity = verbosity

    #   --- PLAY GAME ---

    start_time = time.perf_counter()
    reason = ''

    if graphics:
        import ksgraphics
        ksgraphics.init(NO_ITERATIONS, FIELD_WIDTH, FIELD_HEIGHT, ks, player1, player2, debug, verbosity, slowdown)

    else:
        iterations_run = 0
        for i in range(1, NO_ITERATIONS + 1):
            game_over, reason = kingsheep_iteration(i, ks, player1, player2, reason)

            iterations_run += 1
            if game_over:
                break

    #   --- END GAME ---

    elapsed_time = time.perf_counter() - start_time

    if ks.score1 == ks.score2:
        ks.grading1 = 0.5
        ks.grading2 = 0.5
    elif ks.score1 > ks.score2:
        ks.grading1 = 0.1 + round((0.9 * ks.score1 / (ks.score1 + ks.score2)), 3)
        ks.grading2 = 0 + round((0.9 * ks.score2 / (ks.score1 + ks.score2)), 3)
    else:
        ks.grading1 = 0 + round((0.9 * ks.score1 / (ks.score1 + ks.score2)), 3)
        ks.grading2 = 0.1 + round((0.9 * ks.score2 / (ks.score1 + ks.score2)), 3)

    print('' + map_name + ',' + str(round(ks.grading1, 2)) + ',' + str(round(ks.grading2, 2)))


# --- GLOBAL VARIABLES ----

debug = False
verbosity = 5
graphics = False
slowdown = 0.0


def main():
    # command line: -p1m ksplayers -p1n PassivePlayer -p2m ksplayers -p2n KingsheepPlayer

    global debug
    global verbosity
    global graphics
    global slowdown

    parser = argparse.ArgumentParser(description="Run the Kingsheep Game")
    parser.add_argument("-d", "--debug", help="turn on debug mode", action="store_true")
    parser.add_argument("-v", "--verbosity", type=int,
                        help="verbosity of the output (1: elapsed time, 2: system messages, 3: ending board")

    parser.add_argument("-p1m", "--player1module", help="name of module that defines player 1")
    parser.add_argument("-p1n", "--player1name", help="name of class that defines player 1")

    parser.add_argument("-p2m", "--player2module", help="name of module that defines player 2")
    parser.add_argument("-p2n", "--player2name", help="name of class that defines player 2")

    parser.add_argument("-g", "--graphics", help="turn on graphics based on arcade (http://arcade.academy/index.html)",
                        action="store_true")

    parser.add_argument("-s", "--slowdown", type=float,
                        help="slowdown in each iteration in seconds (fractions allowed")

    parser.add_argument("map", help="map file")

    args = parser.parse_args()
    if args.debug:
        debug = True

    if args.verbosity:
        verbosity = args.verbosity

    if args.slowdown:
        slowdown = args.slowdown

    if args.player1module:
        mod1 = importlib.import_module(args.player1module)
    else:
        mod1 = importlib.import_module("random_player")

    if args.player1name:
        player1class = getattr(mod1, args.player1name)
    else:
        player1class = getattr(mod1, "RandomPlayer")

    if args.player2module:
        mod2 = importlib.import_module(args.player2module)
    else:
        mod2 = importlib.import_module("random_player")

    if args.player2name:
        player2class = getattr(mod2, args.player2name)
    else:
        player2class = getattr(mod2, "RandomPlayer")

    if args.graphics:
        graphics = True

    if args.map:
        map_name = args.map
    else:
        map_name = "resources/test.map"

    try:
        kingsheep_play(player1class, player2class, map_name)
    except Exception as ex:
        print('' + map_name + ',0,0,Exception: [' + str(ex) + ']')


if __name__ == "__main__":
    main()
