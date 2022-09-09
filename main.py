from random import choice
from tkinter import filedialog

def store_list_in_txt(list, text="enregistrer"):
    choice = filedialog.askopenfilename(title=text)

    if choice is None or choice == '':
        return

    with open(choice, "w", encoding='utf-8') as file:

        for line in list:
            file.write(f"{line}\n")


def open_list_in_txt(text="Ouvrir", choice: str= None) -> list[str]:
    if choice is None:
        choice = filedialog.askopenfilename(title=text)

        if choice is None or choice == '':
            return list()

    with open(choice, "r", encoding='utf-8') as file:
        raw_list = []

        for line in file:
            raw_list.append(line.strip().lower())

    return raw_list


def get_a_word() -> (str, list):
    """returns the word to find"""
    raw_list = open_list_in_txt()

    new_list = [word for word in raw_list if 4 < len(word) < 11 and
                word.count('-') == 0]

    small_list = open_list_in_txt()

    word_to_find = ''
    while word_to_find not in raw_list:
        word_to_find = choice(small_list)

    return word_to_find, raw_list, small_list


def LCSLength(proposition, word_to_find, m=None, n=None):
    if m is None:
        m = len(proposition)
    if n is None:
        n = len(word_to_find)

    # retour si la fin de l'une ou l'autre des séquences est atteinte
    if m == 0 or n == 0:
        return 0

    # si le dernier caractère de `proposition` et `word_to_find` correspond
    if proposition[m - 1] == word_to_find[n - 1]:
        return LCSLength(proposition, word_to_find, m - 1, n - 1) + 1

    # sinon,
    return max(LCSLength(proposition, word_to_find, m - 1, n),
               LCSLength(proposition, word_to_find, m, n - 1))


def get_score_nb_letters(proposition: str,
                         word_to_find: str,
                         nb: int) -> int:
    """function to check how many letters are correct in the proposition
    :param proposition: str given by user (lowercase)
    :param word_to_find: str from game (lowercase)
    :param nb: size of the slices to check

    :returns score: 1pt by correct slice
    """
    score = 0
    chars = set(
        proposition[x:x + nb] for x in range(0, len(proposition) - nb + 1))

    for char in chars:
        nb_in_proposition = proposition.count(char)
        nb_in_word_to_find = word_to_find.count(char)
        matching_chars = min(nb_in_word_to_find, nb_in_proposition)

        score += matching_chars

    return score


def get_score_each_letter(proposition: str,
                          word_to_find: str) -> float:
    """function to check how many letters are correct in the proposition
    :param proposition: str given by user (lowercase)
    :param word_to_find: str from game (lowercase)

    :returns score: float as 1pt for correct letter - 0,5 for incorrect letter
    """
    score = 0
    if len(word_to_find)>len(proposition):
        max_word = word_to_find
        min_word = proposition
    else :
        max_word = proposition
        min_word = word_to_find

    chars = set(x for x in max_word)

    for char in chars:
        nb_in_max_word = max_word.count(char)
        nb_in_min_word = min_word.count(char)
        correct_letters = min(nb_in_min_word, nb_in_max_word)
        incorrect_letters = nb_in_max_word - nb_in_min_word
        this_char_score = correct_letters - incorrect_letters * 0.5
        score += this_char_score

    return score


def get_score(proposition, word_to_find) -> float:
    """Compares two strings and gives a score as :
    1pt for correct letter - 0.5pt for incorrect letter
    2 pts for correct two letters suit
    4 pts for correct three letters suit
    """
    score = 0

    score += get_score_each_letter(proposition, word_to_find)

    for x in range(2, min(3, len(proposition), len(word_to_find))):
        score += get_score_nb_letters(proposition, word_to_find, x) * x

    return score


def display_best_answer(best_answer: dict):
    """Display 10 best proposition scores"""
    scores = list(best_answer.keys())
    scores.sort()
    scores = scores[-10:]

    for score in scores:
        print(f"{best_answer[score]} : {score:.2f} %")


def game():
    tries = 0
    word_to_find, words, simple_words = get_a_word()

    simple_words.sort(key=lambda x: get_score(x, word_to_find))
    # words.sort(key=lambda x: LCSLength(x, word_to_find))

    max_score = get_score(word_to_find, word_to_find)
    # max_score_bis = LCSLength(word_to_find, word_to_find)

    # a dict to record answers as score:proposition
    best_answers = dict()
    while True:
        proposition = input("Quel mot proposez-vous ? ").lower()

        if proposition == "":
            print(f"*** La solution est : {word_to_find} ***")
            continue

        if proposition == "help":
            for x in range(100, 1, -1):
                print(words[-x])

        if proposition not in words:
            if proposition == "aa":
                exit()
            else:
                print(f"Je ne connais pas {proposition}")
                continue

        score = get_score(proposition, word_to_find)
        # score_bis = LCSLength(proposition, word_to_find)
        tries += 1

        # score = (score / max_score) * 50
        score = score*100/max_score
        scoreB = len(words)-words.index(proposition)

        if score in best_answers.keys():
            best_answers[score].append(proposition)
        else:
            best_answers[score] = [proposition]


        """print(f"(n°{tries}) {proposition} rapporte : "
              f"{score:.1f} %")

        print(f"OU (n°{tries}) {proposition} rapporte : "
              f"{(score_bis / max_score_bis) * 50 + (score / max_score) * 50:.1f} %")"""
        print()
        display_best_answer(best_answers)
        print()

        if scoreB > 1000:
            print(f"(n°{tries}) {proposition} rapporte : "
                  f"{score:.2f} %")
        elif scoreB > 1:
            print(f"(n°{tries}) {proposition}  : {scoreB} !!!")
        else:
            print(f"BRAVO, c'était bien {word_to_find} !!")


if __name__ == "__main__":
    game()
