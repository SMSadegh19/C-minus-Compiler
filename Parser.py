import typing

terminals = {}
non_terminals = {}
first_sets = dict()
follow_sets = dict()

class Grammer:
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
    
    def fill_table(self, grammers: typing.List[Grammer]):
        for grammer in grammers:
            for terminal in grammer.predict:
                self.table[grammer.origin][terminal] = grammer.destination
            if grammer.destination[0] == 'ε':
                for terminal in follow_sets[grammer.origin]:
                    self.table[grammer.origin][terminal] = 'ε'
        for nt in non_terminals:
            if 'ε' not in first_sets[nt]:
                for terminal in follow_sets[nt]:
                    self.table[nt][terminal] = 'synch'

