"""Wordle application."""


from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from random import randrange
import ctypes

import pygame
import pygame.freetype

import words


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


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE_H = 1080
WIN_W = 500
WIN_H = 782


class Screen:
    def __init__(self):
        self.scale_mode: int
        self.desktop_h = pygame.display.Info().current_h
        self.scale = pygame.display.Info().current_h / BASE_H
        self.window = pygame.display.set_mode((WIN_W * self.scale, WIN_H * self.scale))
        self.letters = {}
        for letter in ALPHABET:
            self.letters.update({letter:Status.NOT_TESTED})
        self.word = ""
        self.initiate_window()

    def initiate_window(self):
        self.grid = [[Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()],
                     [Square(), Square(), Square(), Square(), Square()]]
        self.caption = "Start typing to begin"
        for square in  self.grid[0]:
            square.status = Status.NOT_TESTED
        self.active_row = 0
        self.active_column = 0
        self.state = Game_State.IN_GAME


def handleEvent(screen: Screen, event: pygame.event.Event):
    if screen.state == Game_State.OUT_OF_GAME:
        screen.initiate_window()
        new_word(screen)
        screen.letters = {}
        for letter in ALPHABET:
            screen.letters.update({letter:Status.NOT_TESTED})
        draw_grid(screen)
    else:
        #Check if key pressed is in English alphabet:
        if event.scancode >= 4 and \
           event.scancode <= 29 and \
           screen.grid[screen.active_row][screen.active_column].letter == "":
            screen.grid[screen.active_row][screen.active_column].letter = ALPHABET[event.scancode-4]
            if screen.active_column <= 3:
                screen.active_column += 1
            screen.caption = "Guess #" + str(screen.active_row + 1)
            draw_grid(screen)
        #Check for backspace:
        elif event.key == pygame.K_BACKSPACE: # pylint: disable=no-member
            if screen.active_column >= 1 and \
               screen.grid[screen.active_row][screen.active_column].letter == "":
                screen.active_column -= 1
            screen.grid[screen.active_row][screen.active_column].letter = ""
            screen.caption = "Guess #" + str(screen.active_row + 1)
            draw_grid(screen)
        #Check for enter:
        elif event.key == pygame.K_RETURN and \
             screen.grid[screen.active_row][screen.active_column].letter != "": # pylint: disable=no-member
            guess: str = ""
            for square in screen.grid[screen.active_row]:
                guess += square.letter
            validation_state = guess_validation(guess)
            if validation_state == Validation_State.VALID:
                statuses, correct_letter_amount = test_guess(screen, guess)

                i = 0
                for square in screen.grid[screen.active_row]:
                    square.status = statuses[i]
                    i += 1

                if correct_letter_amount == 5:
                    screen.caption = "Correct! You win!"
                    screen.state = Game_State.OUT_OF_GAME
                elif screen.active_row <= 4:
                    screen.active_column = 0
                    screen.active_row += 1

                    for square in screen.grid[screen.active_row]:
                        square.status = Status.NOT_TESTED
                    screen.caption = "Guess #" + str(screen.active_row + 1)
                else:
                    screen.caption = "You lost! The word was: " + screen.word.upper()
                    screen.state = Game_State.OUT_OF_GAME
            elif validation_state == Validation_State.NOT_IN_DICTIONARY:
                for square in screen.grid[screen.active_row]:
                    square.letter = ""
                    square.status = Status.NOT_TESTED

                screen.active_column = 0

                screen.caption = "Word not in dictionary. Try again"
            draw_grid(screen)


def check_dictionary(guess: str) -> bool:
    if guess.lower() in words.WORDS:
        return True
    return False


def guess_validation(guess: str) -> Validation_State:
    if not check_dictionary(guess):
        return Validation_State.NOT_IN_DICTIONARY

    return Validation_State.VALID


def test_guess(screen: Screen, guess: str) -> tuple[list[Status], int]:
    guess = guess.lower()
    statuses = [Status.NOT_TESTED] * 5
    correct_letters = 0
    temp_word = screen.word

    for i in range(5):
        if guess[i] == screen.word[i]:
            statuses[i] = Status.CORRECT
            screen.letters[guess[i].upper()] = Status.CORRECT
            correct_letters += 1
            temp_word = temp_word.replace(screen.word[i], "", 1)
    for i in range(5):
        if screen.word.count(guess[i]) > 0:
            if statuses[i] != Status.CORRECT:
                if guess[i] in temp_word:
                    statuses[i] = Status.WRONG_PLACE
                    if screen.letters[guess[i].upper()] != Status.CORRECT:
                        screen.letters[guess[i].upper()] = Status.WRONG_PLACE
                    temp_word = temp_word.replace(guess[i], "", 1)
                else:
                    statuses[i] = Status.INCORRECT
                    if screen.letters[guess[i].upper()] != Status.CORRECT and \
                       screen.letters[guess[i].upper()] != Status.WRONG_PLACE:
                        screen.letters[guess[i].upper()] = Status.INCORRECT
        else:
            statuses[i] = Status.INCORRECT
            if screen.letters[guess[i].upper()] != Status.CORRECT and \
               screen.letters[guess[i].upper()] != Status.WRONG_PLACE:
                screen.letters[guess[i].upper()] = Status.INCORRECT

    return statuses, correct_letters


def new_word(screen: Screen):
    word_number = randrange((len(words.WORDS) - 1))
    screen.word = words.WORDS[word_number]


def run_game():    
    pygame.init() # pylint: disable=no-member

    pygame.display.set_caption("Five-letter Word Game")

    screen = Screen()
    clock = pygame.time.Clock()
    new_word(screen)
    running = True
    draw_grid(screen)
    while running:
        for event in pygame.event.get(eventtype=pygame.KEYDOWN): # pylint: disable=no-member
            handleEvent(screen, event)
        for event in pygame.event.get(eventtype=pygame.QUIT): # pylint: disable=no-member
            running = False

        clock.tick(60)


def get_letter_color(screen: Screen, letter: str) -> str:
    if screen.letters[letter] == Status.CORRECT:
        return "green"
    if screen.letters[letter] == Status.INCORRECT:
        return "red"
    if screen.letters[letter] == Status.WRONG_PLACE:
        return "yellow"
    if screen.letters[letter] == Status.NOT_TESTED:
        return "grey"


def draw_keyboard(screen: Screen, start_y: int):
    square_size = 42 * screen.scale
    font_size = 18 * screen.scale
    hor_screen_edge = 8 * screen.scale
    hor_square_margin = 7 * screen.scale
    ver_square_margin = 7 * screen.scale
    row_margin = 8 * screen.scale

    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

    def draw_character(row: int, column: int, letter: str):
        fg_color = get_letter_color(screen, letter)
        square_font = pygame.freetype.SysFont("Trebuchet MS", font_size)

        square_rect = pygame.Rect(
            hor_screen_edge + column * (square_size + hor_square_margin) + row * row_margin,
            start_y + row * (square_size + ver_square_margin),
            square_size,
            square_size)
        pygame.draw.rect(screen.window, fg_color, square_rect, 1)
        text_surface, text_rect = square_font.render(letter, fg_color)
        screen.window.blit(
            text_surface,
            (square_rect.left + square_rect.width / 2 - text_rect.width / 2,
             square_rect.top + square_rect.height / 2 - text_rect.height / 2))

    for row in range(3):
        for column, letter in enumerate(rows[row]):
            draw_character(row, column, letter)


def draw_grid(screen: Screen):
    square_size = 88 * screen.scale
    screen_edge = 10 * screen.scale
    hor_square_margin = 10 * screen.scale
    ver_square_margin = 10 * screen.scale
    font_size = 36 * screen.scale
    square_font = pygame.freetype.SysFont("OCR-A Extended", font_size )

    screen.window.fill("black")

    for row in range(6):
        for column in range(5):
            square = screen.grid[row][column]
            text_color = "grey"

            if square.status == Status.NOT_TESTED:
                text_color = "white"
            elif square.status == Status.INCORRECT:
                text_color = "red"
            elif square.status == Status.CORRECT:
                text_color = "green"
            elif square.status == Status.WRONG_PLACE:
                text_color = "yellow"

            square_rect = pygame.Rect(
                column * (square_size + hor_square_margin) + screen_edge,
                row * (square_size + ver_square_margin) + screen_edge,
                square_size,
                square_size)
            pygame.draw.rect(screen.window, text_color, square_rect, 1)
            text_surface, text_rect = square_font.render(square.letter, text_color, "black")
            screen.window.blit(
                text_surface,
                (square_rect.left + square_rect.width / 2 - text_rect.width / 2,
                 square_rect.top + square_rect.height / 2 - text_rect.height / 2))

    label_font = pygame.freetype.SysFont("Lucida Console", 22 * screen.scale)
    text_surface, text_rect = label_font.render(screen.caption, "white")
    screen.window.blit(
        text_surface,
        (0 + screen.window.get_width() / 2 - text_rect.width / 2, 600 * screen.scale))

    draw_keyboard(screen, 634 * screen.scale)

    pygame.display.flip()


def main():
    ctypes.windll.user32.SetProcessDPIAware()

    run_game()


if __name__ == "__main__":
    main()
