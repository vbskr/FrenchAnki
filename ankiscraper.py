from bs4 import BeautifulSoup
import requests
import html2text
import re
from jmd_imagescraper.core import duckduckgo_search
from pathlib import Path
from PIL import Image
import glob
import psutil
import os

prompt = ""
ankicards = ""
newsearch = ""
while prompt != "q":
    inp = input("Hvilket ord vil du søke opp? ")

    # Definerer de cookiene jeg trenger:

    url = "https://www.wordreference.com/fren/" + inp
    result = requests.get(url)
    content = result.content
    soup = BeautifulSoup(content, features="lxml")

    samples = soup.find(id="articleWRD")
    word = soup.select_one(".FrWrd strong").get_text()

    sample = samples.get_text()

    # print(html2text.html2text(sample))

    # This is our string:
    string = html2text.html2text(sample)
    originalstring = string

    # String cleaning:
    # Clear linebreaks
    while string.find("\n") != -1:
        string = string.replace("\n", " ")
    # Managing quotation marks:
    while string.find('"') != -1:
        string = string.replace('"', "DOUBLE2")
    while string.find("'") != -1:
        string = string.replace("'", "SINGLE1")

    phrases_to_remove = [
        "traductionsFrançaisAnglais",
        "verbe transitif: verbe qui sSINGLE1utilise avec un complément dSINGLE1objet direct (COD). Ex : DOUBLE2JSINGLE1écris une lettreDOUBLE2. DOUBLE2Elle a retrouvé son chatDOUBLE2.",
        "vtrtransitive verb: Verb taking a direct object--for example, DOUBLE2Say something.DOUBLE2 DOUBLE2She found the cat.DOUBLE2",
        "verbal expression: Phrase with special meaning functioning as verb--for example, DOUBLE2put their heads together,DOUBLE2 DOUBLE2come to an end.DOUBLE2",
        "verbe pronominal: verbe qui sSINGLE1utilise avec le pronom réfléchi DOUBLE2seDOUBLE2, qui sSINGLE1accorde avec le sujet. Ex : se regarder : DOUBLE2Je me regarde dans le miroir. Tu te regardes dans le miroir.DOUBLE2. Les verbes pronominaux se conjuguent toujours avec lSINGLE1auxiliaire DOUBLE2êtreDOUBLE2. Ex : DOUBLE2Elle a lavé la voitureDOUBLE2 mais DOUBLE2Elle sSINGLE1est lavée.DOUBLE2",
        ": Verb with adverb(s) or preposition(s), having special meaning, divisible--for example, DOUBLE2call offDOUBLE2 [=cancel], DOUBLE2call the game off,DOUBLE2 DOUBLE2call off the game.DOUBLE2",
        "nmnom masculin: sSINGLE1utilise avec les articles DOUBLE2leDOUBLE2, DOUBLE2lSINGLE1DOUBLE2 (devant une voyelle ou un h muet), DOUBLE2unDOUBLE2. Ex : garçon - nm > On dira DOUBLE2le garçonDOUBLE2 ou DOUBLE2un garçonDOUBLE2. ",
        "nnoun: Refers to person, place, thing, quality, etc. ",
        "adjadjectif: modifie un nom. Il est généralement placé après le nom et sSINGLE1accorde avec le nom (ex : un ballon bleu, une balle bleue). En général, seule la forme au masculin singulier est donnée. Pour former le féminin, on ajoute DOUBLE2eDOUBLE2 (ex : petit > petite) et pour former le pluriel, on ajoute DOUBLE2sDOUBLE2 (ex : petit > petits). Pour les formes qui sont DOUBLE2irrégulièresDOUBLE2 au féminin, celles-ci sont données (ex : irrégulier, irrégulière > irrégulier = forme masculine, irrégulière = forme féminine)",
        "adjadjectif: modifie un nom. Il est généralement placé après le nom et sSINGLE1accorde avec le nom (ex : un ballon bleu, une balle bleue). En général, seule la forme au masculin singulier est donnée. Pour former le féminin, on ajoute DOUBLE2eDOUBLE2 (ex : petit > petite) et pour former le pluriel, on ajoute DOUBLE2sDOUBLE2 (ex : petit > petits). Pour les formes qui sont DOUBLE2irrégulièresDOUBLE2 au féminin, celles- ci sont données (ex : irrégulier, irrégulière > irrégulier = forme masculine, irrégulière = forme féminine)",
        "adjadjective: Describes a noun or pronoun--for example, DOUBLE2a tall girl,DOUBLE2 DOUBLE2an interesting book,DOUBLE2 DOUBLE2a big house.DOUBLE2 ",
        "adjadjective: Describes a noun or pronoun-- for example, DOUBLE2a tall girl,DOUBLE2 DOUBLE2an interesting book,DOUBLE2 DOUBLE2a big house.DOUBLE2 ",
        "nfnom féminin: sSINGLE1utilise avec les articles DOUBLE2laDOUBLE2, DOUBLE2lSINGLE1DOUBLE2 (devant une voyelle ou un h muet), DOUBLE2uneDOUBLE2. Ex : fille - nf > On dira DOUBLE2la filleDOUBLE2 ou DOUBLE2une filleDOUBLE2. Avec un nom féminin, lSINGLE1adjectif sSINGLE1accorde. En général, on ajoute un DOUBLE2eDOUBLE2 à lSINGLE1adjectif. Par exemple, on dira DOUBLE2une petite filleDOUBLE2. ",
        "nfnom féminin: sSINGLE1utilise avec les articles DOUBLE2laDOUBLE2, DOUBLE2lSINGLE1DOUBLE2 (devant une voyelle ou un h muet), DOUBLE2uneDOUBLE2. Ex : fille - nf > On dira DOUBLE2la filleDOUBLE2 ou DOUBLE2une filleDOUBLE2. Avec un nom féminin, lSINGLE1adjectif sSINGLE1accorde. En général, on ajoute un DOUBLE2eDOUBLE2 à lSINGLE1adjectif. Par exemple, on dira DOUBLE2une petite filleDOUBLE2. ",
        "conjconjunction: Connects words, clauses, and sentences--for example, DOUBLE2and,DOUBLE2 DOUBLE2but,DOUBLE2 DOUBLE2because,DOUBLE2 DOUBLE2in order that.DOUBLE2 in the manner of, following the example of ",
        "exprexpression: Prepositional phrase, adverbial phrase, or other phrase or expression--for example, DOUBLE2behind the times,DOUBLE2 DOUBLE2on your own.DOUBLE2 ",
        "advadverbe: modifie un adjectif ou un verbe. Est toujours invariable ! Ex : DOUBLE2Elle est très grande.DOUBLE2 DOUBLE2Je marche lentement.DOUBLE2 ",
        "advadverb: Describes a verb, adjective, adverb, or clause--for example, DOUBLE2come quickly,DOUBLE2 DOUBLE2very rare,DOUBLE2 DOUBLE2happening now,DOUBLE2 DOUBLE2fall down.DOUBLE2 ",
        "preppreposition: Relates noun or pronoun to another element of sentence--for example, DOUBLE2a picture of John,DOUBLE2 DOUBLE2She walked from my house to yours.DOUBLE2 ",
        "viverbe intransitif: verbe qui sSINGLE1utilise sans complément dSINGLE1objet direct (COD). Ex : DOUBLE2Il est parti.DOUBLE2 DOUBLE2Elle a ri.DOUBLE2 ",
        "viintransitive verb: Verb not taking a direct object--for example, DOUBLE2She jokes.DOUBLE2 DOUBLE2He has arrived.DOUBLE2 ",
        "Note: Followed by SINGLE1onSINGLE1, SINGLE1uponSINGLE1, or SINGLE1aroundSINGLE1 ",
    ]

    for i in phrases_to_remove:
        while string.find(i) != -1:
            string = string.replace(i, "ENDPART")

    # Managing quotation marks again:
    while string.find("DOUBLE2") != -1:
        string = string.replace("DOUBLE2", '"')
    while string.find("SINGLE1") != -1:
        string = string.replace("SINGLE1", "'")

    # Other things to remove:
    phrases_to_remove = [
        "ⓘCette phrase n'est pas une traduction de la phrase originale.",
        "Un oubli important ? Signalez une erreur ou suggérez une amélioration. Traductions supplémentairesFrançaisAnglais",
        "⇒",
    ]

    for i in phrases_to_remove:
        while string.find(i) != -1:
            string = string.replace(i, "")

    # Finding definitions:
    next = "m"
    while next == "m":
        # French Definition
        definition_start = string.find("(")
        definition_end = string.find(")", definition_start)
        definition = string[(definition_start + 1):(definition_end)]
        print("French Definition: " + definition + "\n")
        # English Definition:
        eng_def_start = definition_end + 1
        eng_def_end = string.find("ENDPART", definition_end)
        eng_def = string[eng_def_start:eng_def_end]
        # if eng_def.find("⇒") != -1:
        #     eng_def = eng_def[0:(eng_def.find("⇒"))]
        next_eng_def_start = eng_def_end + 7
        next_eng_def_end = string.find("ENDPART", next_eng_def_start)
        next_search = string[next_eng_def_start:next_eng_def_end]
        check_dots = re.search('[.!?]', next_search)
        while check_dots == None:
            eng_def_new = (string[(next_eng_def_start):next_eng_def_end])
            eng_def = eng_def + ", " + eng_def_new
            next_eng_def_start = next_eng_def_end + 7
            next_eng_def_end = string.find("ENDPART", next_eng_def_start)
            next_search = string[next_eng_def_start:next_eng_def_end]
            check_dots = re.search('[.!?]', next_search)
            eng_def = eng_def.replace(" ,", ",")
        print("English Definition: " + eng_def + "\n")
        # French Sentence:
        # Finding end of sentence, checking if there are more than one sentence for each language
        string = string[next_eng_def_start:len(string)]
        sentence_end = string.find("ENDPART", 0)
        search = string[0:sentence_end]
        find_all_dots = re.findall('[.!?]', search)
        number_sentences = len(find_all_dots)/2
        if find_all_dots == 3:
            iterator = 1
        else:
            iterator = number_sentences
        if re.search('([A-Z][^.!?]+)', search) != None:
            # Passer på å begynne der det er en stor bokstav
            fre_sen_start_reg = re.search('([A-Z][^.!?]+)', search).span()
            fre_sen_start = fre_sen_start_reg[0]
        else:
            print("Did not find start of French sentence. Please type manually: ")
            fre_sen_start = 0
        number = 1
        OK = "undetermined"
        while iterator != 0 and re.search('[.!?]', search) != None and OK != "":
            fre_sen_end = re.search('[.!?]', search).span()
            fre_sen_end_result = re.search('[.!?]', search)
            fre_sen_end = fre_sen_end[0] + 1
            fre_sen = search[fre_sen_start:fre_sen_end]
            print("French Sentence " + str(number) + ": " + fre_sen + "\n")
            number = number + 1
            search = search.replace(fre_sen, "")
            iterator = iterator - 1
            # French Sentence: Remove keyword:
            keyword = word[0:(len(word)-2)]
            if fre_sen.find(keyword) != 1:
                remove_word_start = fre_sen.find(keyword)
                # Intervention to make sure one can search for expressions, i.e. more than one word
                if fre_sen.find(word) != -1:
                    fre_sen_remove = fre_sen.replace(word, "PLACEHOLDER")
                else:
                    fre_sen_remove = fre_sen.replace(keyword, "PLACEHOLDER")
                remove_word_end = fre_sen_remove.find(" ", remove_word_start)
                remove_word = fre_sen_remove[remove_word_start:remove_word_end]
                sentence_keyword_removed = fre_sen_remove.replace(
                    remove_word, "___")
                print("Sentence with keyword removed: " +
                      sentence_keyword_removed + "\n")
            else:
                print("Keyword not found")
            OK = input("If this is OK, press enter. Else, press m for more")
        # English sentence
        if find_all_dots == 3:
            iterator = 1
        else:
            iterator = number_sentences
        number = 1
        eng_sen_start = 0
        eng_sen_end = 0
        while iterator != 0 and re.search('[.!?]', search) != None:
            eng_sen_end = re.search('[.!?]', search).span()
            eng_sen_end_result = re.search('[.!?]', search)
            eng_sen_end = eng_sen_end[0] + 1
            eng_sen = search[eng_sen_start:eng_sen_end]
            print("English Sentence " + str(number) + ": " + eng_sen + "\n")
            number = number + 1
            search = search.replace(eng_sen, "")
            iterator = iterator - 1
        if eng_sen_end != 0:
            string = string[(string.find(
                "ENDPART", eng_sen_end)+1):len(string)]
        else:
            string = string[(string.find(
                "ENDPART", fre_sen_end)+1):len(string)]
        next = input(
            "Do you want to scroll to the next definition? Press m to scroll, t to type sentence or any key to continue")
    if next == "t":
        fre_sen = input("Write your sentence here: ")
        keyword = word[0:(len(word)-2)]
        if fre_sen.find(keyword) != -1:
            remove_word_start = fre_sen.find(keyword)
            # Intervention to make sure one can search for expressions, i.e. more than one word
            if fre_sen.find(word) != -1:
                fre_sen_remove = fre_sen.replace(word, "PLACEHOLDER")
            else:
                fre_sen_remove = fre_sen.replace(keyword, "PLACEHOLDER")
            remove_word_end = fre_sen_remove.find(" ", remove_word_start)
            if remove_word_end == -1:
                remove_word_end = fre_sen_remove.find(".", remove_word_start)
            remove_word = fre_sen_remove[remove_word_start:remove_word_end]
            sentence_keyword_removed = fre_sen_remove.replace(
                remove_word, "___")
    # Finner uttale-IPA
    url = "https://fr.wiktionary.org/wiki/" + word
    result = requests.get(url)
    content = result.content
    soup = BeautifulSoup(content, features="lxml")
    samples = soup.find(id="bodyContent")
    sample = samples.get_text()
    string = html2text.html2text(sample)
    pron_start = string.find("\\")
    pron_end = string.find("\\", pron_start+1)
    pron = string[pron_start:pron_end+1]
    # Renser opp:
    while pron.find("\n") != -1:
        pron = pron.replace("\n", "")
    print("Pronunciation: " + pron)

    # Finner kjønn:
    string = originalstring
    while string.find("\n") != -1:
        string = string.replace("\n", " ")
    gender_search_start = string.find("Principales traductionsFrançaisAnglais")
    gender_search_start = gender_search_start + \
        len("Principales traductionsFrançaisAnglais ")
    masculine = word + " nm"
    feminine = word + " nf"
    string = string[gender_search_start:len(string)]
    masculine_start = string.find(masculine)
    feminine_start = string.find(feminine)
    if masculine_start == 0:
        gender = "un"
    elif feminine_start == 0:
        gender = "une"
    else:
        gender = ""
    if gender != "":
        print("Gender: " + gender)

    # Adding images
    img_prompt = input(
        "Press enter to search using the same term, or type an alternative search string: ")
    if img_prompt == "":
        search = word
    else:
        search = img_prompt
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
        root = Path().cwd()/"images"
        duckduckgo_search(root, word, search, max_results=10)
        image_folder = Path().cwd()/"images"/word
        images_jpg = "images/" + word + "/*.jpg"
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
                "Press enter to scroll to next image, s to save, q to quit, or a to give a new search string ")
            if cont == "s":
                image_name = word + ".jpg"
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
    # Removes images that are not used
    root_folder = str(root)
    dir_name = root_folder + "/" + word
    remove_images = os.listdir(dir_name)
    for item in remove_images:
        if item.endswith(".jpg"):
            os.remove(os.path.join(dir_name, item))
    # Gjør bildet lesbart for anki:
    image_name = "<img src=" + '"' + image_name + '">'

    two_cards = input("Do you want to make two cards? Press y")
    if two_cards == "y":
        two_cards = "y"
    else:
        two_cards = ""
    # New prompt?
    prompt = input(
        "Do you want to make another card? Press q to quit, x to discard current card and start again, or q to quit: ")
    if prompt != "x":
        # Lager kort
        # ankicard = ';'.join([sentence_keyword_removed,image_name,definition,word,gender,fre_sen,pron,two_cards, '', '', '', ''])
        ankicard = sentence_keyword_removed + ";" + image_name + ";" + definition + ";" + word + \
            ";" + gender + ";" + fre_sen + ";" + pron + \
            ";" + two_cards + ";" + ";" + ";" + ";" + ";"
        ankicards = ankicards + ankicard + "\n"
        text_file = open("ankideck.txt", "w")
        n = text_file.write(ankicards)
        text_file.close()
