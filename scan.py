from tkinter import filedialog
from dataclasses import dataclass

import main
from collections import Counter
import csv


@dataclass
class Syllable:
    name: str
    nb_prefix: int
    nb_suffix: int
    sound: str


@dataclass
class Sound:
    id: int
    name: str
    count: int
    typing: list[str]

    def __str__(self):
        return f"[{self.id}]{self.name}"


def store_sounds(sounds: list[Sound]):
    '''function to write a list of sound in a csv file
    as : sound, typing, typing, typing...'''
    '''choice = filedialog.askopenfilename(title="Choisir un fichier pour enregistrer la liste des sons")

    if choice == "":
        return'''
    choice = "C:/Users/Famille/Documents/Python/syllabes/sounds.csv"
    try:
        with open(choice, "w", encoding='utf-8', newline='') as file:
            write = csv.writer(file)

            for sound in sounds:
                write.writerow([sound.name, sound.count, *sound.typing])
    except PermissionError:
        choice = input("Erreur de permission: confirmez ?")
        if choice == "NO":
            exit()
        else:
            store_sounds(sounds)


def restore_sounds() -> list[Sound]:
    '''fonction to read a list of sound from a csv file'''
    sounds = list()

    choice = filedialog.askopenfilename(title="Choisir la liste des sons connus")

    if choice == "":
        return []

    # choice = "C:/Users/Famille/Documents/Python/orthographix/sounds.csv"
    print(choice)

    with open(choice, "r", encoding='utf-8') as file:
        reader = csv.reader(file)

        for index, line in enumerate(reader):
            if len(line) < 3:
                sound = Sound(index+1, line[0], int(line[1]), [line[0]])
            else:
                sound = Sound(index+1, line[0], int(line[1]), [syllable for syllable in line[2:] if syllable != ''])

            sounds.append(sound)

    display_sounds(sounds)

    return sounds


def display_sounds(sounds):
    # control display
    for sound in sounds:
        print(sound.id, sound.name, sound.typing, sound.count)


def restore_record(not_empty=False) -> list[Syllable]:
    # get from CSV all sounds already recorded
    syllables = list()

    choice = filedialog.askopenfilename(title="Choisissez votre sauvegarde")

    if choice == "":
        return []

    with open(choice, "r", encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for line in reader:
            syllable = Syllable(line['syllabe'],
                                line['nb_prefix'],
                                line['nb_suffix'],
                                line['sound'])

            if not_empty and syllable.sound == '':
                continue
            else:
                syllables.append(syllable)

    return syllables


def save_syllables(syllables: list):
    with open("sauvegarde.csv", "w", encoding='utf-8', newline='') as file:
        field_names = ['syllabe', 'nb_prefix', 'nb_suffix', 'sound']

        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()

        for syllable in syllables:
            writer.writerow({'syllabe': syllable.name,
                             'nb_prefix': syllable.nb_prefix,
                             'nb_suffix': syllable.nb_suffix,
                             'sound': syllable.sound})


def save_sounds(sounds_dict: dict):
    with open("sauvegarde-sound.csv", "w", encoding='utf-8', newline='') as file:
        field_names = ['syllabe', 'son']
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()

        for syllabe, sound in sounds_dict.items():
            writer.writerow({'syllabe': syllabe, 'son': sound})


def scan(word_list):
    debut = Counter(word[:5] for word in word_list)
    fin = Counter(word[-5:] for word in word_list)

    print(len(debut), len(fin))

    debuts = debut.most_common(200)
    fins = fin.most_common(200)
    return debuts, fins


def end(sounds_dict):
    save_sounds(sounds_dict)
    exit()


def initiate_db():
    word_list = main.open_list_in_txt("Choisir le dictionnaire")
    # sounds_dict = restore_record()

    debuts, fins = scan(word_list)

    syllables = dict()

    for debut in debuts:
        syllables[debut[0]] = Syllable(debut[0], debut[1], 0, '')

    for fin in fins:
        if fin[0] in syllables.keys():
            syllables[fin[0]].nb_suffix = fin[1]
        else:
            syllables[fin[0]] = Syllable(fin[0], 0, fin[1], '')

    save_syllables(sorted(syllables.values(),
                          key=lambda x: x.nb_prefix + x.nb_suffix,
                          reverse=True))


def create_sounds(syllables):
    sounds = dict()
    for syllable in syllables:
        if syllable.sound == '':
            continue
        if syllable.sound not in sounds.keys():
            sounds[syllable.sound] = [syllable]
        else:
            sounds[syllable.sound].append(syllable)

    return sounds


def type_sounds(syllables):
    for syllable in syllables:
        if syllable.sound is not None and syllable.sound != '':
            print(f"[{syllable.name}] est simplifié en {syllable.sound}")
            continue

        for sound in sounds.keys():
            if syllable.name.startswith(sound) or \
                    syllable.name.endswith(sound):
                proposition = \
                    input(f"[{syllable.name}]-"
                          f"{(syllable.nb_suffix + syllable.nb_prefix)} "
                          f"(entrée pour accepter : {sound} ) ")
                if proposition == "":
                    syllable.sound = sound
                    sounds[sound].append(syllable)
                else:
                    syllable.sound = proposition
                    if proposition in sounds.keys():
                        sounds[proposition].append(syllable)
                    else:
                        sounds[proposition] = [syllable]
                break
        else:
            proposition = \
                input(f"[{syllable.name}]-"
                      f"{(syllable.nb_suffix + syllable.nb_prefix)} ")
            if proposition != "":
                syllable.sound = proposition
                if proposition in sounds.keys():
                    sounds[proposition].append(syllable)
                else:
                    sounds[proposition] = [syllable]

            else:
                save_syllables(syllables)
                break


def update_syllable(syllables, name, sound):
    for syllable in syllables:
        if syllable.name == name:
            syllable.sound = sound
            break
    else:
        syllables.append(Syllable(name, 0, 0, sound))


def check_sound(proposition):
    for sound in sounds:
        if sound.name == proposition:
            return sound
    return None


def add_new_sound(proposition: str, word: str, is_prefix: bool):
    # process to use propositions with a proposition for prefix or suffix
    typing = word[:3] if is_prefix else word[-3:]
    try:
        proposition = int(proposition)
        # so an int have been given, it's a know sound, I add the typing to its syllable
        sound = sounds[proposition - 1]
        assert sound.id == proposition
        if typing not in sound.typing:
            sound.typing.append(typing)
        sound.count += 1
        print(f"J'ai incrémenté le compteur de {sound.name}, il vaut maintenant {sound.count}.")
    except ValueError:
        # so a string have been given, that's a new sound
        sound = check_sound(proposition)
        if sound is None:
            sound = Sound(len(sounds) + 1, proposition, 1, [typing])
            print(f"J'ai créé un nouveau son '{sound.name}' qui correspond "
                  f"au {'prefix' if is_prefix else 'suffix'} {typing}.")
            sounds.append(sound)
        else:
            sound.typing.append(typing)
            sound.count += 1
            print(f"J'ai incrémenté le compteur de {sound.name}, il vaut maintenant {sound.count}.")



def clean_list(words, test=False):
    length = len(words)
    for word in words:
        if word.endswith("s"):
            if word[:-1] in words:
                words.remove(word)
                if test:
                    print(word)
        elif word.endswith("ée"):
            if word[:-1] in words:
                words.remove(word)
                if test:
                    print(word)
        elif word.endswith("ées"):
            if word[:-2] in words:
                words.remove(word)
                if test:
                    print(word)
        elif word.endswith("er"):
            if word[:-2]+"é" in words:
                words.remove(word)
                if test:
                    print(word)
        elif word.endswith("ent"):
            if word[:-2] in words:
                words.remove(word)
                if test:
                    print(word)
        elif word.endswith("aient"):
            words.remove(word)
        elif word.endswith("ait"):
            if word[:-3]+"er" in words or word[:-3]+"é" in words:
                words.remove(word)
        elif ' ' in word:
            words.remove(word)

    print(f"J'ai supprimé {length - len(words)} mots, il en reste {len(words)}")

    return words


if __name__ == '__main__':
    # initiate_db()
    # syllables = restore_record(not_empty=True)
    # sounds = create_sounds(syllables)
    # print(f"On a déjà {len(sounds)} syllabes prêtes !")

    sounds = restore_sounds()

    words = main.open_list_in_txt("Liste de mots",
                                  "C:/Users/Famille/Documents/Python/syllabes/liste.txt")
    # words = clean_list(words)
    # words = clean_list(words)
    # words = clean_list(words)

    # main.store_list_in_txt(words, "Liste de mots")
    # exit()

    for index, word in enumerate(words):
        prefix_sound = None
        suffix_sound = None
        matches = 0
        for sound in sounds:
            if prefix_sound is None and any(word.startswith(x) for x in sound.typing):
                matches += 1
                prefix_sound = sound
            if suffix_sound is None and any(word.endswith(x) for x in sound.typing):
                matches += 1
                suffix_sound = sound
            if matches == 2:
                print(f"Pour le mot {word},")
                prefix_sound.count += 1
                print(f"J'ai incrémenté le compteur de {prefix_sound.name}, il vaut maintenant {prefix_sound.count}.")
                suffix_sound.count += 1
                print(f"J'ai incrémenté le compteur de {suffix_sound.name}, il vaut maintenant {suffix_sound.count}.")
                break

        if matches == 2:
            continue

        print()
        print(f"{index}/{len(words)} Pour le mot {word}, vous avez {matches} cartes : {prefix_sound} et {suffix_sound}")
        new_sound = input("Voulez-vous modifier ?")

        while new_sound == 'DISPLAY':
            display_sounds(sounds)
            print(f"Pour le mot {word}, vous avez {matches} cartes : {prefix_sound} et {suffix_sound}")
            new_sound = input("Voulez-vous modifier ?")

        if new_sound == 'NO':
            continue

        if new_sound == '':
            store_sounds(sounds)
            exit()

        if new_sound == 'Q':
            exit()

        try:
            prefix_proposition, suffix_proposition = new_sound.split(' ')
        except ValueError:
            store_sounds(sounds)
            exit()

        add_new_sound(prefix_proposition, word, is_prefix=True)
        add_new_sound(suffix_proposition, word, is_prefix=False)



"""
    for debut in debuts:
        if debut[0] in sounds_dict.keys():
            print(f"{debut[0]} est déjà simplifié en {sounds_dict[debut[0]]}")
            continue

        proposition = input(f"[{debut}] ")

        if proposition == "":
            continue

        if proposition == "1":
            end(sounds_dict)

        sounds_dict[debut[0]] = proposition
"""
