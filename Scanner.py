import typing

SIGMA = set()

DIGITS = set()
for i in range(10):
    DIGITS.add(chr(i + ord('0')))
LETTERS = set()
for i in range(26):
    LETTERS.add(chr(i + ord('a')))
for i in range(26):
    LETTERS.add(chr(i + ord('A')))

SIGMA = SIGMA.union(DIGITS)
SIGMA = SIGMA.union(LETTERS)

SYMBOL = set(';:,[](){}+-*=<')
WHITESPACE = set(' \n\r\t\v\f')

SIGMA = SIGMA.union(SYMBOL)
SIGMA = SIGMA.union(WHITESPACE)
SIGMA.add('/')

source_text = open(file='input.txt', mode="r")


class DFA:

    def __init__(self):
        self.terminal_nodes = set()
        self.token_type = dict()
        self.refeed_nodes = set()
        self.nodes_edges = dict()
        self.nodes_edges: typing.Dict[typing.Dict]
        self.non_sigma_edges = dict()
        self.reset_node = 0
        self.current_node = 0
        self.buffer = ""

    def add_node(self, *, node_id: int, is_terminal: bool, token_type: str, is_refeeder: bool):
        if is_terminal:
            self.terminal_nodes.add(node_id)
        self.token_type[node_id] = token_type
        if is_refeeder:
            self.refeed_nodes.add(node_id)
        self.nodes_edges[node_id] = dict()

    def add_edge(self, from_node: int, to_node: int, chars: typing.Set):
        edges_dict = self.nodes_edges[from_node]
        for char in chars:
            edges_dict[char] = to_node

    def add_non_sigma_edge(self, from_node: int, to_node: int):
        self.non_sigma_edges[from_node] = to_node

    def init_traversal(self, start_node: int):
        self.reset_node = start_node
        self.current_node = start_node

    def feed_character(self, char: str):
        if char == "EOF" and self.current_node == self.reset_node:
            return "nothing"
        if char not in self.nodes_edges[self.current_node]:
            next_node = self.non_sigma_edges[self.current_node]
        else:
            next_node = self.nodes_edges[self.current_node][char]
        self.current_node = next_node
        if self.current_node in self.terminal_nodes:
            if self.current_node not in self.refeed_nodes:
                self.buffer += char
                result = "terminal node", self.token_type[self.current_node], self.buffer
            else:
                result = "refeed node", self.token_type[self.current_node], self.buffer
            self.current_node = self.reset_node
            self.buffer = ""
            return result
        else:
            self.buffer += char
            return "nothing"


dfa = DFA()
#  node,  terminal, token, refeeder
nodes = [[1, False, None, False],
         [2, False, None, False],
         [3, True, "Invalid number", False],
         [4, True, "NUM", True],
         [5, False, None, False],
         [6, True, "ID", True],
         [7, True, "SYMBOL", False],
         [8, False, None, False],
         [9, True, "SYMBOL", False],
         [10, True, "SYMBOL", True],
         [11, False, None, False],
         [12, True, "SYMBOL", True],
         [13, True, "Unmatched comment", False],
         [14, False, None, False],
         [15, False, None, False],
         [16, True, "COMMENT", False],
         [17, False, None, False],
         [18, False, None, False],
         [19, True, "WHITESPACE", False],
         [20, True, "Invalid input", False],
         [21, True, "Unclosed comment", True]
         ]

for node in nodes:
    dfa.add_node(node_id=node[0], is_terminal=node[1], token_type=node[2], is_refeeder=node[3])

edges = [[1, 2, DIGITS],
         [2, 2, DIGITS],
         [2, 3, LETTERS],
         [2, 4, set.union(SIGMA - LETTERS, {'EOF'})],
         [1, 5, LETTERS],
         [5, 5, set.union(LETTERS, DIGITS)],
         [5, 6, SIGMA - set.union(LETTERS, DIGITS, {'EOF'})],
         [1, 7, SYMBOL - {'='}],
         [1, 8, {'='}],
         [8, 9, {'='}],
         [8, 10, set.union(SIGMA - set('='), {'EOF'})],
         [1, 11, {'*'}],
         [11, 12, set.union(SIGMA - {'/'}, {'EOF'})],
         [11, 13, {'/'}],
         [1, 14, {'/'}],
         [14, 15, {'/'}],
         [14, 17, {'*'}],
         [15, 15, SIGMA - {'\n'}],
         [15, 16, {'\n', 'EOF'}],
         [17, 17, SIGMA - {'*'}],
         [17, 18, {'*'}],
         [18, 18, {'*'}],
         [18, 17, SIGMA - {'*'}],
         [18, 16, {'/'}],
         [1, 19, WHITESPACE],
         [17, 21, {'EOF'}],
         [18, 21, {'EOF'}]
         ]

for edge in edges:
    dfa.add_edge(from_node=edge[0], to_node=edge[1], chars=edge[2])

non_sigma_edges = [[2, 3],
                   [5, 6],
                   [8, 10],
                   [11, 12],
                   [15, 15],
                   [17, 17],
                   [18, 17],
                   [1, 20]]

for non_sigma_edge in non_sigma_edges:
    dfa.add_non_sigma_edge(non_sigma_edge[0], non_sigma_edge[1])


def get_next_character():
    char = source_text.read(1)
    if not char:
        return -1
    return char


KEYWORDS = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return']

def check_if_keyword(token_type, token_content, token_line):
    if token_type == 'ID' and token_content in KEYWORDS:
        token_type = 'KEYWORD'
    return token_type, token_content, token_line


current_line = 1
refeed = False
last_character = ''

import time

def get_next_token():
    global current_line, refeed, last_character
    dfa.init_traversal(1)
    token_line = current_line
    while True:
        char = last_character
        if not refeed:
            char = get_next_character()
        if char == -1:
            char = "EOF"
        # print("feeding char", "\'%s\'" % char, " to dfa")
        result = dfa.feed_character(char)
        last_character = char
        # print(result)

        if result[0] == 'refeed node':
            refeed = True
        else:
            refeed = False

        if result[0] in ['refeed node', 'terminal node']:
            token = check_if_keyword(result[1], result[2], token_line)
            return token

        if char == '\n' and not refeed:
            current_line += 1
        if char == "EOF" and not refeed:
            return 'EOF'
        time.sleep(0.001)

