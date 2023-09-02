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

