import numpy as np
import socket
import threading
from dlgo.agent import naive
from dlgo.gotypes import Player, Point
from dlgo.goboard import GameState, Board, Move
from dlgo.encoders.base import get_encoder_by_name

features_data = np.load('./test_data/features-40k.npy')
print(features_data[1])
labels_data = np.load('./test_data/labels-40k.npy')

encoder = get_encoder_by_name('oneplane', 9)
rand_bot = naive.RandomBot()

HEADER = 2048
PORT = 5051
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"

conns = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
  print(f"[New Connection] {addr} connected.")

  connected = True
  while connected:
    msg = conn.recv(HEADER).decode(FORMAT)
    if msg:
      if msg == DISCONNECT_MSG:
        connected = False

      print(f"[{addr}] {msg}")

      msg = eval(msg)

      state, move = decode_msg(msg)

      if state.is_valid_move(move):
        # send back to client: "valide move"
        print("VALID")
        # conn.send("VALID".encode(FORMAT))

        # Search in features.npy
        state = state.apply_move(move)
        board = encoder.encode(state)
        idx = -1
        bot_move = None
        for i in range(len(features_data)):
          comparision = features_data[i] == board
          if comparision.all():
            idx = i

        # find next move in labels.npy
        if idx != -1:
          bot_move = labels_data[idx]
          # apply found move
          point = encoder.decode_point_index(find_point(bot_move))
          bot_decoded_move = Move.play(point)
          state = state.apply_move(bot_decoded_move)

          # send bot move
          print(encoder.encode(state))
          # conn.send(str(encoder.encode(bot_state)).encode(FORMAT))

        else:
          # apply random
          bot_move_rand = rand_bot.select_move(state)
          state = state.apply_move(bot_move_rand)
          print(encoder.encode(state))
          # conn.send(str(encoder.encode(state)).encode(FORMAT))

      else:
        # send to client: "unvalid move"
        print("UNVALID")
        # conn.send("UNVALID".encode(FORMAT))

  conn.close()

def decode_board(encoded_board, next_player):
  board = np.array(encoded_board)
  if next_player == Player.black:
    for r in range(9):
      for c in range(9):
        if board[r, c] == 1:
          board[r, c] = Player.black
        elif board[r, c] == -1:
          board[r, c] = Player.white 
  else:
    for r in range(9):
      for c in range(9):
        if board[r, c] == 1:
          board[r, c] = Player.white
        elif board[r, c] == -1:
          board[r, c] = Player.black 
  return board

def find_point(move):
  for i in range(len(move)):
    if move[i] == 1:
      return i
  return None

""" 
{
  states: 
    [
      (list của tất cả trạng thái từ lúc bắt đầu)
      {
        board: [list điểm trong bảng],
        last_move: nước đi trước đó 
      }
    ], 
  move: nước đi muốn thực hiện (ở dạng one hot encode)
} 
"""
def decode_msg(msg):
  states = msg["states"]
  final_state = None
  next_player = Player.black
  for s in states:
    board_grid = s["board"]
    board_grid = decode_board(board_grid, next_player)
    board = Board(9, 9, board_grid)

    last_move = s["last_move"]
    p = None
    count = 0
    for i in range(len(last_move)):
      if last_move[i] != 0:
        p = encoder.decode_point_index(i)
      else: 
        count += 1

    move = None
    if count < len(last_move):
      move = Move.play(p)

    final_state = GameState(board, next_player, final_state, move)

    next_player = next_player.other

  next_move = msg["move"]
  decoded_move = encoder.decode_point_index(find_point(next_move))
  next_move = Move.play(decoded_move)

  return final_state, next_move


def start():
  server.listen()
  print(f"[Listening] Server is listening on {SERVER}")
  while True:
    conn, addr = server.accept()
    conns.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[Active connections] {threading.active_count() - 1}")

print("[Starting] Server is starting...")
start()