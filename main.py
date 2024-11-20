"""Wordle application."""


from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from random import randrange
from tkinter import *
from unidecode import unidecode
import sys
import tkinter


@dataclass
class Config:
    list_path: Path


class Status(Enum):
    INACTIVE = 0
    NOT_TESTED = 1
    INCORRECT = 2
    WRONG_PLACE = 3
    CORRECT = 4


class Validation_State(Enum):
    TOO_LONG = 0
    TOO_SHORT = 1
    NOT_IN_DICTIONARY = 2
    VALID = 3

class Game_State(Enum):
    IN_GAME = 0
    OUT_OF_GAME = 1


class Square:
    def __init__(self):
        self.status = Status.INACTIVE
        self.letter = ""


dictionary: list[str]
word: str
letters: dict
    

class Screen:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.bind("<KeyPress>", self.onKeyPress)
        self.initiate_window()
 
    def onKeyPress(self, e):
        print("Key pressed:", e.char.upper(), e.keycode)

        if self.state == Game_State.OUT_OF_GAME:
            self.initiate_window()
            new_word()
            alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM"
            global letters
            letters = {}
            for letter in alphabet:
                letters.update({letter:Status.NOT_TESTED})
            draw_grid(self)
        else:
            #Check if key pressed is in English alphabet:
            if e.keycode >= 65 and e.keycode <= 90 and e.char.isalpha() and self.grid[self.active_row][self.active_column].letter == "":
                #Use unidecode to strip out any accents
                self.grid[self.active_row][self.active_column].letter = unidecode(e.char.upper())
                if self.active_column <= 3:
                    self.active_column += 1
                self.caption = "Guess #" + str(self.active_row + 1)
                draw_grid(self)
            #Check for backspace:
            elif e.keycode == 8:
                if self.active_column >= 1 and self.grid[self.active_row][self.active_column].letter == "":
                    self.active_column -= 1
                self.grid[self.active_row][self.active_column].letter = ""
                self.caption = "Guess #" + str(self.active_row + 1)
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

                    if correct_letter_amount == 5:
                        self.caption = "Congratulations! You won!"
                        self.state = Game_State.OUT_OF_GAME
                    elif self.active_row <= 4:
                        self.active_column = 0
                        self.active_row += 1

                        for square in self.grid[self.active_row]:
                            square.status = Status.NOT_TESTED  
                        self.caption = "Guess #" + str(self.active_row + 1)
                    else:
                        self.caption = "You lost! The word was: " + word.upper()
                        self.state = Game_State.OUT_OF_GAME
                elif validation_state == Validation_State.NOT_IN_DICTIONARY:
                    for square in self.grid[self.active_row]:
                        square.letter = ""
                        square.status = Status.NOT_TESTED

                    self.active_column = 0

                    self.caption = "Word is not in word list. Try another word."
                draw_grid(self)
    
    def initiate_window(self):
        self.grid = [[Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()]]
        self.caption = "Welcome! Start typing to begin"
        for square in  self.grid[0]:
            square.status = Status.NOT_TESTED
        self.active_row = 0
        self.active_column = 0
        self.state = Game_State.IN_GAME


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
        print("Word is not in dictionary. Please try a different word.")
        return Validation_State.NOT_IN_DICTIONARY
    
    return Validation_State.VALID


def test_guess(guess: str, word: str) -> tuple[list[Status], int]:
    guess = guess.lower()
    statuses = [Status.NOT_TESTED] * 5
    correct_letters = 0
    temp_word = word

    global letters
    for i in range(5):
        if guess[i] == word[i]:
            statuses[i] = Status.CORRECT
            letters[guess[i].upper()] = Status.CORRECT
            correct_letters += 1
            temp_word = temp_word.replace(word[i], "", 1)
    for i in range(5):
        if word.count(guess[i]) > 0:
            if statuses[i] != Status.CORRECT:
                if guess[i] in temp_word:
                    statuses[i] = Status.WRONG_PLACE
                    if letters[guess[i].upper()] != Status.CORRECT:
                        letters[guess[i].upper()] = Status.WRONG_PLACE
                    temp_word = temp_word.replace(guess[i], "", 1)
                else:
                    statuses[i] = Status.INCORRECT
                    if letters[guess[i].upper()] != Status.CORRECT and letters[guess[i].upper()] != Status.WRONG_PLACE:
                        letters[guess[i].upper()] = Status.INCORRECT
        else:
            statuses[i] = Status.INCORRECT
            if letters[guess[i].upper()] != Status.CORRECT and letters[guess[i].upper()] != Status.WRONG_PLACE:
                letters[guess[i].upper()] = Status.INCORRECT
        
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

def new_word():
    word_number = randrange((len(dictionary) - 1))
    global word
    word = dictionary[word_number]


def run_game(config: Config):
    global dictionary 
    dictionary = read_list(config)

    alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM"
    global letters
    letters = {}
    for letter in alphabet:
        letters.update({letter:Status.NOT_TESTED})

    new_word()
    
    screen = Screen()
    screen.window.title("Wordle Clone")
    screen.window.resizable(width=False, height=False)
    screen.window.geometry("460x716")
    screen.window.configure(bg="black")
    draw_grid(screen)

    screen.window.mainloop()
    
    print("The word was: " + word)


def get_letter_color(letter) -> str:
    if letters[letter] == Status.CORRECT:
        return "green"
    elif letters[letter] == Status.INCORRECT:
        return "red"
    elif letters[letter] == Status.WRONG_PLACE:
        return "yellow"
    elif letters[letter] == Status.NOT_TESTED:
        return "grey"


def draw_keyboard(screen: Screen, start_y: int):
    square_size = 36
    font_size = 12
    hor_screen_edge = 10
    ver_screen_edge = 10
    hor_square_margin = 8
    ver_square_margin = 8
    row_margin = 8

    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

    def draw_row(row_no: int):
        fg_color = get_letter_color(letter)

        frame = tkinter.Frame(screen.window, background="black", highlightbackground=fg_color, highlightthickness=1, width=square_size, height=square_size)
        frame.pack_propagate(0)
        label = tkinter.Label(frame, bg="black", fg=fg_color, font=("Calibri", font_size), text=letter)
        label.pack(expand=True)
        frame.place(x = hor_screen_edge + i * (square_size + hor_square_margin) + row_no * row_margin, y = start_y + ver_screen_edge + row_no * (square_size + ver_square_margin))

    for row_no in range(3):
        for i, letter in enumerate(rows[row_no]):
            draw_row(row_no)


def draw_grid(screen: Screen):
    square_size = 80
    hor_screen_edge = 10
    ver_screen_edge = 10
    hor_square_margin = 10
    ver_square_margin = 10

    for child in screen.window.winfo_children():
        child.destroy()

    for row in range(6):
        for column in range(5):
            square = screen.grid[row][column]
            if square.status == Status.INACTIVE:
                bg_color = "black"
                text_color = "grey"
            elif square.status == Status.NOT_TESTED:
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
    
    frame = tkinter.Frame(screen.window, background="black", width=460, height=40)
    frame.pack_propagate(0)
    label = tkinter.Label(frame, bg="black", fg="white", font=("Calibri", 14), text=screen.caption)
    label.pack(expand=True)
    frame.place(x = 0, y = 540)

    draw_keyboard(screen, 570)


def main():
    config = read_args()

    if config is not None:
        run_game(config)


if __name__ == "__main__":
    main()
