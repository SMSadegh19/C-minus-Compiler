import string
import typing

DIGITS = set(string.digits)
LETTERS = set(string.ascii_letters)
SYMBOL = set(';:,[](){}+-*=<')
WHITESPACE = set(' \n\r\t\v\f')
SIGMA = set.union(DIGITS).union(LETTERS).union(SYMBOL).union(WHITESPACE).union({'/'})


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
            return "nothing", self.token_type[self.current_node], self.buffer
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
            return "nothing", self.token_type[self.current_node], self.buffer


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
         [21, True, "Unclosed comment", True],
         [22, True, "Invalid input", False],
         [23, True, "Invalid input", True]
         ]

for node in nodes:
    dfa.add_node(node_id=node[0], is_terminal=node[1], token_type=node[2], is_refeeder=node[3])

edges = [[1, 2, DIGITS],
         [2, 2, DIGITS],
         [2, 3, LETTERS],
         [2, 4, set.union(SIGMA - LETTERS - DIGITS, {'EOF'})],
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
         [14, 23, SIGMA - {'/', '*', 'EOF'}],
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
                   [5, 22],
                   [8, 10],
                   [11, 12],
                   [15, 15],
                   [17, 17],
                   [18, 17],
                   [1, 20],
                   [14, 23]
                   ]

for non_sigma_edge in non_sigma_edges:
    dfa.add_non_sigma_edge(non_sigma_edge[0], non_sigma_edge[1])
