#!/usr/bin/python3
from util import memorywatcher, paths, gamestate, controller, enums, logger
from goals import choosecharacter, killopponent, skippostgame

import argparse
import globals
import signal
import sys

goal = None

parser = argparse.ArgumentParser(description='SmashBot: The AI that beats you at Melee')
parser.add_argument('--port', '-p', type=int,
                    help='The controller port SmashBot will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=int,
                    help='The controller port the human will play on',
                    default=1)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game state')

args = parser.parse_args()

#Setup some config files before we can really play
paths.first_time_setup()
paths.configure_controller_settings(args.port)
globals.init(args.port, args.opponent)
log = globals.log

def signal_handler(signal, frame):
        log.writelog()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
        sys.exit(0)

def creategoal(new_goal):
    global goal
    if goal == None:
        goal = new_goal()
    if type(goal) !=  new_goal:
        goal = new_goal()

if args.debug:
    signal.signal(signal.SIGINT, signal_handler)

memory_watcher = memorywatcher.MemoryWatcher()

game_state = globals.gamestate
controller = globals.controller

#"Main loop" of SmashBot, process memory updates until the frame has incremented
for mem_update in memory_watcher:
    #If the frame counter has updated, then process it!
    if game_state.update(mem_update):
        if game_state.menu_state == enums.Menu.IN_GAME:
            creategoal(killopponent.KillOpponent)
            goal.pickstrategy()
        elif game_state.menu_state == enums.Menu.CHARACTER_SELECT:
            creategoal(choosecharacter.ChooseCharacter)
            goal.pickstrategy()
        elif game_state.menu_state == enums.Menu.POSTGAME_SCORES:
            creategoal(skippostgame.SkipPostgame)
            goal.pickstrategy()
        #Flush and button presses queued up
        controller.flush()
        if args.debug:
            log.logframe()
            log.writeframe()
