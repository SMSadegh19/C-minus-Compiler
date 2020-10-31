import typing

terminals = {}
non_terminals = {}
first_sets = dict()
follow_sets = dict()

class Grammar:
    def __init__(self, origin: str, destination: list, predict: list):
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
    
    def fill_table(self, grammars: typing.List[grammar]):
        # put each grammar
        for grammar in grammars:
            for terminal in grammar.predict:
                self.table[grammar.origin][terminal] = grammar.destination
            if grammar.destination[0] == 'ε':
                for terminal in follow_sets[grammar.origin]:
                    self.table[grammar.origin][terminal] = 'ε'
        # finding synch cells
        for nt in non_terminals:
            if 'ε' not in first_sets[nt]:
                for terminal in follow_sets[nt]:
                    self.table[nt][terminal] = 'synch'

