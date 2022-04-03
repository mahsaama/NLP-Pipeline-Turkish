import utils


# NOT ONEMLİ: Stopword listesi https://github.com/ahmetax/trstop adresinden alındı.
# Kaynak belirtmek gerekir. Onun dışında o adresten kod kullanılmadı.


class StopwordRemover:
    def __init__(self):
        self.stop_words_list = utils.load_words("./DATA/turkce-stop-words.txt")

    def remove_stopwords(self, word_tokens):
        filtered_sentence = []

        for w in word_tokens:
            if w not in self.stop_words_list:
                filtered_sentence.append(w)

        return filtered_sentence
