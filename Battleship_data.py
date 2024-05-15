
"""Data Collection Implementation"""

import random


def random_moves(Board, num_moves):

    # REQUIRES: num_moves < 100

    num_moved = 0

    while num_moved < num_moves:
        index = random.randint(0, 99)
        row = index // 10
        col = index % 10
        if Board.board[row][col].hit:
            continue
        else:
            Board.play_move(row, col)
            num_moved += 1

    return


def partition_move():
    # break up 100 into intervals with length (1,10)

    num_moves = []
    while sum(num_moves) < 100:
        num_moves.append(random.randint(1, 10))
    if sum(num_moves) >= 100:
        num_moves.pop()
    return num_moves


def check_inbound(row, col):
    return 0 <= row < 10 and 0 <= col < 10


def collect_board_data(Board):
    # Count how many occupied grids are not hit yet

    occupied_remain = 17
    total_remain = 100

    for row in range(10):
        for col in range(10):
            if Board.board[row][col].hit:
                if Board.board[row][col].occupied:
                    occupied_remain -= 1
                total_remain -= 1

    return round(occupied_remain/total_remain, 3)


def distance_to_center(row, col):
    # calculates a grid's distance to the center of the board
    # defined as the Euclidean distance from the grid to the nearest one of the four central grids

    dist_center = 0

    if row <= 4:
        dist_center += (4-row)**2
    else:
        dist_center += (5-row)**2

    if col <= 4:
        dist_center += (4-col)**2
    else:
        dist_center += (5-col)**2

    return round(dist_center**0.5, 3)


def collect_grid_data(Board, row, col):
    # adj_miss = adjacent grids confirmed hit / total # of adjacent grids
    # adj_hit = adjacent grids confirmed miss / total # of adjacent grids
    # diag_hit and diag_miss defined similarly

    # only record data that would be available to a hypothetical player

    del_rows = [0, 1, -1]
    del_cols = [0, 1, -1]

    dist_center = distance_to_center(row, col)
    adj_count = 0
    adj_hit = 0
    adj_miss = 0
    diag_count = 0
    diag_hit = 0
    diag_miss = 0

    for del_row in del_rows:
        for del_col in del_cols:
            if del_row == 0 and del_col == 0:
                continue

            row_now = row + del_row
            col_now = col + del_col

            if check_inbound(row_now, col_now):
                if del_row == 0 or del_col == 0:
                    adj_count += 1
                    if Board.board[row_now][col_now].hit and Board.board[row_now][col_now].occupied:
                        adj_hit += 1
                    elif Board.board[row_now][col_now].hit and not Board.board[row_now][col_now].occupied:
                        adj_miss += 1
                else:
                    diag_count += 1
                    if Board.board[row_now][col_now].hit and Board.board[row_now][col_now].occupied:
                        diag_hit += 1
                    elif Board.board[row_now][col_now].hit and not Board.board[row_now][col_now].occupied:
                        diag_miss += 1

    adj_hit = round(adj_hit/adj_count, 2)
    adj_miss = round(adj_miss/adj_count, 2)
    diag_hit = round(diag_hit/diag_count, 2)
    diag_miss = round(diag_miss/diag_count, 2)

    return dist_center, adj_hit, adj_miss, diag_hit, diag_miss


def choose_grids():
    return random.sample(range(100), 10)


# data collection codes are commented below
# df_master = pd.DataFrame(columns=["occupied?",
#                                 "occupied_pct",
#                                 "dist_center",
#                                 "adj_hit",
#                                 "adj_miss",
#                                 "diag_hit",
#                                 "diag_miss"])
#
# counter = 0
#
# for i in range(1000):
#
#     board = Board()
#     board.place_by_rng()
#     num_moves = partition_move()
#
#     for num_move in num_moves:
#         random_moves(board, num_move)
#         occupied_pct = collect_board_data(board)
#
#         grids = choose_grids()
#
#         for grid in grids:
#             row = grid // 10
#             col = grid % 10
#             occupied, dist_center, adj_hit, adj_miss, diag_hit, diag_miss = collect_grid_data(board, row, col)
#
#             df_master.loc[counter] = [occupied,
#                                     occupied_pct,
#                                     dist_center,
#                                     adj_hit,
#                                     adj_miss,
#                                     diag_hit,
#                                     diag_miss]
#             counter += 1
#
# df_master.to_csv("master.csv", index=False)
