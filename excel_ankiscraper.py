from bs4 import BeautifulSoup
import requests
import html2text
import re
from jmd_imagescraper.core import * # dont't worry, it's designed to work with import *
from pathlib import Path
from PIL import Image
import glob
import psutil
import os
import pandas as pd
from pyforvo import Forvo
import random

# Creating unique identifyer for image and audio files
unique_identifyer = random.randint(0,10000)

# adding forvo API
filePath = "api.txt"
textFile = open(filePath)
api_key = textFile.read()
textFile.close()
api_key = api_key.replace("\n", "")


excel_folder = Path().cwd()/"vocab"
df = pd.read_excel(excel_folder/"frenchkindle.xlsx")

words_later = ""
prompt = ""
ankicards = ""
row_number = 0
while prompt != "q":
    new_search = "y"
    while new_search == "y":
        word = df["word"][row_number]
        usage = df["usage"][row_number]
        print("\n\n" + "Word: " + word)
        wordreplace = "**" + word + "**"
        usage = usage.replace(word, wordreplace)
        print("\n"+ "Usage:" + usage + "\n")
        decision = input("Do you want to add this word? Press enter to confirm, m to move to next sentence, or t to type word: ")
        if decision == "t":
            search = input("Type word to search for: ")
            new_search = "n"
        if decision == "m":
            new_search = "y"
        elif decision != "t" and decision != "m":
            search = word
            new_search = "n"
        row_number = row_number +1
    result = requests.get("https://www.wordreference.com/fren/" + search)
    content = result.content
    soup = BeautifulSoup(content, features="lxml")
    string = soup.prettify()
    samples = soup.find(id="articleWRD")
    word = soup.select_one(".FrWrd strong").get_text()
    word = word.replace("⇒", "")
    word = word.replace("/", " ou ")
    if word != search:
        check_word = input("Suggested word: " + word + ". Do you want to use this? Press any key, or press n to continue using input term")
        if check_word == "n":
            word = search
    # Finding how many word instances (they are tagget with fren: + a number):
    numbers = []
    number_string = string
    while number_string.find('id="fren:') != -1:
        id_start = number_string.find('id="fren:')
        number_start = id_start + 9
        number_end = number_string.find('"', number_start)
        number = number_string[number_start:number_end]
        numbers.append(number)
        number_string = number_string[number_end:len(number_string)]

    print(str(len(numbers)) + " definitions found.")
    input("Press enter to show definitions: ")

    main_list = []
    temp_list = []
    number_iterator = 0
    stop = ""
    first_iterator_save = 0
    second_iterator_save = 0
    full_length = len(numbers)
    current_length = 0
    limit_iterator = 0
    iterator = 0
    choice = "s"
    while number_iterator < full_length and choice == "s": # Makes it iterate through all the words found
        print_iterator = 0 + len(main_list)
        # French Word
        current_length = full_length - len(main_list)
        if current_length < 5:
            max_five = current_length
        else:
            max_five = 5
        limit_iterator = 0
        while limit_iterator < max_five:
            fre_word_number = "#fren\:" + numbers[number_iterator]
            fre_word_path = fre_word_number + " > td.FrWrd > strong" # This is the css selector pattern for the French word
            fre_word = soup.select_one(fre_word_path).get_text() # This selects the actual text
            fre_word = fre_word.replace("⇒", "")
            # print("Word: " + fre_word)
            temp_list.append(fre_word)
            # French definition
            def_path = fre_word_number + " > td:nth-child(2)" # This is the css selector pattern for the definition of the word above
            definition = soup.select_one(def_path).get_text()
            definition = definition.replace("(", "")
            definition = definition.replace(")", "")
            # print("Definition: " + definition)
            temp_list.append(definition)
            # English definition
            eng_def_path = fre_word_number + " > td.ToWrd"
            eng_def = soup.select_one(eng_def_path).get_text()
            eng_remove = soup.select_one(eng_def_path + "> em").get_text()
            eng_def = eng_def.replace(eng_remove, "")
            eng_def = eng_def.replace("⇒", "")
            # Note that this only gives the first English definition given. It is much harder to find the next ones... Might figure out later
            # print("English definition: " + eng_def)
            temp_list.append(eng_def)
            # French Sentence:
            # It is much harder to get this one right, because there is no obvious way to where it is found in the css selector tree... But we are trying to find a workaround
            fre_sen = ""
            first_table_test = ""
            if first_iterator_save != 0:
                first_iterator = first_iterator_save # i.e., if this is not the first search, then we start were we left off.
            else:
                first_iterator = 1 # We start at 1, not zero
            # print("ITERATOR:" + str(first_iterator)) # To check
            while first_iterator < 50: # There is never more than 50 instances
                first_table_path = "#articleWRD > table:nth-child(" + str(first_iterator) + ")" # Checks the first part of the table.
                first_table_test = soup.select_one(first_table_path) # If the first part of the table exists...
                if first_table_test is not None:
                    if second_iterator_save != 0:
                        second_iterator = second_iterator_save +1
                    else:
                        second_iterator = 1
                    while second_iterator < 50:
                        # print("HER: " + soup.select_one(first_table_path).get_text())
                        second_table_path = first_table_path + " > tr:nth-child(" + str(second_iterator) + ") > td.FrEx" #We then check for the second part of the table.
                        # print("PATH: " + second_table_path)
                        second_table_test = soup.select_one(second_table_path)
                        if second_table_test is not None:
                            fre_sen = soup.select_one(second_table_path).get_text()
                            second_iterator_save = second_iterator +1
                            second_iterator = 100
                            first_iterator_save = first_iterator
                            first_iterator = 100
                        second_iterator = second_iterator +1
                        if second_iterator == 49:
                            second_iterator_save = 0 #i.e. if the first part of the css selector goes up one, the second part is also reset.
                first_iterator = first_iterator +1
            temp_list.append(fre_sen)
            number_iterator = number_iterator +1
            limit_iterator = limit_iterator + 1
            main_list.append(temp_list)
            temp_list = []
        current_iterator = print_iterator + max_five
        while print_iterator < current_iterator:
            print("\n")
            print("Definition " + str(print_iterator +1) + ":")
            print("Word: " + main_list[print_iterator][0])
            print("French definition: " + main_list[print_iterator][1])
            print("English definition: " + main_list[print_iterator][2])
            print("French sentence: " + main_list[print_iterator][3])
            print_iterator = print_iterator +1
        choice = input("\nDo you want to pick one of these definitions? Press the corresponding number, press enter to select the first of the definitions listed here or s to scroll further: ")
        if choice == "s":
            if number_iterator == full_length:
                print("No more definitions. Beginning from top")
                number_iterator = 0
                limit_iterator = 0
                main_list = []
    #Picking a definition
    pick = ""
    while pick == "":
        if choice == "":
            choice = current_iterator - max_five +1
        try:
            choice = int(choice)
            if choice > len(numbers):
                choice = input("Please enter a number between 1 and " + str(len(numbers)))
                pick = ""
            else:
                pick = choice -1
                fre_word = main_list[pick][0]
                fre_def = main_list[pick][1]
                eng_def = main_list[pick][2]
                fre_sen = main_list[pick][3]
        except ValueError:
            choice = input('Please enter a non-decimal number')
            pick = ""

    print("\n\nWord: " + fre_word)
    print("French definition: " + fre_def)
    print("English definition: " + eng_def)
    print("French sentence: " + fre_sen)

    sentence_decision = input("\n\nDo you want to use this sentence? Press any key to continue, or 't' to type a new one: ")
    if sentence_decision == "t":
        fre_sen = input("Type the new sentence: ")

    keyword = fre_word[0:(len(fre_word)-2)]
    if fre_sen.find(keyword) != -1:
        remove_word_start = fre_sen.find(keyword)
        # Intervention to make sure one can search for expressions, i.e. more than one word
        if fre_sen.find(fre_word) != -1:
            fre_sen_remove = fre_sen.replace(fre_word, "PLACEHOLDER")
        else:
            fre_sen_remove = fre_sen.replace(keyword, "PLACEHOLDER")
        remove_word_end = fre_sen_remove.find(" ", remove_word_start)
        if remove_word_end == -1:
            remove_word_end = fre_sen_remove.find(".", remove_word_start)
        remove_word = fre_sen_remove[remove_word_start:remove_word_end]
        sentence_keyword_removed = fre_sen_remove.replace(
            remove_word, "___")
        print("Sentence with keyword removed: " +
              sentence_keyword_removed + "\n")
        ok = input("Is this OK? Press enter to continue or 't' to type the sentence with keyword removed yourself")
    else:
        sentence_keyword_removed = input("Keyword not found! Please type the sentence with the keyword removed")

    # Finding pronunciation IPA
    url = "https://fr.wiktionary.org/wiki/" + word
    result = requests.get(url)
    content = result.content
    soup = BeautifulSoup(content, features="lxml")
    pron = soup.find(class_='API')
    if pron != None:
        pron = pron.get_text()
        print("\nPronunciation: " + pron)
    else:
        print("\nPronunciation not found!")
        pron = ""

    # Finding gender
    gender = soup.find_all(class_ = "ligne-de-forme")
    if gender is not None:
        try:
            gender = gender[0].get_text()
            if gender =="féminin":
                gender = "une"
            elif gender == "masculin":
                gender = "un"
            else:
                gender = ""
                print("Gender: " + gender)
        except IndexError:
            gender = ""
    else:
        gender = ""
    # Adding images
    search = ""
    img_prompt = input(
        "\nPress enter to search for an image using the same term, press q to skip, or type an alternative search string: ")
    if img_prompt == "":
        search = word
    elif img_prompt == "q":
        search = ""
        image_name = ""
    else:
        search = img_prompt
    if search != "":
        image_name = ""
        cont = ""
        while cont != "q":
            if cont == "a":
                search = input("Give new search string: ")
                root_folder = str(root)
                dir_name = root_folder + "/" + word
                remove_images = os.listdir(dir_name)
                for item in remove_images:
                    if item.endswith(".jpg"):
                        os.remove(os.path.join(dir_name, item))
            root = Path().cwd()/"images_temp"
            duckduckgo_search(root, word, search, max_results=10)
            image_folder = Path().cwd()/"images_temp"/word
            images_jpg = "images_temp/" + word + "/*.jpg"
            images = glob.glob(images_jpg)
            cont = ""
            number_images = len(images)
            iterator = 0
            while cont != "q" and cont != "a":
                if iterator == number_images:
                    print("no more images to display, starting again")
                    iterator = 0
                im = Image.open(images[iterator])
                im.show()
                cont = input(
                    "\nPress enter to scroll to next image, s to save, q to quit, or a to give a new search string ")
                if cont == "s":
                    image_name = word + str(unique_identifyer) + ".jpg"
                    im.save(image_name)
                    cont = "q"
                for proc in psutil.process_iter():
                    if proc.name() == "display":
                        proc.kill()
                iterator = iterator + 1
        if image_name != "":
            basewidth = 130
            img = Image.open(image_name)
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(image_name)
            imagefolder = Path().cwd()/"images"
            os.rename(image_name, imagefolder/image_name)
        # Removes images that are not used
        root_folder = str(root)
        dir_name = root_folder + "/" + word
        remove_images = os.listdir(dir_name)
        for item in remove_images:
            if item.endswith(".jpg"):
                os.remove(os.path.join(dir_name, item))
        # Gjør bildet lesbart for anki:
        image_name_anki = "<img src=" + '"' + image_name + '">'
    # Legger inn forvo:
    audio_prompt = input("\nDo you want to search forvo.com for pronunciation? Press enter to search for your current term, or type a new term, or press n to skip: ")
    newaudioname = ""
    if audio_prompt != "n":
        if audio_prompt == "":
            audiosearch = word
        elif audio_prompt != "" and audio_prompt != "n":
            audiosearch = audio_prompt
        forvo = Forvo(api_key)
        #Play pronunciation (only supports Linux with mplayer installed)
        audio = forvo.get_pronunciation(audiosearch, language='fr')
        audio.play()
        # Download audio
        # Set download folder
        main_folder = Path().cwd()
        audiofolder = Path().cwd()/"audio"
        dwnld = input("\nDo you want to save the file? Press s: ")
        if dwnld == "s":
            audio = forvo.get_pronunciation(audiosearch, language = "fr")
            audio.download(fmt="mp3")
        for file in os.listdir(main_folder):
            if file.endswith(".mp3"):
                audioname = os.path.join(main_folder, file)
                newaudioname = word + str(unique_identifyer) + ".mp3"
                os.rename(audioname, audiofolder/newaudioname)
                ankiaudio = "[sound:" + newaudioname + "]"
                pron = pron + ankiaudio
    two_cards = input("Do you want to make two cards? Press s: ")
    if two_cards == "s":
        two_cards = "y"
    else:
        two_cards = ""
    # New prompt?
    prompt = input(
        "Do you want to make another card? Press enter to continue, x to discard current card and start again, or q to quit: ")
    if prompt != "x":
        # Making cards:
        empty = ""
        ankicard = sentence_keyword_removed + "|" + image_name_anki + "|" + fre_def + "|" + fre_word + "|" + gender + "|" + fre_sen + "|" + pron + "|" + two_cards + "|" + empty + "|" + empty + "|" + empty + "|" + eng_def + "|" + empty
        # The empty fields are optional fields that can be modified later
        ankicards = ankicards + ankicard + "\n"
        text_file = open("ankideck.txt", "w")
        n = text_file.write(ankicards)
        text_file.close()
    else:
        if newaudioname != "":
            if os.path.exists(audiofolder/newaudioname):
                os.remove(audiofolder/newaudioname)
        if image_name != "":
            if os.path.exists(imagefolder/image_name):
                os.remove(imagefolder/image_name)
