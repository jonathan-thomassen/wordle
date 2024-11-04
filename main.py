"""Wordle application."""


from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from random import randrange
import sys


@dataclass
class Config:
    list_path: Path


class Status(Enum):
    NOT_TESTED = 0
    INCORRECT = 1
    WRONG_PLACE = 2
    CORRECT = 3


dictionary: list[str]


def read_args() -> Config:
    if len(sys.argv) > 1:
        list_path = Path(sys.argv[1])
        return Config(list_path)
    else:
        print("Error: First argument must be the path to a list of English words.")


def read_list(config: Config) -> list[str]:
    words: list[str]
    with open(config.list_path, encoding="utf-8") as list_file:
        words = [line.strip() for line in list_file]
    return words


def check_dictionary(guess: str) -> bool:
    if guess in dictionary:
        return True
    return False


def guess_validation(guess: str) -> bool:
    if guess == "igiveup":
        return True

    if len(guess) > 5:
        print("Length of word is too long, word must be five letters.")
        return False
    if len(guess) < 5:
        print("Length of word is too short, word must be five letters.")
        return False
    if not guess.isalpha():
        print("Word contains non-alphabet characters. Word should only contain characters in the English alphabet.")
        return False
    if not check_dictionary(guess):
        print("Word is not in dictionary. Please input a valid English word.")
        return False
    
    return True


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


def print_result(statuses, correct_letters, guess):
    i = 0    
    for status in statuses:
        print(guess[i] + " is " + str(status))
        i += 1

    if correct_letters == 5:
        print("You have guessed the word. You win!")


def process_guess(word: str, guess_no: int) -> int:
    print("Guess #" + str(guess_no) + ":")
    guess = input().lower()

    while not guess_validation(guess):
        print("Guess #" + str(guess_no) + ":")
        guess = input()

    if guess == "igiveup":
        return 5
    
    statusarray, correct_letters = test_guess(guess, word)

    print_result(statusarray, correct_letters, guess)

    return correct_letters


def run_game(config: Config):
    global dictionary 
    dictionary = read_list(config)

    word_number = randrange((len(dictionary) - 1))
    word = dictionary[word_number]

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
