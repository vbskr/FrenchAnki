# %%
import requests
import bs4
import lxml
import pdb
import os
import matplotlib.pyplot as plt
import send2trash
from PIL import Image
import random
import psutil
from playsound import playsound

# %%
from pyforvo import Forvo

# %%
class Instance:
    def __init__(
        self,
        fre_word,
        fre_def="",
        eng_word="",
        fre_sen="",
        fre_sen_keyword_removed="",
        eng_sen="",
        gender="",
        ipa="",
        pron="",
        image="",
        two_cards="",
    ):
        self.fre_word = fre_word
        self.fre_def = fre_def
        self.eng_word = eng_word
        self.fre_sen = fre_sen
        self.fre_sen_keyword_removed = fre_sen_keyword_removed
        self.eng_sen = eng_sen
        self.gender = gender
        self.ipa = ipa
        self.pron = pron
        self.image = image
        self.two_cards = two_cards

    def add_fre_def(self, new_fre_def):
        self.fre_def = new_fre_def

    def add_eng_word(self, new_eng_word):
        if self.eng_word == "":
            self.eng_word = new_eng_word
        else:
            self.eng_word = self.eng_word + ", " + new_eng_word

    def add_fre_sen(self, new_fre_sen):
        self.fre_sen = new_fre_sen

    def add_fre_sen_keyword_removed(self, fre_sen_keyword_removed):
        self.fre_sen_keyword_removed = fre_sen_keyword_removed

    def add_eng_sen(self, new_eng_sen):
        self.eng_sen = new_eng_sen

    def add_gender(self, new_gender):
        self.gender = new_gender
        if self.gender == "nm":
            self.gender = "un"
        elif self.gender == "nf":
            self.gender = "une"
        else:
            self.gender = ""

    def add_ipa(self, new_ipa):
        self.ipa = new_ipa

    def add_image(self, new_image):
        self.image = new_image

    def add_pron(self, new_pron):
        self.pron = new_pron

    def check_two_cards(self):
        check = input(
            "Do you want to make two cards? Press any key to accept, or n if not: "
        )
        if check != "n":
            self.two_cards = "y"
        else:
            pass

    # def show_eng_word(self):
    #    return ", ".join(self.eng_word)

    def show_instance(self):
        print(f"French Word: {self.fre_word}")
        print(f"Gender: {self.gender}")
        print(f"French Definition: {self.fre_def}")
        print(f"English word: {self.eng_word}")
        print(f"French Sentence: {self.fre_sen}")
        print(f"English Sentence: {self.eng_sen}")

    def make_anki_card(self):
        things_list = []
        things_list.append(self.fre_sen_keyword_removed)
        things_list.append(self.image)
        things_list.append(self.fre_def)
        things_list.append(self.fre_word)
        things_list.append(self.gender)
        things_list.append(self.fre_sen)
        things_list.append(self.pron)
        things_list.append(self.ipa)
        things_list.append(self.two_cards)
        things_list.append("")
        things_list.append("")
        things_list.append("")
        things_list.append(self.eng_word)
        things_list.append(" ")
        things_list.append(" ")
        anki_card = "|".join(things_list)
        return anki_card

    def __str__(self):
        return f"French Word: {self.fre_word}\nFrench Definition: {self.fre_def}\nEnglish word: {self.eng_word}\nFrench Sentence: {self.fre_sen}, English Sentence: {self.eng_sen}"

# %%
def extract_even_odd(soup):
    even = soup.select(".even")
    odd = soup.select(".odd")
    soup_string = str(soup)
    soup_dictionary = {}
    for o in odd:
        string_o = str(o)
        position = soup_string.find(string_o)
        soup_dictionary[o] = position
    for e in even:
        string_e = str(e)
        position = soup_string.find(string_e)
        soup_dictionary[e] = position
    sorted_list_tuples = sorted(soup_dictionary.items(), key=lambda x: x[1])
    sorted_list = []
    for i in sorted_list_tuples:
        sorted_list.append(i[0])
    return sorted_list

# %%
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

# %%
def check_new_line(line):
    try:
        line.select_one(".FrWrd").text
        return True
    except:
        return False

# %%
def find_fre_word(line):
    try:
        line.select_one(".FrWrd").select_one("strong")
        return line.select_one(".FrWrd").select_one("strong").text
    except:
        return False

# %%
def find_gender(line):
    try:
        result = line.select_one(".FrWrd").select_one(".POS2").text
        return result
    except:
        return False

# %%
def check_dsense(line):
    if line.select_one(".dsense") is not None:
        dsense = line.select_one(".dsense")
        return dsense
    else:
        return False

# %%
def check_extra_def_info(line):
    if line.select_one(".Fr2") is not None:
        extra_def_info = line.select_one(".Fr2")
        return extra_def_info
    else:
        return False

# %%
def find_fre_def(line):
    try:
        extra_def_info = ""
        for i in line.select("td"):
            if i.text.find("(") != -1:
                result = i.text
                if check_dsense(i) is not False:
                    result = result.replace(check_dsense(i).text, "")
                if check_extra_def_info(i) is not False:
                    extra_def_info = check_extra_def_info(i).text
                    result = result.replace(extra_def_info, "")
                break
        result = result.replace("(", "")
        result = result.replace(")", "")
        while result[-1] == " ":
            result = result[:-1]
        while result[0] == " ":
            result = result[1:]
        if extra_def_info != "":
            result = result + " (" + extra_def_info + ")"
        return result
    except:
        return False

# %%
def find_eng_word(line):
    try:
        result = line.select_one(".ToWrd").text
        gender = line.select_one(".ToWrd").select_one(".POS2").text
        result = rreplace(result, gender, "", 1)
        while result[-1] == " ":
            result = result[:-1]
        return result
    except:
        return False

# %%
def find_fre_sen(line):
    try:
        return line.select_one(".FrEx").text
    except:
        return False


# %%
def find_eng_sen(line):
    try:
        return line.select_one(".ToEx").text
    except:
        return False

# %%
def unpack_line(line, instance):
    # instance = Instance(fre_word)
    if find_gender(line) is not False:
        instance.add_gender(find_gender(line))
    if find_fre_def(line) is not False and instance.fre_def == "":
        instance.add_fre_def(find_fre_def(line))
    if find_eng_word(line) is not False:
        instance.add_eng_word(find_eng_word(line))
    if find_fre_sen(line) is not False:
        instance.add_fre_sen(find_fre_sen(line))
    if find_eng_sen(line) is not False:
        instance.add_eng_sen(find_eng_sen(line))
    return instance

# %%
def make_instance(fre_word):
    return Instance(fre_word)

# %%
def unpack_lines(lines):
    instance = ""
    instances = []
    for line in lines:
        if check_new_line(line) is True:
            if instance != "":
                instances.append(instance)
            fre_word = find_fre_word(line)
            instance = make_instance(fre_word)
        instance = unpack_line(line, instance)
        #mulig du må gjøre ett elller annet for siste linjen...
    return instances

# %%
def return_fre_sen_keyword_removed(fre_sen, fre_word):
    if fre_sen.find(fre_word[0:-2]) != -1:
        start = fre_sen.find(fre_word[0:-2])
        end = fre_sen.find(" ", start)
        keyword = fre_sen[start:end]
        fre_sen_keyword_removed = fre_sen.replace(keyword,"___")
        print(f"French sentence with keyword removed: {fre_sen_keyword_removed}\n")
        ok_q = input("If this looks ok, press enter. If not, press s to type manually")
        if ok_q == "s":
            fre_sen_keyword_removed = input("Keyword not found. Please type sentence with keyword removed manually")
        else:
            pass
    else:
        fre_sen_keyword_removed = input("Keyword not found. Please type sentence with keyword removed manually")
    return fre_sen_keyword_removed
    

# %%
def collage_method(images_list):
    collage = Image.new("RGBA", (2000,1500))
    counter = 0
    for i in range(0,2000,500):
        for j in range(0,1500,500):
            try:
                file = images_list[counter]
            except:
                file = images_list[0]
            photo = Image.open(file).convert("RGBA")
            photo = photo.resize((500,500))        
            collage.paste(photo, (i,j))
            counter += 1
    collage.show()

# %%
def search_and_download_images(query, num_images, directory):
    url = 'https://searx.thegpm.org/'

    params = {
        'q': query,
        'categories': 'images',
        'format': 'json',
        'pageno': 1,
        'count': num_images,
        'language': 'fr'
    }

    response = requests.get(url, params=params)
    data = response.json()

    image_urls = [result['img_src'] for result in data['results']]
    image_paths = []

    for index, image_url in enumerate(image_urls[:num_images]):
        response = requests.get(image_url)
        image_path = os.path.join(directory, f'image{index}.jpg')  # Use os.path.join to create the file path
        with open(image_path, 'wb') as f:
            f.write(response.content)
        image_paths.append(image_path)

    return image_paths
# %%
def image_search(search):
    while True:
        question = input(f"Do you want to make an image search for: {search}? Press any key to continue, s to give a new search term, or n to cancel")
        if question == "s":
            search = input("Provide search term")
        if question == "n":
            return ""
        directory = os.path.join(os.getcwd(), "images_temp")
        try:
            send2trash.send2trash(directory)
        except:
            pass
        os.mkdir(directory)
        images_list = search_and_download_images(search, 12, directory)
        images_list = sorted(images_list)
        collage_method(images_list)
        while True:
            choice = input("Press a digit from 1-12 corresponding to the picture you want, s to search for a new term, or any other key to cancel: ")
            try:
                choice = int(choice)
                if choice not in range(1,13):
                    print("Try again")
                else:
                    break                    
            except:
                break
        if choice == int(choice):
            save_image = Image.open(images_list[choice-1])
            save_directory = os.path.join(os.getcwd(), "images_saved")
            if os.path.isdir(save_directory) == True:
                pass
            else:
                os.mkdir(save_directory)
            basewidth = 130
            #img = Image.open(image_name)
            wpercent = (basewidth/float(save_image.size[0]))
            hsize = int((float(save_image.size[1])*float(wpercent)))
            save_image = save_image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
            if search.find(" ") != -1:
                while search.find(" ") != -1:
                    search = search.replace(" ", "_")
            image_name = search + str(random.randint(100,999)) + ".jpg"
            save_name = os.path.join(save_directory, image_name)
            save_image.save(save_name)
            for proc in psutil.process_iter():
                if proc.name() == "eog":
                    proc.kill()
            send2trash.send2trash(directory)
            image_name = '<img src="' + image_name + '">'
            return image_name
        elif choice == "s":
            for proc in psutil.process_iter():
                if proc.name() == "eog":
                    proc.kill()
            send2trash.send2trash(directory)
            continue
        else:
            for proc in psutil.process_iter():
                if proc.name() == "eog":
                    proc.kill()
            send2trash.send2trash(directory)
            return ""

# %%
def find_ipa(soup):
    if soup.select_one(".pronWR") is not None:
        ipa = soup.select_one(".pronWR").text
        ipa = ipa.replace("[","/")
        ipa = ipa.replace("]","/")
        return ipa
    else:
        return False

# %%
def api_check():
    try:
        filePath = "api.txt"
        textFile = open(filePath)
        api_key = textFile.read()
        textFile.close()
        api_key = api_key.replace("\n", "")
        return api_key
    except:
        print("Api-code not found. Place api.txt in the same folder as script.")
        return False

# %%
def get_forvo(search_term, api_key):
    while True:
        inp = input(f"Do you want to search for a pronunciation for {search_term}? Press enter, or type in alternative search term, or press c to cancel: ")
        if inp == "c":
            return ""
        try:
            if inp == "":
                pass
            else:
                search_term = inp
            forvo = Forvo(api_key)
            audio = forvo.get_pronunciation(search_term, language='fr')
            audio_folder = os.path.join(os.getcwd(), "audio")
            if os.path.isdir(audio_folder) == True:
                pass
            else:
                os.mkdir(audio_folder)
            file_name = search_term + str(random.randint(100,999)) + ".mp3" #This is the name of the file, without folder
            audio_name = "[sound:" + file_name + "]" # This is the text that needs to appear on the anki card
            file_name_path = os.path.join(audio_folder, file_name) # This is the entire path of the file
            audio.download(path=file_name_path, fmt="mp3") # Downloading this file
            playsound(file_name_path)
            inp = input("Press enter to choose this sound file, or any key to try again: ")
            if inp == "":
                return audio_name
            else:
                pass
        except:
            print("\nNot found!")
            return ""

# %%
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



