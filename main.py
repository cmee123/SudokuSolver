import time

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar

from kivymd.uix.snackbar import Snackbar

board = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
]

time_duration = None
time_start = None


class HomeWindow(Screen):
    pass


class InputWindow(Screen):
    # method to get the numbers inputted into the board and check they are valid
    def get_inputs(self):
        global board
        # set variables
        invalid = 0
        row = 8
        col = 8
        # first take all numbers in grid and add them to the board array
        # for every input box in the grid
        for widget in self.ids.input_board.children:
            # if there is no text
            if widget.text == "":
                # add a 0 to the board in that position
                board[row][col] = 0
            # if there is text
            else:
                # if is 1 digit
                if len(widget.text) == 1:
                    # append that number to the board in that position
                    try:
                        board[row][col] = int(widget.text)
                    # if it is not a number, specify that the board is invalid
                    except ValueError:
                        invalid += 1
                # if is are more than 1 digit
                else:
                    # specify that the board is invalid
                    invalid += 1
            # change board indexes for next grid position
            # starts looping grid from 9, 9 square, so indexes go down from 8
            col -= 1
            if col < 0:
                row -= 1
                col = 8

        # reset row, col indexes to check for validity
        row = 0
        col = 0
        # then check the board array to make sure it is valid
        # for every row in the board
        for i in board:
            # for every column in that row
            for k in i:
                # if it is not a valid number in that position
                if not self.valid(board, k, (row, col)):
                    # specify that the board is invalid
                    invalid += 1
            # change board indexes for next grid position
                col += 1
            row += 1
            col = 0
        # if the board is invalid at any point, show an error message
        if invalid > 0:
            Snackbar(text="Please enter valid information").open()
        # if the board is totally valid, change to the solve screen
        elif invalid == 0:
            self.parent.current = "solve"
            self.manager.transition.direction = "left"

    # method to determine if a number is valid in any given position
    # takes the board, the number in question, and the row and col of that number
    def valid(self, bo, num, pos):
        # check to see if the number fits in that row
        # for every column
        for i in range(len(bo[0])):
            # if the number is in any column in that row and it isn't the number and it isn't 0
            if bo[pos[0]][i] == num and pos[1] != i and num != 0:
                # then it is an invalid solution for that square
                return False

        # check to see if the number fits in that col
        # for every row
        for i in range(len(bo[0])):
            # if the number is in any row in that column and it isn't the number and it isn't 0
            if bo[i][pos[1]] == num and pos[0] != i and num != 0:
                # then it is an invalid solution for that square
                return False

        # check to see if the number fits in that box
        # first determine which box we are in
        box_x = pos[1] // 3
        box_y = pos[0] // 3
        # for each row and column in that box
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                # if the number is in any square in that box and it isn't the number and it isn't 0
                if bo[i][j] == num and (i, j) != pos and num != 0:
                    # then it is an invalid solution for that square
                    return False
        # if all of the previous conditions are met, then it is a valid solution for that square
        return True

    # method to clear all numbers inputted into the grid
    def clear_inputs(self):
        # for every input box in the grid
        for widget in self.ids.input_board.children:
            # make the text blank
            widget.text = ""


class SolveWindow(Screen):
    # method to start the process of either updating the board or solving the puzzle
    # cannot use board from .kv file, so must use this method
    def start_process(self, solve=False):
        global board, time_duration, time_start
        # if we don't want to solve the puzzle
        if not solve:
            # update the numbers in the board
            self.update_board(board)
        # if we do want to solve the puzzle
        elif solve:
            # set the maximum time allowed to complete the puzzle
            time_duration = 5
            time_start = time.time()
            # solve the puzzle
            self.solve(board)

    def solve(self, bo):
        global time_duration, time_start
        # first find the coordinates of an empty square
        find = self.find_empty(bo)
        # if we have not reached the maximum allotted time
        if time.time() < time_start + time_duration:
            # if no empty squares were found
            if not find:
                # update the board to show solution and stop solving puzzle
                self.update_board(bo)
                return True
            # otherwise get the coordinates of that empty square
            else:
                row, column = find

            # determine the possible solutions for that square
            # loop through numbers 1 to 9
            for i in range(1, 10):
                # if that number if valid in that square
                if self.valid(bo, i, (row, column)):
                    # put it into the board
                    bo[row][column] = i
                    # attempt to solve the puzzle assuming that the number is correct
                    if self.solve(bo):
                        # if the puzzle is completed, update the board to show solution and stop solving puzzle
                        self.update_board(bo)
                        return True
                    # if the puzzle is not able to be completed, reset the square
                    bo[row][column] = 0
        # if we have reached the maximum allotted time, we assume the puzzle is impossible
        else:
            # raise an error message
            Snackbar(text="Sudoku board is not solvable").open()
        return False

    def valid(self, bo, num, pos):
        # check to see if the number fits in that row
        # for every column
        for i in range(len(bo[0])):
            # if the number is in any column in that row and it isn't the number
            if bo[pos[0]][i] == num and pos[1] != i:
                # then it is an invalid solution for that square
                return False

        # check to see if the number fits in that col
        # for every row
        for i in range(len(bo[0])):
            # if the number is in any row in that column and it isn't the number
            if bo[i][pos[1]] == num and pos[0] != i:
                # then it is an invalid solution for that square
                return False

        # check to see if the number fits in that box
        # first determine which box we are in
        box_x = pos[1] // 3
        box_y = pos[0] // 3
        # for each row and column in that box
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                # if the number is in any square in that box and it isn't the number
                if bo[i][j] == num and (i, j) != pos:
                    # then it is an invalid solution for that square
                    return False
        # if all of the previous conditions are met, then it is a valid solution for that square
        return True

    # method to find an empty square in the board
    def find_empty(self, bo):
        # for every row
        for i in range(len(bo)):
            # for every column in that row
            for j in range(len(bo[0])):
                # if the value in that square is 0 then it is empty
                if bo[i][j] == 0:
                    # return the row and column coordinates of that square
                    return (i, j)  # row, column
        # if no empty squares are found, return none
        return None

    # method to update the board on screen based on the board array
    def update_board(self, bo):
        # specify coordinates for each square
        row = 8
        col = 8
        # for every label in the grid
        for widget in self.ids.solve_board.children:
            # make its text correspond with that position in the board array
            widget.text = str(bo[row][col])
            # update the indexes to handle next label position
            col -= 1
            if col < 0:
                row -= 1
                col = 8


class WindowManager(ScreenManager):
    pass


class SudokuSolver(MDApp):
    # method to build the app
    def build(self):
        # designate kivy design file
        kv = Builder.load_file("solver_gui.kv")
        # set default background color for app
        Window.clearcolor = (1, 1, 1, 1)
        return kv

# set window size
Window.size = (600, 600)

if __name__ == "__main__":
    SudokuSolver().run()

