"""Wordle application."""


from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from random import randrange
import csv
import sys

@dataclass
class Config:
    list_path: Path


@dataclass
class Entry:
    word: str


class Status(Enum):
    NOT_TESTED = 0
    INCORRECT = 1
    WRONG_PLACE = 2
    CORRECT = 3


def read_args() -> Config:
    if len(sys.argv) > 1:
        list_path = Path(sys.argv[1])
        return Config(list_path)
    else:
        print("Error: First argument must be the path to a list of English words.")


def read_list(config: Config) -> list[Entry]:
    entries: list[Entry] = []
    words: list[str]
    with open(config.list_path, encoding="utf-8") as list_file:
        words = [line for line in list_file]
    for word in words:
        entry = Entry(word)
        entries.append(entry)
    return entries


def guess_validation(guess: str) -> bool:
    isvalid = True

    if (len(guess) > 5):
        print("Length of word is too long, word must be five letters.")
        isvalid = False
    if (len(guess) < 5):
        print("Length of word is too short, word must be five letters.")
        isvalid = False
    if (not guess.isalpha()):
        print("Guess contains non-alphabet characters. Word only contains characters in the English alphabet.")
        isvalid = False

    return isvalid


def test_guess(guess: str, word: str):
    statuses = [Status.NOT_TESTED, Status.NOT_TESTED, Status.NOT_TESTED, Status.NOT_TESTED, Status.NOT_TESTED]
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


def print_result(statusarray, correct_letters, guess):
    i = 0    
    for status in statusarray:
        print(guess[i] + " is " + str(status))
        i += 1

    if correct_letters == 5:
        print("You have guessed the word. You win!")


def process_guess(word: str, guess_no: int) -> int:
    print("Guess #" + str(guess_no) + ":")
    guess = input()

    while not guess_validation(guess):
        print("Guess #" + str(guess_no) + ":")
        guess = input()

    statusarray, correct_letters = test_guess(guess, word)

    print_result(statusarray, correct_letters, guess)

    return correct_letters


def run_game(config: Config):
    entries = read_list(config)

    word_number = randrange((len(entries) - 1))
    word = entries[word_number].word

    for i in range(5):
        correct_letters = process_guess(word, i+1)
        if (correct_letters == 5):
            break
    
    print("The word was: " + word)


def main():
    config = read_args()

    if config is not None:
        while True:
            run_game(config)

            response_valid = False
            while not response_valid:
                print("Would you like to play again?")
                response = input().lower()       
                if response == "y":
                    response_valid = True
                elif response == "n":
                    exit()
                else:
                    print("Invalid input. Try again.")
                
                    

if __name__ == "__main__":
    main()
