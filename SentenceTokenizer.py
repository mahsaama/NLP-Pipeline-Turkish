from enum import Enum
import warnings
import regex

PATH = "DATA"

# Based on the scripts developed by Philipp Koehn and Josh Schroeder: https://pypi.org/project/sentence-splitter/
# Simplified for custom needs and Turkish language
class SentenceTokenizer:
    class PrefixType(Enum):
        DEFAULT = 1
        NUMERIC_ONLY = 2

    def __init__(self):  # ISO 639-1 language code
        self.non_breaking_prefixes = dict()
        with open(
            PATH + "/" + "non_breaking_prefixes_tr.txt", mode="r", encoding="utf-8"
        ) as prefix_file:
            for line in prefix_file.readlines():

                if "#NUMERIC_ONLY#" in line:
                    prefix_type = SentenceTokenizer.PrefixType.NUMERIC_ONLY
                else:
                    prefix_type = SentenceTokenizer.PrefixType.DEFAULT

                # non_brekaing_prefixes_tr file contains comments for ease of read
                # so this part removes them
                line = regex.sub(
                    pattern=r"#.*",
                    repl="",
                    string=line,
                    flags=regex.DOTALL | regex.UNICODE,
                )
                line = line.strip()

                if not line:
                    continue

                self.non_breaking_prefixes[line] = prefix_type

    # lower level function used by the class to split given string into list of strings, thus sentences
    def split(self, text):

        if text is None:
            warnings.warn("Text is None.", SentenceTokenizer)
            return []

        if not text:
            return []

        # Sentence Breaker Rules:

        # Sentence markes such as "?", "!" that are not period, followed by sentence starter
        text = regex.sub(
            pattern=r'([?!]) +([\'"([\u00bf\u00A1\p{Initial_Punctuation}]*[\p{Uppercase_Letter}\p{Other_Letter}])',
            repl="\\1\n\\2",
            string=text,
            flags=regex.UNICODE,
        )

        # Multiple dots ("...") followed by sentence starter
        text = regex.sub(
            pattern=r'(\.[\.]+) +([\'"([\u00bf\u00A1\p{Initial_Punctuation}]*[\p{Uppercase_Letter}\p{Other_Letter}])',
            repl="\\1\n\\2",
            string=text,
            flags=regex.UNICODE,
        )

        # Sentence ending with punctuation, within quotation marks or parenthesis, followed by sentence starter punctuation and upper case
        text = regex.sub(
            pattern=(
                r'([?!\.][\ ]*[\'")\]\p{Final_Punctuation}]+) +([\'"([\u00bf\u00A1\p{Initial_Punctuation}]*[\ ]*'
                r"[\p{Uppercase_Letter}\p{Other_Letter}])"
            ),
            repl="\\1\n\\2",
            string=text,
            flags=regex.UNICODE,
        )

        # Sentence ending with punctuation and followed by sentence starter punctuation and capital letter
        text = regex.sub(
            pattern=(
                r'([?!\.]) +([\'"[\u00bf\u00A1\p{Initial_Punctuation}]+[\ ]*[\p{Uppercase_Letter}\p{Other_Letter}])'
            ),
            repl="\\1\n\\2",
            string=text,
            flags=regex.UNICODE,
        )

        # Special punctuation cases
        words = regex.split(pattern=r" +", string=text, flags=regex.UNICODE)
        text = ""
        for i in range(0, len(words) - 1):

            match = regex.search(
                pattern=r"([\w\.\-]*)([\'\"\)\]\%\p{Final_Punctuation}]*)(\.+)$",
                string=words[i],
                flags=regex.UNICODE,
            )
            if match:

                prefix = match.group(1)
                starting_punct = match.group(2)

                def is_honorific_prefix(prefix_, starting_punct_):
                    """Check if \\1 is a known honorific and \\2 is empty."""
                    if prefix_:
                        if prefix_ in self.non_breaking_prefixes:
                            if (
                                self.non_breaking_prefixes[prefix_]
                                == SentenceTokenizer.PrefixType.DEFAULT
                            ):
                                if not starting_punct_:
                                    return True
                    return False

                if is_honorific_prefix(prefix_=prefix, starting_punct_=starting_punct):
                    # Not breaking
                    pass

                elif regex.search(
                    pattern=r"(\.)[\p{Uppercase_Letter}\p{Other_Letter}\-]+(\.+)$",
                    string=words[i],
                    flags=regex.UNICODE,
                ):
                    # Not breaking - upper case acronym
                    pass

                elif regex.search(
                    pattern=(
                        r'^([ ]*[\'"([\u00bf\u00A1\p{Initial_Punctuation}]*[ ]*[\p{Uppercase_Letter}'
                        r"\p{Other_Letter}0-9])"
                    ),
                    string=words[i + 1],
                    flags=regex.UNICODE,
                ):

                    def is_numeric(prefix_, starting_punct_, next_word):
                        """The next word has a bunch of initial quotes, maybe a space, then either upper case or a
                        number."""
                        if prefix_:
                            if prefix_ in self.non_breaking_prefixes:
                                if (
                                    self.non_breaking_prefixes[prefix_]
                                    == SentenceTokenizer.PrefixType.NUMERIC_ONLY
                                ):
                                    if not starting_punct_:
                                        if regex.search(
                                            pattern="^[0-9]+",
                                            string=next_word,
                                            flags=regex.UNICODE,
                                        ):
                                            return True
                        return False

                    if not is_numeric(
                        prefix_=prefix,
                        starting_punct_=starting_punct,
                        next_word=words[i + 1],
                    ):
                        words[i] = words[i] + "\n"

                    # A return is always added unless there is a numeric non-breaker and a number start

            text = text + words[i] + " "

        # Stopped one token away from the end, so that easy look-ahead is possible. Then appended.
        text = text + words[-1]

        # White spaces at the head and tail are removed.
        # Double white spaces are also removed.
        text = regex.sub(pattern=" +", repl=" ", string=text)
        text = regex.sub(pattern="\n ", repl="\n", string=text)
        text = regex.sub(pattern=" \n", repl="\n", string=text)
        text = text.strip()

        sentences = text.split("\n")

        return sentences

    # higher level function that is called by the user to split
    def split_text_into_sentences(self, text):
        splitter = SentenceTokenizer()
        return splitter.split(text=text)
