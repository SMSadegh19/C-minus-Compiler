import typing


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

    def extend(self, number_of_index_to_extend):
        self.symbol_register_index += self.byte_length * number_of_index_to_extend


class Symbol:
    def __init__(self, *, lexeme: str, var_type: str, addressing_type: str, address: int, scope: int,
                 symbol_type: str, arguments_count=0):
        self.lexeme = lexeme
        self.type = symbol_type
        self.addressing_type = addressing_type
        self.address = address
        self.scope = scope
        self.var_type = var_type
        self.arguments_count = arguments_count

    def __str__(self):
        return 'lexeme: %s, type: %s, addressing_type: %s, address: %s, scope: %s, var_type: %s' % \
               (self.lexeme, self.type, self.addressing_type, self.address, self.scope, self.var_type)


class NewSymbolTable:

    def __init__(self):
        self.symbols = typing.List[Symbol]
        self.symbols = []
        self.stack_pointer = 100
        self.byte_length = 4
        self.temp_register_index = 3000
        self.globals_index = 20000
        self.return_value_address_pointer = 10
        self.symbols.append(Symbol(
            lexeme='output', symbol_type='function', var_type='void', addressing_type='none', address=-1, scope=-1)
        )

    def get_symbol(self, input_symbol: str):
        for symbol in reversed(self.symbols):
            if symbol.lexeme == input_symbol:
                return symbol
        raise Exception("Symbol %s not defined" % input_symbol)

    def define_symbol(self, symbol: Symbol):
        self.symbols.append(symbol)

    def get_simple_temp(self):
        result = self.temp_register_index
        self.temp_register_index += self.byte_length
        return result

    def remove_scope(self, scope_number):
        symbols_copy = []
        for symbol in self.symbols:
            if symbol.scope != scope_number:
                symbols_copy.append(symbol)
        self.symbols = symbols_copy

    def get_new_global_address(self):
        address = self.globals_index
        self.globals_index += self.byte_length
        return address

    def allocate_array_memory(self, array_size: int):
        allocation_address = self.globals_index
        self.globals_index += self.byte_length * array_size
        return allocation_address
