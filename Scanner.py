from ScannerDFA import DFA


KEYWORDS = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return']


class Scanner:

    def _get_next_character(self):
        char = self.source.read(1)
        if not char:
            return -1
        return char

    def __init__(self, *, dfa: DFA, source):
        self.dfa = dfa
        self.source = source
        self._current_line = 1
        self._refeed = False
        self._last_character = ''

    def _get_next_token(self):
        self.dfa.init_traversal(1)
        token_line = self._current_line
        while True:
            char = self._get_next_character() if not self._refeed else self._last_character
            if char == -1:
                char = 'EOF'
            token_status, token_type, token_content = self.dfa.feed_character(char)
            self._last_character = char
            self._refeed = True if token_status == 'refeed node' else False
            if char == '\n' and not self._refeed:
                self._current_line += 1
            if token_status in ['refeed node', 'terminal node']:
                if token_type == 'ID' and token_content in KEYWORDS:
                    token_type = 'KEYWORD'
                return token_type, token_content, token_line

            if char == "EOF" and not self._refeed:
                return 'EOF', '$', token_line

    def get_next_token(self):
        while True:
            token = self._get_next_token()
            if token[0] in ['COMMENT', 'WHITESPACE']:
                continue
            elif token[0] in ['SYMBOL', 'KEYWORD']:
                token_presentation = "(%s, %s)" % (token[0], token[1])
                token_type = token[1]
            elif token[0] in ['ID', 'NUM']:
                token_presentation = "(%s, %s)" % (token[0], token[1])
                token_type = token[0]
            elif token[0] in ['EOF']:
                token_presentation = "%s" % token[1]
                token_type = token[1]
            else:
                continue
                # x = "(%s, %s, %s)" % (token[0], token[1], token[2])
                # raise Exception("strange token %s was found!" % x)
            token_line = token[2]
            # print(token_type, token_presentation, token_line)
            return token_type, token_presentation, token_line
