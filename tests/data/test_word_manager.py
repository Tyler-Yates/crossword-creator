from application import WordManager


class TestWordManager(WordManager):
    def __init__(self, valid_words=None):
        self.valid_words = valid_words

        super(TestWordManager, self).__init__(set())

    def is_word(self, word: str) -> bool:
        if self.valid_words:
            return word in self.valid_words
        else:
            return True
