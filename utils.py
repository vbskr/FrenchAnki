import os
import requests
import bs4
from PIL import Image
import random
import psutil
import send2trash
from pyforvo import Forvo
from playsound import playsound
from instance import Instance

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
    try:
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
        response.raise_for_status()  # Check for HTTP request errors

        data = response.json()

        image_urls = [result['img_src'] for result in data['results']]
        image_paths = []

        for index, image_url in enumerate(image_urls[:num_images]):
            response = requests.get(image_url)
            response.raise_for_status()  # Check for HTTP request errors

            image_path = os.path.join(directory, f'image{index}.jpg')
            with open(image_path, 'wb') as f:
                f.write(response.content)
            image_paths.append(image_path)

        return image_paths

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during image search and download: {e}")
        return []

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
        except Exception as e:
            print(f"Error while sending directory to trash: {e}")

        try:
            os.mkdir(directory)
            images_list = search_and_download_images(search, 12, directory)
            images_list = sorted(images_list)
            collage_method(images_list)
            
            while True:
                choice = input("Press a digit from 1-12 corresponding to the picture you want, s to search for a new term, or any other key to cancel: ")
                try:
                    choice = int(choice)
                    if choice not in range(1, 13):
                        print("Try again")
                    else:
                        break                    
                except ValueError:
                    break

            if isinstance(choice, int):
                save_image = Image.open(images_list[choice-1])
                save_directory = os.path.join(os.getcwd(), "images_saved")

                if not os.path.exists(save_directory):
                    os.mkdir(save_directory)

                basewidth = 130
                wpercent = (basewidth / float(save_image.size[0]))
                hsize = int((float(save_image.size[1]) * float(wpercent)))
                save_image = save_image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                if " " in search:
                    search = search.replace(" ", "_")
                image_name = search + str(random.randint(100, 999)) + ".jpg"
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

        except Exception as e:
            print(f"An error occurred during image search and processing: {e}")
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
