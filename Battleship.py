# for now, confine the board to be 10x10
# allow both placement by user input and random placement
# some of the functions needed:
# initialize board, placement by input/rng, check valid placement, implement user move, check game end

# 0 is horizontal orientation, 1 is vertical orientation
# default ship sizes: 5 4 3 3 2
# C-Carrier, B-Battleship, D-Destroyer, S-Submarine, P-Patrol Boat

import random


class Grid:

    # the board will be made up of class Grid objects

    def __init__(self, id, name="", occupied=False, hit=False, proba=None):
        self.id = id
        self.occupied = occupied
        self.hit = hit
        self.name = name
        self.proba = proba

    def __repr__(self):
        print_id = "Grid number " + str(self.id)
        print_occupation = " is {occupation}".format(occupation='occupied' if self.occupied else "unoccupied")
        print_status = " and {status}".format(status='hit' if self.hit else 'not hit')

        return print_id + print_occupation + print_status


class Board:
    # len(sizes) or len(names) should both give the amount of ship on the board

    dim = 10
    names = ["C", "B", "D", "S", "P"]
    sizes = [5, 4, 3, 3, 2]
    occupied_indices = []
    placement = []
    board_indices = "ABCDEFGHIJ"

    def __init__(self, name=None):
        self.board = [[[] for i in range(10)] for i in range(10)]
        self.name = name

        for row in range(self.dim):
            for col in range(self.dim):
                self.board[row][col] = Grid(id=row * 10 + col)

    def __repr__(self):
        row_bars = "  " + "-" * 21

        to_print = "   A B C D E F G H I J\n" + row_bars + "\n"

        for row in range(self.dim):
            to_print += (self.board_indices[row] + " |")

            for col in range(self.dim):
                if not self.board[row][col].hit:
                    to_print += " "
                else:
                    if self.board[row][col].occupied:
                        to_print += "X"
                    else:
                        to_print += '\\'
                to_print += "|"

            to_print += ("\n" + row_bars + "\n")

        to_print += "   A B C D E F G H I J\n"
        return to_print

    def reveal_board(self):
        row_bars = "  " + "-" * 21

        to_print = "   A B C D E F G H I J\n" + row_bars + "\n"

        for row in range(self.dim):
            to_print += (self.board_indices[row] + " |")

            for col in range(self.dim):
                if self.board[row][col].hit:
                    if self.board[row][col].occupied:
                        to_print += "X"
                    else:
                        to_print += "\\"
                elif self.board[row][col].occupied:
                    to_print += self.board[row][col].name
                else:
                    to_print += ' '
                to_print += "|"

            to_print += ("\n" + row_bars + "\n")
        to_print += "   A B C D E F G H I J\n"
        print(to_print)

    def print_proba(self):
        to_print = "     A     B     C     D     E     F     G     H     I     J\n"

        for row in range(self.dim):
            to_print += (self.board_indices[row] + " ")
            for col in range(self.dim):
                to_print += str(round(self.board[row][col].proba,3))
                to_print += " "
            to_print += "\n"

        print(to_print)

    def check_placement_valid(self, row, col, size, orientation):
        if orientation == 0:
            if col > self.dim - size or col < 0:
                return False
            for i in range(size):
                if self.board[row][col + i].occupied:
                    return False
            return True
        elif orientation == 1:
            if row > self.dim - size or row < 0:
                return False
            for i in range(size):
                if self.board[row + i][col].occupied:
                    return False
            return True
        else:
            print("The orientation you have requested is invalid!")
            return False

    def place_ship(self, row, col, size, orientation, name, rng=True):

        # can assume the placement is valid

        if orientation == 0:
            for i in range(size):
                self.board[row][col + i].occupied = True
                self.board[row][col + i].name = name
        elif orientation == 1:
            for i in range(size):
                self.board[row + i][col].occupied = True
                self.board[row + i][col].name = name

        if not rng:
            self.occupied_indices.extend([10 * row + col + i if orientation == 0 else 10 * (row + i) + col for i in
                                          range(self.sizes[i])])
            self.placement.extend([row, col, orientation])

    def place_by_rng(self):
        while len(self.occupied_indices) != len(set(self.occupied_indices)) or len(self.placement) != 15:
            self.placement = []
            self.occupied_indices = []

            for i in range(len(self.sizes)):
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                orientation = random.randint(0, 1)

                if self.check_placement_valid(row, col, self.sizes[i], orientation):
                    self.occupied_indices.extend(
                        [10 * row + col + i if orientation == 0 else 10 * (row + i) + col for i in
                         range(self.sizes[i])])
                    self.placement.extend([row, col, orientation])

        for i in range(len(self.sizes)):
            self.place_ship(self.placement[3 * i], self.placement[3 * i + 1], self.sizes[i], self.placement[3 * i + 2],
                            self.names[i])

    def play_move(self, *coordinates, suppressed):

        # can assume the input row and col are valid

        for i in range(len(coordinates) // 2):
            row = coordinates[2 * i]
            col = coordinates[2 * i + 1]
            self.board[row][col].hit = True

            if not suppressed:
                if self.board[row][col].occupied:
                    print("Target hit!")
                else:
                    print("Target missed!")

    def check_game_end(self, suppressed):
        for index in self.occupied_indices:
            row = index // 10
            col = index % 10
            if not self.board[row][col].hit:
                return False

        if not suppressed:
            print("All vessels on {name}'s boards have been destroyed".format(name=self.name))
        return True
