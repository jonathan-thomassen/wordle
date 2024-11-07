"""Wordle application."""


from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from random import randrange
from tkinter import *
import sys
import tkinter


@dataclass
class Config:
    list_path: Path


class Status(Enum):
    NOT_TESTED = 0
    INCORRECT = 1
    WRONG_PLACE = 2
    CORRECT = 3


class Validation_State(Enum):
    TOO_LONG = 0
    TOO_SHORT = 1
    NOT_IN_DICTIONARY = 2
    VALID = 3


class Square:
    def __init__(self):
        self.status = Status.NOT_TESTED
        self.letter = ""
    

class Screen:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.bind("<KeyPress>", self.onKeyPress)
        self.grid = [[Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()]]
        self.active_row = 0
        self.active_column = 0
 
    def onKeyPress(self, e):
        print("Key pressed:", e.char.upper(), e.keycode)

        #Check if key pressed is in English alphabet:
        if e.keycode >= 65 and e.keycode <= 90 and self.grid[self.active_row][self.active_column].letter == "":
            self.grid[self.active_row][self.active_column].letter = e.char.upper()
            if self.active_column <= 3:
                self.active_column += 1
            draw_grid(self)
        #Check for backspace:
        elif e.keycode == 8:
            if self.active_column >= 1 and self.grid[self.active_row][self.active_column].letter == "":
                self.active_column -= 1
            self.grid[self.active_row][self.active_column].letter = ""
            draw_grid(self)
        #Check for enter:
        elif e.keycode == 13 and self.grid[self.active_row][self.active_column].letter != "":
            guess: str = ""
            for square in self.grid[self.active_row]:
                guess += square.letter
            validation_state = guess_validation(guess)
            if validation_state == Validation_State.VALID:
                statuses, correct_letter_amount = test_guess(guess, word)

                i = 0
                for square in self.grid[self.active_row]:
                    square.status = statuses[i]
                    i += 1

                self.active_column = 0
                self.active_row += 1
                draw_grid(self)


dictionary: list[str]
word: str


def read_args() -> Config:
    if len(sys.argv) > 1:
        list_path = Path(sys.argv[1])
        return Config(list_path)
    else:
        print("Error: First argument must be a valid path to a list of English words.")


def read_list(config: Config) -> list[str]:
    words: list[str]
    with open(config.list_path, encoding="utf-8") as list_file:
        words = [line.strip() for line in list_file]
    return words


def check_dictionary(guess: str) -> bool:
    if guess.lower() in dictionary:
        return True
    return False


def guess_validation(guess: str) -> Validation_State:
    if len(guess) > 5:
        print("Length of word is too long, word must be five letters.")
        return Validation_State.TOO_LONG
    if len(guess) < 5:
        print("Length of word is too short, word must be five letters.")
        return Validation_State.TOO_SHORT
    if not check_dictionary(guess):
        print("Word is not in dictionary. Please input a valid English word.")
        return Validation_State.NOT_IN_DICTIONARY
    
    return Validation_State.VALID


def test_guess(guess: str, word: str) -> tuple[list[Status], int]:
    guess = guess.lower()
    statuses = [Status.NOT_TESTED] * 5
    correct_letters = 0

    for i in range(5):
        if guess[i] == word[i]:
            statuses[i] = Status.CORRECT
            correct_letters += 1
        elif word.count(guess[i]) > 0:
            statuses[i] = Status.WRONG_PLACE
        else:
            statuses[i] = Status.INCORRECT
        
    return statuses, correct_letters


def print_result(statuses, correct_letters, guess):
    i = 0    
    for status in statuses:
        print(guess[i] + " is " + str(status))
        i += 1

    if correct_letters == 5:
        print("Correct! You win!")


def process_guess(word: str, guess_no: int) -> int:
    print("Guess #" + str(guess_no) + ":")
    guess = input().lower()

    while not guess_validation(guess):
        print("Guess #" + str(guess_no) + ":")
        guess = input()

    if guess == "igiveup":
        return 5
    
    statuses, correct_letters = test_guess(guess, word)

    print_result(statuses, correct_letters, guess)

    return correct_letters


def run_game(config: Config):
    global dictionary 
    dictionary = read_list(config)

    word_number = randrange((len(dictionary) - 1))
    global word
    word = dictionary[word_number]

    screen = Screen()
    screen.window.title("Wordle Clone")
    screen.window.resizable(width=False, height=False)
    screen.window.geometry("460x550")
    screen.window.configure(bg="black")
    draw_grid(screen)

    screen.window.mainloop()

    """ for i in range(6):
        correct_letters = process_guess(word, i+1)
        if (correct_letters == 5):
            break """
    
    print("The word was: " + word)


def draw_grid(screen: Screen):
    square_size = 80
    hor_screen_edge = 10
    ver_screen_edge = 10
    hor_square_margin = 10
    ver_square_margin = 10    

    for row in range(6):
        for column in range(5):
            square = screen.grid[row][column]
            if square.status == Status.NOT_TESTED:
                bg_color = "black"
                text_color = "white"
            elif square.status == Status.INCORRECT:
                bg_color = "black"
                text_color = "red"
            elif square.status == Status.CORRECT:
                bg_color = "black"
                text_color = "green"
            elif square.status == Status.WRONG_PLACE:
                bg_color = "black"
                text_color = "yellow"

            frame = tkinter.Frame(screen.window, background=bg_color, highlightbackground=text_color, highlightthickness=1, width=square_size, height=square_size)
            frame.pack_propagate(0)    
            label = tkinter.Label(frame, bg=bg_color, fg=text_color, font=("Calibri", 24), text=square.letter)
            label.pack(expand=True)
            frame.place(x = column * (square_size + hor_square_margin) + hor_screen_edge, y = row * (square_size + ver_square_margin) + ver_screen_edge)


def main():
    config = read_args()

    if config is not None:
        run_game(config)


if __name__ == "__main__":
    main()
