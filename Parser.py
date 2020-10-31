import typing

terminals = set()
non_terminals = set()
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


firsts_file = open(file='Firsts.txt', mode='r')
follows_file = open(file='Follows.txt', mode='r')
predicts_file = open(file='Predicts.txt', mode='r')
grammars_file = open(file='Grammars.txt', mode='r')

lines = firsts_file.readlines()
for line in lines:
    items = line.split()
    nt = items[0]
    non_terminals.add(nt)
    first_sets[nt] = set(items[1:])

lines = follows_file.readlines()
for line in lines:
    items = line.split()
    nt = items[0]
    follow_sets[nt] = set(items[1:])

grammar_lines = grammars_file.readlines()
predict_lines = predicts_file.readlines()
for i in range(len(grammar_lines)):
    items = grammar_lines[i].split()
    predict = set(predict_lines[i].split())
    grammar = Grammar(items[0], items[2:], predict)
    grammars.add(grammar)


for grammar in grammars:
    for x in grammar.destination:
        if x not in non_terminals:
            terminals.add(x)


