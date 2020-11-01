import typing
from anytree import AnyNode, RenderTree

# root = AnyNode(name='Program')
# c1 = AnyNode(parent=root, name)

terminals = []
non_terminals = []
grammars = set()
first_sets = dict()
follow_sets = dict()


class Grammar:
    def __init__(self, origin: str, destination: list, predict: set):
        self.origin = origin
        self.destination = destination
        self.predict = predict


class ParseTable:
    def __init__(self):
        self.table = dict()
        self.table: typing.Dict[typing.Dict]

    def init_table(self):
        for nt in non_terminals:
            self.table[nt] = dict()
            for t in terminals:
                self.table[nt][t] = None

    def fill_table(self, grammars: typing.Set[Grammar]):
        # put each grammar into LL(1) parse table
        for grammar in grammars:
            for terminal in grammar.predict:
                self.table[grammar.origin][terminal] = grammar.destination
        # finding synch cells
        for nt in non_terminals:
            if 'ε' not in first_sets[nt]:
                for terminal in follow_sets[nt]:
                    if self.table[nt][terminal] == None:
                        self.table[nt][terminal] = 'synch'


def render_parse_tree(root):
    parse_tree_file = open(file='parse_tree.txt', mode="w")
    parse_tree_file.write(RenderTree(root).by_attr("name"))


firsts_file = open(file='Firsts.txt', mode='r')
follows_file = open(file='Follows.txt', mode='r')
predicts_file = open(file='Predicts.txt', mode='r')
grammar_file = open(file='phase 2/grammar.txt', mode='r')

# lines = firsts_file.readlines()
# for line in lines:
#     items = line.split()
#     nt = items[0]
#     non_terminals.add(nt)
#     first_sets[nt] = set(items[1:])
#
# lines = follows_file.readlines()
# for line in lines:
#     items = line.split()
#     nt = items[0]
#     follow_sets[nt] = set(items[1:])
#
# predict_lines = predicts_file.readlines()
# for i in range(len(grammar_lines)):
#     items = grammar_lines[i].split()
#     predict = set(predict_lines[i].split())
#     grammar = Grammar(items[0], items[2:], predict)
#     grammars.add(grammar)


grammar_lines = grammar_file.readlines()
for line in grammar_lines:
    symbols = line.split(' ')
    beginning_non_terminal = symbols[0]
    if beginning_non_terminal not in non_terminals:
        non_terminals.append(beginning_non_terminal)


for line in grammar_lines:
    line: str
    symbols = line.split()
    for symbol in symbols[2:]:
        if symbol not in non_terminals and symbol != 'Îµ':
            if symbol == '$':
                symbol = 'EOF'
            if symbol not in terminals:
                terminals.append(symbol)

print(terminals)
print(non_terminals)

# for grammar in grammars:
#     for x in grammar.destination:
#         if x not in non_terminals:
#             terminals.add(x)
#
# parse_table = ParseTable()
# parse_table.init_table()
# parse_table.fill_table(grammars)
#
