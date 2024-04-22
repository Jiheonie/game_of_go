from dlgo import goboard
from dlgo import gotypes
from dlgo.minimax import alphabeta
from dlgo.utils import print_board, print_move
import time

BOARD_SIZE = 5


# tag::naive-board-heuristic[]
def capture_diff(game_state):
  black_stones = 0
  white_stones = 0
  for r in range(1, game_state.board.num_rows + 1):
    for c in range(1, game_state.board.num_cols + 1):
      p = gotypes.Point(r, c)
      color = game_state.board.get(p)
      if color == gotypes.Player.black:
        black_stones += 1
      elif color == gotypes.Player.white:
        white_stones += 1
  diff = black_stones - white_stones                    # <1>
  if game_state.next_player == gotypes.Player.black:    # <2>
    return diff                                       # <2>
  return -1 * diff                                      # <3>
# end::naive-board-heuristic[]

def main():
  game = goboard.GameState.new_game(BOARD_SIZE)
  bots = {
    gotypes.Player.black: alphabeta.AlphaBetaAgent(3, capture_diff),
    gotypes.Player.white: alphabeta.AlphaBetaAgent(3, capture_diff),
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