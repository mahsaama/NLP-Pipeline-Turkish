import re
import utils


class Tokenizer:
    def __init__(self):
        self.mwe_lexicon = utils.load_words("./DATA/MWE_lexicon.txt")
        self.abbrevations = utils.load_words("./DATA/abbrevations.txt")
        self.rules = [
            "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$",  # email
            "(?<=[^0-9])(\:)(?=[^0-9.]|[\s]|$)",  # time
            "(\#)(?=[^a-z0-9]|[\s]|$)",  # hashtag
            "(?:(https?://)?(http?://)(www\.)?[a-z0-9]+\.[a-z][.a-z0-9\?=\-\+%&\_/])",  # handling web addresses
            "\?+",
            "\!+",
            "\,",
            "\;",
            "\*",
            "\^",
            r"\(|\)|\[|\]|\{|\}",
        ]
        self.split = r"\s|\t|\n|\r"

    def tokenize(self, input_sentence, split_token="<*>"):
        sentence = input_sentence

        # Check regular expressions for matches and add split:
        for rule in self.rules:
            sentence = re.sub(
                rule, " \g<0> ", sentence
            )  # The backreference \g<0> substitutes in the entire substring matched by the RE.

        # Split from all splitted characters
        working_sentence = re.sub(self.split, split_token, sentence)
        list_of_token_strings = [
            x.strip() for x in working_sentence.split(split_token) if x.strip() != ""
        ]

        original_list_of_token_strings = list(list_of_token_strings)

        # Normalization:
        index = 0
        inserted_dots = 0
        for token in original_list_of_token_strings:
            index += 1
            if token[-1] == ".":
                abbrevation = False
                # Check if abbrevation:
                if token in self.abbrevations:
                    abbrevation = True
                if not abbrevation:
                    new_token = token[:-1]
                    list_of_token_strings.insert(index + inserted_dots, ".")
                    list_of_token_strings[index + inserted_dots - 1] = new_token
                    inserted_dots += 1

        # Multi Word Expressions
        # Known bug:
        # If MWE appears at the end of the sentence,
        # Bug appears.

        original_length = len(original_list_of_token_strings)
        original_list_of_token_strings = list(list_of_token_strings)
        index = 0

        while index < original_length:

            token = original_list_of_token_strings[index]
            for expression in self.mwe_lexicon:
                expression_length = expression.count(" ") + 1
                check_index = index
                is_multiword = False  # todo true
                for i in range(expression_length):
                    if index + i >= original_length:
                        continue
                    else:
                        if original_list_of_token_strings[index + i] not in expression:
                            is_multiword = False

                if is_multiword:
                    # Pass if already multiword:
                    if token.count(" ") == 0:
                        list_of_token_strings.insert(index, expression)
                        for deleter in range(expression_length):
                            if index + 1 < original_length:
                                list_of_token_strings.pop(index + 1)
                        index += expression_length

            index += 1

        return list_of_token_strings
