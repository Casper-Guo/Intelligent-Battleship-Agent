# Game Play Implementation
import pandas as pd

from Battleship import *
from Battleship_data import *
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

clf = pickle.load(open("rf_classifier.sav", 'rb'))
indices = 'ABCDEFGHIJ'
names = ['Carrier', 'Battleship', 'Destroyer', 'Submarine', 'Patrol Boat']
sizes = [5, 4, 3, 3, 2]


def data_to_df(data):
    # convert data about a grid to a pandas df
    # fix sklearn throw warning when predicting data without column names

    return pd.DataFrame([data], columns=["dist_center", "adj_hit", "adj_miss", "diag_hit", "diag_miss"])


def find_grid_proba(Board, row, col):
    # calculate the probability score for a grid

    grid_data = collect_grid_data(Board, row, col)
    grid_proba = clf.predict_proba(data_to_df(grid_data))

    # grid_proba = (P[unoccupied], P[occupied])
    # use the second one
    Board.board[row][col].proba = grid_proba[0][1]

    return grid_proba[0][1]


def find_best_grid(Board):
    max_proba = 0
    max_row = 0
    max_col = 0

    for row in range(Board.dim):
        for col in range(Board.dim):
            if Board.board[row][col].hit:
                continue

            current_proba = find_grid_proba(Board, row, col)

            if current_proba > max_proba:
                max_proba = current_proba
                max_row = row
                max_col = col

    # fix edge case where all grids have near-zero probability score
    # default to the first grid that has not been hit
    if max_proba <= 0.01:
        for row in range(Board.dim):
            for col in range(Board.dim):
                if Board.board[row][col].hit:
                    return row, col

    return max_row, max_col


def random_exploratory_move(Board):
    # play a random move at the center of the board (not edge or corner)
    # only plays on a grid if none of its neighbors have been attempted (while such grid exist)
    # return move_row and move_col
    # (10, 10) return value means no valid move

    def check_neighbors(row, col):
        del_rows = [0, 1, -1]
        del_cols = [0, 1, -1]

        for del_row in del_rows:
            for del_col in del_cols:
                if not (del_row or del_col):
                    continue
                if Board.board[row + del_row][col + del_col].hit:
                    return True

        return False

    attempts = 0

    while True:

        # return no valid grid signal after 40 attempts
        if attempts >= 40:
            return 10, 10

        rng_row = random.randint(1, 8)
        rng_col = random.randint(1, 8)

        if Board.board[rng_row][rng_col].hit:
            continue

        if attempts > 20:
            Board.play_move(rng_row, rng_col, suppressed=True)
            break

        attempts += 1

        if check_neighbors(rng_row, rng_col):
            continue
        else:
            Board.play_move(rng_row, rng_col, suppressed=True)
            break

    return rng_row, rng_col


def random_edge_move(Board):
    # play a random move on the edges of the board
    # (10, 10) return value means no valid move

    edge_indices = [0, 9]
    deltas = {(0, 0): [(1, 0), (0, 1)], (0, 9): [(1, 0), (0, -1)], (9, 0): [(-1, 0), (0, 1)],
              (9, 9): [(-1, 0), (0, -1)]}

    def check_neighbors(row, col, orientation):
        # check immediately adjacent grids for hit
        # return True means some neighbor is hit

        if (row, col) in deltas:
            check_deltas = deltas[(row, col)]
            for check_delta in check_deltas:
                del_row, del_col = check_delta
                if Board.board[row + del_row][col + del_col].hit:
                    return True
            return False
        else:
            if orientation == 0:
                if Board.board[row][col - 1].hit or Board.board[row][col + 1].hit:
                    return True
            elif orientation == 1:
                if Board.board[row - 1][col].hit or Board.board[row + 1][col].hit:
                    return True
            return False

    # 0 is for horizontal edges, 1 is for vertical edges
    attempts = 0
    while True:
        if attempts >= 40:
            return 10, 10

        rng_orientation = random.randint(0, 1)

        if rng_orientation == 0:
            rng_row = edge_indices[random.randint(0, 1)]
            rng_col = random.randint(0, 9)
        else:
            rng_row = random.randint(0, 9)
            rng_col = edge_indices[random.randint(0, 1)]

        attempts += 1

        if check_neighbors(rng_row, rng_col, rng_orientation):
            continue
        else:
            Board.play_move(rng_row, rng_col, suppressed=True)
            break

    return rng_row, rng_col


def color_map(Board, color="viridis"):
    cmap = np.array([[Board.board[row][col].proba for col in range(10)] for row in range(10)])
    ax = sns.heatmap(cmap, cmap=color)
    plt.show()

    return


def check_grid_input(grid_in):
    # return true if the grid input is valid
    # return false otherwise

    if len(grid_in) < 2:
        return False
    return grid_in[0].upper() in indices and grid_in[1].upper() in indices


def check_orientation_input(orientation_in):
    # return true if the orientation input is valid
    # return false otherwise

    if len(orientation_in) < 1:
        return False
    return orientation_in[0] == '0' or orientation_in[0] == '1'


def get_player_placement():
    # reject invalid player placement requests
    # return a valid set of placement instructions
    # (row, col, orientation)

    grid_in = input("Enter the starting coordinate of your ship (the ship extends downwards or rightwards): ")

    while not check_grid_input(grid_in):
        print("Please enter a valid coordinate")
        grid_in = input("Enter the starting coordinate of your ship (the ship extends downwards or rightwards): ")

    row_in = indices.find(grid_in[0].upper())
    col_in = indices.find(grid_in[1].upper())

    orientation_in = input("Enter 0 for horizontal orientation, enter 1 for vertical orientation: ")

    while not check_orientation_input(orientation_in):
        print("Enter either 0 or 1 for your ship orientation")
        orientation_in = input("Enter 0 for horizontal orientation, enter 1 for vertical orientation: ")

    orientation_in = int(orientation_in[0])

    return row_in, col_in, orientation_in


def init_player_board():
    print("Welcome to Battleship!")
    username = input("Choose a in-game name for yourself: ").upper()
    num_placed = 0
    player_board = Board(name=username)
    print(player_board)

    while num_placed < 5:
        print("Choose where to place the {boat} (size:{size})".format(
            boat=names[num_placed] + '(' + names[num_placed][0] + ')',
            size=sizes[num_placed]))

        row_in, col_in, orientation_in = get_player_placement()

        if not player_board.check_placement_valid(row_in, col_in, sizes[num_placed], orientation_in):
            print("The placement you have requested is illegal!")
            continue
        else:
            player_board.place_ship(row_in, col_in, sizes[num_placed], orientation_in, names[num_placed][0])
            num_placed += 1
            player_board.reveal_board()

    return player_board


def init_AI_board():
    AI_board = Board(name="AI")
    AI_board.place_by_rng()
    return AI_board


def player_turn(AI_board):
    # rejects invalid player move requests
    # return the last valid player move

    while True:
        grid_in = input("Enter the coordinate you want to fire upon: ")

        while not check_grid_input(grid_in):
            print("Please enter a valid coordinate")
            grid_in = input("Enter the coordinate you want to fire upon: ")

        row_in = indices.find(grid_in[0].upper())
        col_in = indices.find(grid_in[1].upper())

        if AI_board.board[row_in][col_in].hit:
            print("You have attempted this coordinate already!")
            continue

        AI_board.play_move(row_in, col_in, suppressed=False)

        if AI_board.check_game_end(suppressed=True):
            break

        if AI_board.board[row_in][col_in].occupied:
            print("\n" + "AI's board:")
            print(AI_board)
        else:
            # the player didn't hit a target on his last attempt
            # the player's turn is over
            # exit the function
            break

    return grid_in


def AI_turn(miss_counter, player_board):
    # return (row, col, rng_mode, proba) that describes the AI's move

    rng_mode = ""
    row, col = find_best_grid(player_board)

    # two dummy variables to save the optimal choice
    best_row, best_col = row, col
    proba = round(player_board.board[row][col].proba, 3)

    if proba >= 0.25 or miss_counter <= 5 or miss_counter > 30 or 25 >= miss_counter > 20:
        player_board.play_move(row, col, suppressed=True)
    elif (20 >= miss_counter > 15 and proba < 0.23) or 30 >= miss_counter > 25:
        row, col = random_edge_move(player_board)
        rng_mode = "random edge move"
    elif 20 >= miss_counter > 5 and proba < 0.25:
        row, col = random_exploratory_move(player_board)
        rng_mode = "random exploratory move"

    if row == 10 and col == 10:
        row, col = best_row, best_col
        rng_mode = ""
        player_board.play_move(best_row, best_col, suppressed=True)
    
    return row, col, rng_mode, proba


def play_game(player_board, AI_board):
    miss_counter = 0
    AI_move_counter = 0
    player_move_counter = 0
    best_probas = []
    # AI_board.reveal_board()

    while not (player_board.check_game_end(suppressed=True) or AI_board.check_game_end(suppressed=True)):

        print("\n" + "-" * 20 + player_board.name + "'S TURN" + "-" * 20 + "\n")
        print("Your board:")
        player_board.reveal_board()
        print("AI's board:")
        print(AI_board)

        player_move = player_turn(AI_board)
        player_move_counter += 1

        if AI_board.check_game_end(suppressed=True):
            # if the game is over after the player's turn
            # exit the while loop
            break

        print("\n" + "-" * 20 + "AI'S TURN" + "-" * 20 + "\n")

        while True:
            
            AI_row, AI_col, rng_mode, current_proba = AI_turn(miss_counter, player_board)
            best_probas.append(current_proba)

            AI_move_counter += 1

            if player_board.board[AI_row][AI_col].occupied:
                # set a high proba for cmap
                player_board.board[AI_row][AI_col].proba = 0.600

                if not rng_mode:
                    print("The AI played at {row}{col} with best proba={proba}. Target Hit!".format(row=indices[AI_row],
                                                                                                    col=indices[AI_col],
                                                                                                    proba=current_proba))
                else:
                    print("The AI entered {random} and played at {row}{col}. Target Hit!".format(random=rng_mode,
                                                                                                 row=indices[AI_row],
                                                                                                 col=indices[AI_col]))
            else:
                # set proba to 0 for cmap
                player_board.board[AI_row][AI_col].proba = 0.000

                if not rng_mode:
                    print("The AI played at {row}{col} with best proba={proba}. Target Missed!".format(
                        row=indices[AI_row],
                        col=indices[AI_col],
                        proba=current_proba))
                else:
                    print("The AI entered {random} and played at {row}{col}. Target Missed!".format(random=rng_mode,
                                                                                                    row=indices[AI_row],
                                                                                                    col=indices[
                                                                                                        AI_col]))
                miss_counter += 1

                # AI doesn't hit a target on this attempt
                # The AI's turn is over
                break

            if player_move[-1].upper() == "M":
                color_map(player_board)

            if player_board.check_game_end(suppressed=True):
                # if the AI scores the game-winning hit
                # exit the while loop

                break

    if player_board.check_game_end(suppressed=False):
        print("You are defeated by my all-too-powerful AI in {num} turns!\n".format(num=AI_move_counter))
        print("This was the AI's board:")
        AI_board.reveal_board()
    elif AI_board.check_game_end(suppressed=False):
        print("Impossible, you have defeated the AI overlord in {num} turns!".format(num=player_move_counter))

    return


def autoplay(show_map=None, suppressed=False):
    if show_map is None:
        show_map = []

    AI_board = Board()
    AI_board.place_by_rng()

    if not suppressed:
        AI_board.reveal_board()

    move_counter = 0
    miss_counter = 0
    all_probas = []
    recent_probas = []

    while not AI_board.check_game_end(suppressed=True):
        AI_row, AI_col = find_best_grid(AI_board)

        best_row, best_col = AI_row, AI_col

        current_proba = round(AI_board.board[AI_row][AI_col].proba, 3)
        all_probas.append(current_proba)
        recent_probas.append(current_proba)

        if current_proba >= 0.25 or miss_counter <= 10 or miss_counter > 35 or 25 >= miss_counter > 20:
            AI_board.play_move(AI_row, AI_col, suppressed=True)
        elif (20 >= miss_counter > 15 and current_proba < 0.23) or 35 >= miss_counter > 25:
            AI_row, AI_col = random_edge_move(AI_board)
        elif 20 >= miss_counter > 10 and current_proba < 0.25:
            AI_row, AI_col = random_exploratory_move(AI_board)

        if AI_row == 10 and AI_col == 10:
            AI_row, AI_col = best_row, best_col
            AI_board.play_move(best_row, best_col, suppressed=True)

        if not AI_board.board[AI_row][AI_col].occupied:
            AI_board.board[AI_row][AI_col].proba = 0
            miss_counter += 1
        else:
            AI_board.board[AI_row][AI_col].proba = 0.600

        if move_counter in show_map:
            AI_board.reveal_board()
            print(recent_probas)
            recent_probas.clear()
            color_map(AI_board)

        move_counter += 1

        if not suppressed:
            print(move_counter)

    print("Finished game in " + str(move_counter) + " moves")
    # print(all_probas)
    print(sum(all_probas) / len(all_probas))

    return move_counter


def selfplay_viz():
    AI = init_AI_board()

    step_size = int(input("Stepsize: "))
    show_viz = [i*step_size for i in range(1, 100//step_size + 1)]

    move_counter = 0
    miss_counter = 0
    all_probas = []
    recent_probas = []

    AI.reveal_board()

    while not AI.check_game_end():
        AI_row, AI_col = find_best_grid(AI)
        current_proba = round(AI.board[AI_row][AI_col].proba, 3)
        all_probas.append(current_proba)
        recent_probas.append(current_proba)

        print("The agent played on row ", AI_row, " col ", AI_col)
        AI.play_move(AI_row, AI_col, suppressed=False)

        if not AI.board[AI_row][AI_col].occupied:
            AI.board[AI_row][AI_col].proba = 0.000
            miss_counter += 1
        else:
            AI.board[AI_row][AI_col].proba = 0.600

        move_counter += 1

        if move_counter in show_viz:
            AI.reveal_board()
            print(recent_probas)
            recent_probas.clear()
            color_map(AI)

    print("Finished game in " + str(move_counter) + " moves")
    print(sum(all_probas) / len(all_probas))

    color_map(AI)

    return


if __name__ == "__main__":
    selfplay_viz()
