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
        

