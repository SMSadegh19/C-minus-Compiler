class SymbolTable:

    def __init__(self):
        self.symbols = []
        self.temp_register_index = 1000
        self.temps = []
        self.byte_length = 4
        self.symbol_register_index = 500

    def get_symbol(self, input_symbol: str):
        for symbol in self.symbols:
            if symbol[0] == input_symbol:
                return symbol
        self.symbols.append((input_symbol, self.symbol_register_index, 'Undefined'))
        self.symbol_register_index += self.byte_length
        return self.symbols[-1]

    def get_temp(self):
        result = self.temp_register_index
        self.temp_register_index += self.byte_length
        return result


