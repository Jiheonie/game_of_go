from dlgo import goboard
from dlgo import gotypes
from dlgo.mcts import mcts
from dlgo.utils import print_board, print_move
import time

BOARD_SIZE = 5


def main():
  game = goboard.GameState.new_game(BOARD_SIZE)
  bots = {
    gotypes.Player.black: mcts.MCTSAgent(500, temperature=1.4),
    gotypes.Player.white: mcts.MCTSAgent(500, temperature=1.4),
  }

  step = 0
  while not game.is_over():
    time.sleep(0.3)

    print(chr(27) + "[2J")
    print_board(game.board)
    print(step)
    bot_move = bots[game.next_player].select_move(game)
    step += 1
    print_move(game.next_player, bot_move)
    game = game.apply_move(bot_move)

  print(game.winner())


if __name__ == '__main__':
  main()