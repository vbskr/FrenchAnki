# main_script.py

import os
import random
import psutil
import send2trash
import requests
import bs4
from PIL import Image
from pyforvo import Forvo
from playsound import playsound
from instance import Instance
from utils import (
    extract_even_odd,
    rreplace,
    check_new_line,
    find_fre_word,
    find_gender,
    check_dsense,
    check_extra_def_info,
    find_fre_def,
    find_eng_word,
    find_fre_sen,
    find_eng_sen,
    unpack_line,
    make_instance,
    unpack_lines,
    return_fre_sen_keyword_removed,
    collage_method,
    search_and_download_images,
    image_search,
    find_ipa,
    api_check,
    get_forvo,
)


anki_cards = ""
while True:
    search_term = input("Please type the word you want to search for: ")
    search = "https://www.wordreference.com/fren/" + search_term
    res = requests.get(search)
    soup = bs4.BeautifulSoup(res.text, "lxml")
    lines = extract_even_odd(soup)
    instances = unpack_lines(lines)
    if len(instances) == 0:
        print("No instances found. Try searching for another word.\n")
        pass
    else:
        print(f"{len(instances)} instances found\n")
        while True:
            for instance in instances:
                instance.show_instance()
                choice = input("\nWould you like to keep this definition? Press enter to save or s to scroll to the next\n")
                if choice == "":
                    word = instance
                    break
                else:
                    continue
            if choice == "":
                break
            else:
                print("No more definitions found. Starting from the beginning.\n")
        fre_sen_keyword_removed = return_fre_sen_keyword_removed(instance.fre_sen, instance.fre_word)
        instance.add_fre_sen_keyword_removed(fre_sen_keyword_removed)
        print("\n")
        if find_ipa(soup) is not False:
            ipa = find_ipa(soup)
            print(f"IPA: {ipa}")
            instance.add_ipa(ipa)
        else:
            print("IPA not found")
        image = image_search(search_term)
        instance.add_image(image)
        if api_check() is not False:
            api_key = api_check()
            pron = get_forvo(search_term, api_key)
            instance.add_pron(pron)
        instance.check_two_cards()
        anki_card = instance.make_anki_card()
        save = input("\nDo you want to save this card? Press any key, or q to abort")
        if save != "q":
            if anki_cards == "":
                anki_cards = anki_card
            else:
                anki_cards = anki_cards + "\n" + anki_card
            text_file = open("ankideck.txt", "w")
            n = text_file.write(anki_cards)
            text_file.close()
        cont = input("Do you want to continue? Press q to quit or any key to continue")
        if cont == "q":
            break
        else:
            continue
        
    
    
    

# %%

