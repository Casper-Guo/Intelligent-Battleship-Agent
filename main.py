# Game Play Implementation

from Battleship import *
from Battleship_data import *
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

clf = pickle.load(open("rf_classifier.sav", 'rb'))
indices = 'ABCDEFGHIJKLMN'
names = ['Carrier', 'Battleship', 'Destroyer', 'Submarine', 'Patrol Boat']
sizes = [5, 4, 3, 3, 2]


def find_grid_proba(Board, row, col):
    grid_data = collect_grid_data(Board, row, col)
    grid_proba = clf.predict_proba(np.array(grid_data).reshape(1,-1))
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

    return max_row, max_col


def random_exploratory_move(Board):
    # return move_row and move_col

    def check_neighbors(row, col):
        del_rows = [0,1,-1]
        del_cols = [0,1,-1]

        for del_row in del_rows:
            for del_col in del_cols:
                if not (del_row or del_col):
                    continue
                if Board.board[row+del_row][col+del_col].hit:
                    return True

        return False

    attempts = 0
    while True:

        rng_row = random.randint(1,8)
        rng_col = random.randint(1,8)

        if attempts > 10 and not Board.board[rng_row][rng_col].hit:
            Board.play_move(rng_row, rng_col, suppressed=True)
            break

        attempts += 1

        if attempts > 40:
            return 10, 10

        if Board.board[rng_row][rng_col].hit:
            continue
        elif check_neighbors(rng_row, rng_col):
            continue
        else:
            Board.play_move(rng_row, rng_col, suppressed=True)
            break

    return rng_row, rng_col


def random_edge_move(Board):
    edge_indices = [0, 9]
    deltas = {(0,0):[(1,0), (0,1)], (0,9):[(1,0), (0,-1)], (9,0):[(-1,0), (0,1)], (9,9):[(-1,0), (0,-1)]}

    def check_neighbors(row, col, orientation):
        # check immediate adjacent grids for hit
        # return True means some neighbor is hit
        if (row, col) in deltas:
            check_deltas = deltas[(row, col)]
            for check_delta in check_deltas:
                del_row, del_col = check_delta
                if Board.board[row+del_row][col+del_col].hit:
                    return True
            return False
        else:
            if orientation == 0:
                if Board.board[row][col-1].hit or Board.board[row][col+1].hit:
                    return True
            elif orientation == 1:
                if Board.board[row-1][col].hit or Board.board[row+1][col].hit:
                    return True
            return False

    # 0 is for horizontal edges,1 is for vertical edges
    attempts = 0
    while True:
        rng_orientation = random.randint(0,1)

        if rng_orientation == 0:
            rng_row = edge_indices[random.randint(0, 1)]
            rng_col = random.randint(0, 9)
        else:
            rng_row = random.randint(0, 9)
            rng_col = edge_indices[random.randint(0,1)]

        attempts += 1

        if attempts >= 40:
            return 10, 10

        if Board.board[rng_row][rng_col].hit:
            continue
        elif check_neighbors(rng_row, rng_col, rng_orientation):
            continue
        else:
            Board.play_move(rng_row, rng_col, suppressed=True)
            break
    return rng_row, rng_col


def color_map(Board, color="viridis"):
    map = np.array([[Board.board[row][col].proba for col in range(10)] for row in range(10)])
    ax = sns.heatmap(map, cmap=color)
    plt.show()
    return None


def init_player_board():
    print("Welcome to Battleship!")
    username = input("Choose a in-game name for yourself: ").upper()
    num_placed = 0
    player_board = Board(name=username)
    print(player_board)

    while num_placed < 5:
        print("Choose where to place the {boat} (size:{size})".format(boat=names[num_placed]+'('+names[num_placed][0]+')',
                                                                size=sizes[num_placed]))
        grid_in = input("Enter the starting coordinate of your ship (the ship extends downwards or rightwards): ")

        try:
            row_in = indices.find(grid_in[0].upper())
            col_in = indices.find(grid_in[1].upper())
        except IndexError:
            print("Enter a valid coordinate")
            continue

        if row_in == -1 or col_in == -1:
            print("The index you have entered is out of bounds!")
            continue

        try:
            orientation_in = int(input("Enter 0 for horizontal orientation, enter 1 for vertical orientation: ")[0])
        except ValueError:
            print("Enter either 0 or 1 for your ship orientation")
            continue

        if not player_board.check_placement_valid(row_in, col_in, sizes[num_placed], orientation_in):
            print("The placement you have requested is illegal!")
            continue
        else:
            player_board.place_ship(row_in, col_in, sizes[num_placed], orientation_in, names[num_placed][0], rng=False)
            num_placed += 1
            player_board.reveal_board()

    return player_board


def init_ai_board():
    ai_board = Board(name="AI")
    ai_board.place_by_rng()
    return ai_board


def play_game(player_board, ai_board):
    miss_counter = 0
    ai_move_counter = 0
    player_move_counter = 0
    best_probas = []
    ai_board.reveal_board()

    while not (player_board.check_game_end(suppressed=True) or ai_board.check_game_end(suppressed=True)):

        print("\n" + "-"*20 + player_board.name + "'S TURN" + "-"*20 + "\n")
        # print(player_board.check_game_end(suppressed=False))
        print("Your board:")
        player_board.reveal_board()
        print("AI's board:")
        print(ai_board)

        while True:
            grid_in = input("Enter the coordinate you want to fire upon: ")
            row_in = indices.find(grid_in[0].upper())
            col_in = indices.find(grid_in[1].upper())

            if row_in == -1 or col_in == -1:
                print("The index you have entered is out of bounds!")
                continue

            if ai_board.board[row_in][col_in].hit:
                print("You have attempted this coordinate already!")
                continue

            ai_board.play_move(row_in, col_in, suppressed=False)
            player_move_counter += 1

            if ai_board.check_game_end(suppressed=True):
                break

            if ai_board.board[row_in][col_in].occupied:
                print("\n" + "AI's board:")
                print(ai_board)
                continue
            else:
                break

        if ai_board.check_game_end(suppressed=True):
            break

        print("\n" + "-"*20 + "AI'S TURN" + "-"*20 + "\n")
        while True:
            rng = ""
            ai_row, ai_col = find_best_grid(player_board)

            # two dummy variables to save the optimal choice
            best_row, best_col = ai_row, ai_col
            current_proba = round(player_board.board[ai_row][ai_col].proba, 3)
            best_probas.append(current_proba)

            if current_proba >= 0.25 or miss_counter <= 5 or miss_counter > 30 or 25 >= miss_counter > 20:
                player_board.play_move(ai_row, ai_col, suppressed=True)
            elif (20 >= miss_counter > 15 and current_proba < 0.23) or 30 >= miss_counter > 25:
                ai_row, ai_col = random_edge_move(player_board)
                rng = "random edge move"
            elif 20 >= miss_counter > 5 and current_proba < 0.25:
                ai_row, ai_col = random_exploratory_move(player_board)
                rng = "random exploratory move"

            if ai_row == 10 and ai_col == 10:
                ai_row, ai_col = best_row, best_col
                rng = ""
                player_board.play_move(best_row, best_col, suppressed=True)

            ai_move_counter += 1

            # player_board.play_move(ai_row, ai_col, suppressed=True)
            # player_board.print_proba()

            if player_board.board[ai_row][ai_col].occupied:
                player_board.board[ai_row][ai_col].proba = 0.600

                if not rng:
                    print("The AI played at {row}{col} with best proba={proba}. Target Hit!".format(row=indices[ai_row],
                                                                                               col=indices[ai_col],
                                                                                               proba=current_proba))
                else:
                    print("The AI entered {random} and played at {row}{col}. Target Hit!".format(random=rng,
                                                                                                 row=indices[ai_row],
                                                                                                 col=indices[ai_col]))
                if grid_in[-1].upper() == "M":
                    color_map(player_board)

                if player_board.check_game_end(suppressed=True):
                    break
            else:
                player_board.board[ai_row][ai_col].proba = 0.000

                if not rng:
                    print("The AI played at {row}{col} with best proba={proba}. Target Missed!".format(row=indices[ai_row],
                                                                                                  col=indices[ai_col],
                                                                                                  proba=current_proba))
                else:
                    print("The AI entered {random} and played at {row}{col}. Target Missed!".format(random=rng,
                                                                                                    row=indices[ai_row],
                                                                                                    col=indices[ai_col]))
                miss_counter += 1

                if grid_in[-1].upper() == "M":
                    color_map(player_board)
                break

        if player_board.check_game_end(suppressed=True):
            break

    if player_board.check_game_end(suppressed=False):
        print("You are defeated by my all-too-powerful AI in {num} moves!\n".format(num=ai_move_counter))
        print("This was the AI's board:")
        ai_board.reveal_board()
    elif ai_board.check_game_end(suppressed=False):
        print("Impossible, you have defeated the AI overlord in {num} moves!".format(num=player_move_counter))


    print(best_probas)

    return None


def autoplay(show_map=None, suppressed=False):

    if show_map is None:
        show_map = []

    ai_board = Board()
    ai_board.place_by_rng()

    if not suppressed:
        ai_board.reveal_board()

    move_counter = 0
    miss_counter = 0
    all_probas = []
    recent_probas = []

    while not ai_board.check_game_end(suppressed=True):
        ai_row, ai_col = find_best_grid(ai_board)

        # save the values for future use
        best_row, best_col = ai_row, ai_col

        current_proba = round(ai_board.board[ai_row][ai_col].proba, 3)
        all_probas.append(current_proba)
        recent_probas.append(current_proba)

        if current_proba >= 0.25 or miss_counter <= 10 or miss_counter > 35 or 25 >= miss_counter > 20:
            ai_board.play_move(ai_row, ai_col, suppressed=True)
        elif (20 >= miss_counter > 15 and current_proba < 0.23) or 35 >= miss_counter > 25:
            ai_row, ai_col = random_edge_move(ai_board)
        elif 20 >= miss_counter > 10 and current_proba < 0.25:
            ai_row, ai_col = random_exploratory_move(ai_board)

        if ai_row == 10 and ai_col == 10:
            ai_row, ai_col = best_row, best_col
            ai_board.play_move(best_row, best_col, suppressed=True)

        if not ai_board.board[ai_row][ai_col].occupied:
            ai_board.board[ai_row][ai_col].proba = 0
            miss_counter += 1
        else:
            ai_board.board[ai_row][ai_col].proba = 0.600

        if move_counter in show_map:
            ai_board.reveal_board()
            print(recent_probas)
            recent_probas.clear()
            color_map(ai_board)

        move_counter += 1

        # if not suppressed:
        #     print(move_counter)

    print("Finished game in " + str(move_counter) + " moves")
    # print(all_probas)
    print(sum(all_probas)/len(all_probas))

    return move_counter


ai = init_ai_board()
player = init_player_board()
play_game(player, ai)

# for i in range(101):
#     print("-"*50)
#     print("Game #" + str(i))
#     autoplay(suppressed=True)
