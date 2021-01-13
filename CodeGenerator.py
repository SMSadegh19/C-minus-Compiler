import typing
import re
from SymbolTable import *
from ScopeHandler import ScopeEntry

symbol_table = SymbolTable()

semantic_stack = []
while_switch_scope_stack = []
while_switch_scope_stack: typing.List[ScopeEntry]

program_block = {}
program_block_counter = 0


def write_to_program_block(*, code: str):
    global program_block_counter
    program_block[program_block_counter] = code
    program_block_counter += 1


def edit_program_line(line: int, replacement: str):
    print("changing line ", line, " from ", program_block[line], end=" ")
    program_block[line] = program_block[line].replace('?', replacement)
    print("to", program_block[line])


class FunctionEntry:

    def __init__(self, *, frame_size: int, lexeme: str):
        self.frame_size = frame_size
        self.lexeme = lexeme


new_symbol_table = NewSymbolTable()
scope_stack = [0]
scope_counter = 1
function_memory = []
function_memory: typing.List[FunctionEntry]

function_signature = dict()
write_to_program_block(code="(ASSIGN, #%s, %s, )" % (500, new_symbol_table.stack_pointer))
write_to_program_block(code="(ASSIGN, #0, %s, )" % new_symbol_table.return_value_address_pointer)


# class SemanticEntry:
#
#     def __init__(self, *, address_type: str = None, address: int = None, code_line: int = None):
#         self.address_type = address_type
#         self.address = address
#         self.code_line = code_line
#
#     def get_address(self):
#         pre = ""
#         if self.address_type == 'indirect':
#             pre = '@'
#         return pre + str(self.address)
#

def get_by_relative_address(relative_address: int):
    temp = new_symbol_table.get_simple_temp()
    write_to_program_block(code="(ADD, %s, #%s, %s)" % (new_symbol_table.stack_pointer, relative_address, temp))
    return "@" + str(temp)


def get_pointer_by_relative_address(relative_address: int):
    pointer_address = get_by_relative_address(relative_address)
    temp = new_symbol_table.get_simple_temp()
    write_to_program_block(code="(ASSIGN, %s, %s, )" % (pointer_address, temp))
    return "@" + str(temp)


def at_at_to_at(pointer: str):
    temp = new_symbol_table.get_simple_temp()
    write_to_program_block(code="(ASSIGN, %s, %s, )" % (pointer, temp))
    return '@' + str(temp)


def get_symbol_address(symbol, real_address: bool = True):
    if symbol.type == 'function':
        raise Exception('extracting address from function')
    if symbol.addressing_type == 'global':
        return symbol.address
    elif symbol.addressing_type == 'relative':
        return get_by_relative_address(symbol.address)
    elif symbol.addressing_type == 'relative pointer':
        return at_at_to_at(get_by_relative_address(symbol.address))
    else:
        raise Exception("hendelll")


def function_call(function_symbol: Symbol, args: list):
    print("calling function", function_symbol.lexeme, "with args:", args)
    if function_symbol.lexeme == 'output':
        write_to_program_block(code="(PRINT, %s, , )" % get_symbol_address(args[0]))
        semantic_stack.append('output function void')
        return

    new_stack_pointer_address = new_symbol_table.get_simple_temp()
    write_to_program_block(code="(ADD, %s, #%s, %s)" % (
        new_symbol_table.stack_pointer, function_memory[-1].frame_size, new_stack_pointer_address))
    write_to_program_block(
        code="(ASSIGN, %s, @%s, )" % (new_symbol_table.stack_pointer, new_stack_pointer_address))

    return_line_address = new_symbol_table.get_simple_temp()
    write_to_program_block(code="(ADD, %s, #%s, %s)" % (
        new_symbol_table.stack_pointer, function_memory[-1].frame_size + 4, return_line_address))
    # todo: check number of args match
    # todo: check args type match signature of function
    for i, arg in enumerate(args):
        arg_address_pointer = new_symbol_table.get_simple_temp()
        write_to_program_block(
            code="(ADD, %s, #%s, %s)" % (
                new_symbol_table.stack_pointer, function_memory[-1].frame_size + 8 + i * 4, arg_address_pointer))
        write_to_program_block(
            code="(ASSIGN, %s, @%s, )" % (get_symbol_address(arg), arg_address_pointer))

    write_to_program_block(
        code="(ASSIGN, %s, %s, )" % (new_stack_pointer_address, new_symbol_table.stack_pointer))
    write_to_program_block(code="(ASSIGN, #%s, @%s, )" % (program_block_counter + 2, return_line_address))
    write_to_program_block(code="(JP, %s, ,)" % function_symbol.address)
    relative_address = function_memory[-1].frame_size
    function_result_address = get_by_relative_address(relative_address)
    function_memory[-1].frame_size += 4
    write_to_program_block(
        code="(ASSIGN, %s, %s, )" % (new_symbol_table.return_value_address_pointer, function_result_address))
    semantic_stack.append(
        Symbol(lexeme="", var_type=function_symbol.var_type, addressing_type='relative', address=relative_address,
               scope=-1, symbol_type='variable')
    )


def exit_function_code():
    return_line_address_pointer = new_symbol_table.get_simple_temp()
    write_to_program_block(
        code=("(ADD, %s, #%s, %s)" % (new_symbol_table.stack_pointer, 4, return_line_address_pointer)))
    write_to_program_block(
        code="(ASSIGN, @%s, %s, )" % (new_symbol_table.stack_pointer, new_symbol_table.stack_pointer)
    )
    at_at_address = new_symbol_table.get_simple_temp()
    write_to_program_block(code="(ASSIGN, @%s, %s, )" % (return_line_address_pointer, at_at_address))
    write_to_program_block(
        code=("(JP, @%s, ,)" % at_at_address)
    )


def new_generate_code(*, action: str, label: str):
    print(action, label)
    global program_block_counter
    global scope_counter
    if action == '#push_type':
        def_type = re.match(r'\((\w+), (\w+)\)', label).group(2)
        semantic_stack.append(def_type)
    elif action == '#push_array_input_type':
        semantic_stack.append("array")
    elif action == '#push_normal_input_type':
        semantic_stack.append("nothing")
    elif action == '#add_param':
        lexeme = semantic_stack[-2]
        input_type = semantic_stack[-1]
        print("         %s %s" % (lexeme, input_type))
    elif action == '#define_function':
        # write_to_program_block(code='--------------------------')
        ss = []
        while semantic_stack[-1] != 'function_start':
            ss.append(semantic_stack.pop())
        semantic_stack.pop()
        ss.append(semantic_stack.pop())
        ss.append(semantic_stack.pop())
        ss = list(reversed(ss))
        function_type = ss[0]
        function_name = ss[1]
        if function_name != 'main':
            write_to_program_block(code="(JP, ?, , )")
            semantic_stack.append(program_block_counter - 1)
        new_symbol_table.define_symbol(
            Symbol(lexeme=function_name, var_type=function_type, addressing_type="code_line",
                   address=program_block_counter, symbol_type='function', scope=scope_stack[-1]))
        scope_counter += 1
        scope_stack.append(scope_counter)
        function_memory.append(FunctionEntry(frame_size=8,
                                             lexeme=function_name))  # todo : link address in memory, return line in code, and ...?
        print("function memory:", function_memory)
        args = ss[2:]
        function_signature[function_name] = args
        i = 0
        while i < len(args):
            input_type = args[i]
            input_lexeme = args[i + 1]
            is_array = args[i + 2]
            var_type = input_type + ('*' if is_array == 'array' else '')
            new_symbol_table.define_symbol(
                Symbol(lexeme=input_lexeme, var_type=var_type, addressing_type='relative',
                       address=function_memory[-1].frame_size,
                       scope=scope_stack[-1], symbol_type='variable')
            )
            function_memory[-1].frame_size += 4

            print("hmmm ", input_type, input_lexeme, is_array)
            i += 3
        print(args)
    elif action == '#END_SCOPE':
        new_symbol_table.remove_scope(scope_number=scope_stack.pop())
    elif action == '#return':
        exit_function_code()
    elif action == '#return_value':
        return_value = get_symbol_address(semantic_stack.pop())
        write_to_program_block(
            code="(ASSIGN, %s, %s, )" % (return_value, new_symbol_table.return_value_address_pointer))
        exit_function_code()
    elif action == '#end_function':
        function_entry = function_memory.pop()
        if function_entry.lexeme != 'main':
            exit_function_code()
            function_jump_over_line = semantic_stack.pop()
            edit_program_line(line=function_jump_over_line, replacement=str(program_block_counter))

    elif action == '#function_call':
        ss = []
        while semantic_stack[-1] != 'function_call':
            ss.append(semantic_stack.pop())
        semantic_stack.pop()
        function_symbol = semantic_stack.pop()
        ss = list(reversed(ss))
        function_call(function_symbol, ss)

    elif action == '#push':
        token = re.match(r'\((\w+), (\w+)\)', label).group(2)
        semantic_stack.append(token)
    elif action == '#start_function':
        function_type = semantic_stack[-2]
        function_name = semantic_stack[-1]
        semantic_stack.append("function_start")
    elif action == '#start_function_call':
        semantic_stack.append("function_call")
    elif action == '#variable_definition':
        var_type = semantic_stack[-2]
        var_name = semantic_stack[-1]
        semantic_stack.pop()
        semantic_stack.pop()
        # todo : check for existence of this same variable in the current scope (semantic error)
        if len(function_memory) <= 0:
            symbol = Symbol(lexeme=var_name, var_type='int', addressing_type='global',
                            address=new_symbol_table.get_new_global_address(), scope=scope_stack[-1],
                            symbol_type='variable')
        else:
            symbol = Symbol(lexeme=var_name, var_type='int', addressing_type="relative",
                            address=function_memory[-1].frame_size, scope=scope_stack[-1], symbol_type='variable')
            function_memory[-1].frame_size += 4

        new_symbol_table.define_symbol(symbol)
        print("herer", var_type, var_name)
    elif action == '#define_array':
        print(semantic_stack)
        var_type = semantic_stack[-3]
        var_name = semantic_stack[-2]
        length = int(semantic_stack[-1])
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.pop()
        if var_type == 'void':
            raise Exception('can\'t define array of void')
        if length <= 0:
            raise Exception('length of arrays must be at least one ')
        if len(function_memory) <= 0:
            array_pointer_address = new_symbol_table.get_new_global_address()
            allocation_address =new_symbol_table.allocate_array_memory(length)
            write_to_program_block(code="(ASSIGN, #%s, %s, )" % (allocation_address, array_pointer_address))
            symbol = Symbol(lexeme=var_name, var_type=(var_type + '*'), addressing_type='global',
                            address=array_pointer_address, scope=scope_stack[-1], symbol_type='variable')
        else:
            symbol = Symbol(lexeme=var_name, var_type=(var_type + "*"), addressing_type='relative',
                            address=function_memory[-1].frame_size, scope=scope_stack[-1], symbol_type='variable')
            print("defining array:", symbol.var_type, symbol.addressing_type)
            pointer_address = get_by_relative_address(function_memory[-1].frame_size)
            function_memory[-1].frame_size += 4
            array_beginning_address = get_by_relative_address(function_memory[-1].frame_size)
            write_to_program_block(code='(ASSIGN, %s, %s, )' % (array_beginning_address[1:], pointer_address))
            function_memory[-1].frame_size += 4 * length
        new_symbol_table.define_symbol(symbol)

    elif action == '#array_access':
        array_symbol = semantic_stack[-2]
        if array_symbol.var_type != 'int*':
            print(array_symbol.var_type, array_symbol.lexeme)
            raise Exception("accessing a non array variable as an array")
        offset_symbol = semantic_stack[-1]
        if offset_symbol.var_type != 'int':
            raise Exception("offset symbol is not of type int")

        array_pointer = get_symbol_address(array_symbol)
        offset = get_symbol_address(offset_symbol)
        semantic_stack.pop()
        semantic_stack.pop()
        relative_address = function_memory[-1].frame_size
        temp_address = get_by_relative_address(relative_address)
        semantic_stack.append(
            Symbol(lexeme="", var_type='int', addressing_type='relative pointer',
                   address=function_memory[-1].frame_size, scope=-1, symbol_type='variable')
        )
        function_memory[-1].frame_size += 4
        write_to_program_block(code="(ADD, %s, %s, %s)" % (array_pointer, offset, temp_address))

    elif action == '#push_number':
        num = re.match(r'\((\w+), (\d+)\)', label).group(2)
        temp_address = new_symbol_table.get_simple_temp()
        write_to_program_block(code="(ASSIGN, #%s, %d, )" % (num, temp_address))
        semantic_stack.append(
            Symbol(lexeme="", var_type='int', addressing_type='global', address=temp_address, scope=-1,
                   symbol_type='variable'))
    elif action == '#push_id':
        identifier = re.match(r'\((\w+), (\w+)\)', label).group(2)
        print(identifier)
        symbol = new_symbol_table.get_symbol(identifier)
        semantic_stack.append(symbol)
        print("appending symbol", symbol.lexeme, symbol.addressing_type, symbol.address)
        # semantic_stack.append(convert_symbol(symbol))
        # todo: check when symbol does not exist
    elif action == '#multiply':
        first_operand_address = get_symbol_address(semantic_stack[-1])
        second_operand_address = get_symbol_address(semantic_stack[-2])
        semantic_stack.pop()
        semantic_stack.pop()
        relative_address = function_memory[-1].frame_size
        temp_address = get_by_relative_address(relative_address)
        function_memory[-1].frame_size += 4
        write_to_program_block(
            code="(MULT, %s, %s, %s)" % (first_operand_address, second_operand_address, temp_address))
        semantic_stack.append(
            Symbol(lexeme="", var_type='int', addressing_type='relative', address=relative_address, scope=-1,
                   symbol_type='variable'))

    elif action == "#assign":
        print()
        for x in semantic_stack:
            print(x)
        print()
        destination = get_symbol_address(semantic_stack[-2])
        source = get_symbol_address(semantic_stack[-1])
        semantic_stack.pop()
        write_to_program_block(code="(ASSIGN, %s, %s, )" % (source, destination))
    elif action == '#pop':
        semantic_stack.pop()
    elif action == '#push_addition_operator':
        semantic_stack.append('ADD')
    elif action == '#push_subtraction_operator':
        semantic_stack.append('SUB')
    elif action == '#add_or_subtract':
        operator = semantic_stack[-2]
        first_operand_address = get_symbol_address(semantic_stack[-3])
        second_operand_address = get_symbol_address(semantic_stack[-1])
        relative_address = function_memory[-1].frame_size
        address = get_by_relative_address(relative_address)
        function_memory[-1].frame_size += 4
        write_to_program_block(
            code="(%s, %s, %s, %s)" % (operator, first_operand_address, second_operand_address, address))
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.append(
            Symbol(lexeme="", var_type='int', addressing_type='relative', address=relative_address, scope=-1,
                   symbol_type='variable'))

    elif action == '#if':
        comparison_result_address = get_symbol_address(semantic_stack[-1])
        semantic_stack.pop()
        write_to_program_block(code="(JPF, %s, ?, )" % comparison_result_address)
        semantic_stack.append(program_block_counter - 1)
    elif action == '#else':
        write_to_program_block(code='(JP, ?, , )')
        if_condition_line = semantic_stack[-1]
        semantic_stack.pop()
        semantic_stack.append(program_block_counter - 1)
        edit_program_line(line=if_condition_line, replacement=str(program_block_counter))
    elif action == '#endif':
        if_body_jump_line = semantic_stack[-1]
        semantic_stack.pop()
        edit_program_line(line=if_body_jump_line, replacement=str(program_block_counter))
    elif action == '#start_while':
        while_switch_scope_stack.append(ScopeEntry("while", len(semantic_stack)))
        # next 3 lines are for break statement
        # jump to start of while:
        write_to_program_block(code="(JP, %s, , )" % (program_block_counter + 2))
        # jump to after of while:
        semantic_stack.append(program_block_counter)
        write_to_program_block(code="(JP, ?, , )")
        # put start of while Expression computing in the stack
        semantic_stack.append(program_block_counter)
    elif action == '#while_condition':
        comparison_result_address = get_symbol_address(semantic_stack[-1])
        semantic_stack.pop()
        write_to_program_block(code="(JPF, %s, ?, )" % comparison_result_address)
        semantic_stack.append(program_block_counter - 1)
    elif action == '#endwhile':
        while_condition_line = semantic_stack[-1]
        while_expression_beginning_line = semantic_stack[-2]
        # break jumps here to get out of while:
        jump_out_line = semantic_stack[-3]
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.pop()
        write_to_program_block(code="(JP, %s, , )" % while_expression_beginning_line)
        edit_program_line(while_condition_line, str(program_block_counter))
        edit_program_line(jump_out_line, str(program_block_counter))
        while_switch_scope_stack.pop()
    elif action == '#break':
        last_scope = while_switch_scope_stack[-1]
        if last_scope.scope_type == "while":
            semantic_stack_scope_index = last_scope.semantic_stack_start_index
            jump_out_line = semantic_stack[semantic_stack_scope_index]
            write_to_program_block(code="(JP, %s, , )" % jump_out_line)
        elif last_scope.scope_type == "switch":
            # TODO for switch block
            print()
    #
    # elif action == '#save':
    #     semantic_stack.append(program_block_counter)
    #     write_to_program_block(code=None)
    # elif action == '#jump_false_save':
    #     number_of_saved_line = semantic_stack[-1]
    #     comparison_result_address = get_symbol_address(semantic_stack[-2])
    #     semantic_stack.pop()
    #     semantic_stack.pop()
    #     semantic_stack.append(program_block_counter)
    #     write_to_program_block(code=None)
    #     write_to_program_block(code="(JPF, %s, %s, )" % (comparison_result_address, program_block_counter),
    #                            line_number=number_of_saved_line)
    #     print("hendell at line", number_of_saved_line)
    #
    # elif action == '#jump':
    #     number_of_saved_line = semantic_stack[-1]
    #     write_to_program_block(code="(JP, %s, , )" % program_block_counter,
    #                            line_number=number_of_saved_line)
    # elif action == '#label':
    #     semantic_stack.append(program_block_counter)
    # elif action == '#while':
    #     before_while_condition_line_number = semantic_stack[-3]
    #     comparison_result_address = get_symbol_address(semantic_stack[-2])
    #     after_while_condition_line_number = semantic_stack[-1]
    #     write_to_program_block(code="(JP, %s, , )" % before_while_condition_line_number)
    #     write_to_program_block(code="(JPF, %s, %s, )" % (comparison_result_address, program_block_counter),
    #                            line_number=after_while_condition_line_number)
    #     semantic_stack.pop()
    #     semantic_stack.pop()
    #     semantic_stack.pop()
    elif action == '#push_less_than_comparator':
        semantic_stack.append('LT')
    elif action == '#push_is_equal_comparator':
        semantic_stack.append('EQ')
    elif action == '#relop':
        first_operand_address = get_symbol_address(semantic_stack[-3])
        operator = semantic_stack[-2]
        second_operand_address = get_symbol_address(semantic_stack[-1])
        relative_address = function_memory[-1].frame_size
        address = get_by_relative_address(relative_address)
        function_memory[-1].frame_size += 4
        write_to_program_block(
            code="(%s, %s, %s, %s)" % (operator, first_operand_address, second_operand_address, address))
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.append(
            Symbol(lexeme="", var_type='int', addressing_type='relative', address=relative_address, scope=-1,
                   symbol_type='variable'))
    elif action == '#negate':
        first_operand_address = get_symbol_address(semantic_stack[-1])
        relative_address = function_memory[-1].frame_size
        result_address = get_by_relative_address(relative_address)
        function_memory[-1].frame_size += 4
        write_to_program_block(
            code="(MULT, %s, #-1, %s)" % (first_operand_address, result_address))
        semantic_stack.pop()
        semantic_stack.append(
            Symbol(lexeme="", var_type='int', addressing_type='relative', address=relative_address, scope=-1,
                   symbol_type='variable'))


def generate_code(*, action: str, label: str):
    return new_generate_code(action=action, label=label)

    global program_block_counter
    print('generating code for %s and %s' % (action, label))
    if action == "#push_id":
        identifier = re.match(r'\((\w+), (\w+)\)', label).group(2)
        address = symbol_table.get_symbol(identifier)[1]
        semantic_stack.append(address)

    elif action == '#push_number':
        # print(label)
        p = re.compile(r'\((\w+), (\d+)\)')
        m = p.match(label)
        a = m.group(1)
        b = m.group(2)
        # print(a, b)
        temp_address = symbol_table.get_temp()
        write_to_program_block(code="(ASSIGN, #%s, %d, )" % (b, temp_address))
        semantic_stack.append(temp_address)
    elif action == '#multiply':
        first_operand_address = semantic_stack[-1]
        second_operand_address = semantic_stack[-2]
        semantic_stack.pop()
        semantic_stack.pop()
        temp_address = symbol_table.get_temp()
        write_to_program_block(
            code="(MULT, %s, %s, %s)" % (first_operand_address, second_operand_address, temp_address))
        semantic_stack.append(temp_address)
    elif action == "#assign":
        # print("         ", semantic_stack)
        destination = semantic_stack[-2]
        source = semantic_stack[-1]
        semantic_stack.pop()
        write_to_program_block(code="(ASSIGN, %s, %s, )" % (source, destination))
    elif action == '#pop':
        print("popping from semantic stack", semantic_stack)
        semantic_stack.pop()
    elif action == '#push_addition_operator':
        semantic_stack.append('ADD')
    elif action == '#push_subtraction_operator':
        semantic_stack.append('SUB')
    elif action == '#add_or_subtract':
        operator = semantic_stack[-2]
        first_operand_address = semantic_stack[-3]
        second_operand_address = semantic_stack[-1]
        address = symbol_table.get_temp()
        write_to_program_block(
            code="(%s, %s, %s, %s)" % (operator, first_operand_address, second_operand_address, address))
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.append(address)
    elif action == '#save':
        semantic_stack.append(program_block_counter)
        write_to_program_block(code=None)
    elif action == '#jump_false_save':
        number_of_saved_line = semantic_stack[-1]
        comparison_result_address = get_symbol_address(semantic_stack[-2])
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.append(program_block_counter)
        write_to_program_block(code=None)
        write_to_program_block(code="(JPF, %s, %s, )" % (comparison_result_address, program_block_counter),
                               line_number=number_of_saved_line)

    elif action == '#jump':
        number_of_saved_line = semantic_stack[-1]
        write_to_program_block(code="(JP, %s, , )" % program_block_counter,
                               line_number=number_of_saved_line)
        semantic_stack.pop()
    elif action == '#label':
        semantic_stack.append(program_block_counter)
    elif action == '#while':
        before_while_condition_line_number = semantic_stack[-3]
        comparison_result_address = semantic_stack[-2]
        after_while_condition_line_number = semantic_stack[-1]
        write_to_program_block(code="(JP, %s, , )" % before_while_condition_line_number)
        write_to_program_block(code="(JPF, %s, %s, )" % (comparison_result_address, program_block_counter),
                               line_number=after_while_condition_line_number)
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.pop()
    elif action == '#push_less_than_comparator':
        semantic_stack.append('LT')
    elif action == '#push_is_equal_comparator':
        semantic_stack.append('EQ')
    elif action == '#relop':
        first_operand_address = semantic_stack[-3]
        operator = semantic_stack[-2]
        second_operand_address = semantic_stack[-1]
        address = symbol_table.get_temp()
        write_to_program_block(
            code="(%s, %s, %s, %s)" % (operator, first_operand_address, second_operand_address, address))
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.append(address)
    elif action == '#negate':
        first_operand_address = semantic_stack[-1]
        result_address = symbol_table.get_temp()
        write_to_program_block(
            code="(MULT, %s, #-1, %s)" % (first_operand_address, result_address))
        semantic_stack.pop()
        semantic_stack.append(result_address)
    elif action == '#push_type':
        print()
        # var_type = re.match(r'\((\w+), (\w+)\)', label).group(2)
        # semantic_stack.append(var_type)
        # print('var_type is:', var_type)
    elif action == '#variable_definition':
        print()
    elif action == '#define_var':
        var_name = re.match(r'\((\w+), (\w+)\)', label).group(2)
        symbol_table.get_symbol(var_name)
    elif action == '#array_extend':
        arr_size = int(re.match(r'\((\w+), (\w+)\)', label).group(2))
        symbol_table.extend(arr_size - 1)
    elif action == '#function_call':
        # TODO for phase 4: must change. now it is just for output
        write_to_program_block(code="(PRINT, %s, , )" % semantic_stack[-1])
        semantic_stack.pop()
    elif action == '#array_access':
        array_address = semantic_stack[-2]
        index_address = semantic_stack[-1]
        index_mul4_address = symbol_table.get_temp()
        result_address = symbol_table.get_temp()
        write_to_program_block(
            code="(MULT, #%s, %s, %s)" % (symbol_table.byte_length, index_address, index_mul4_address))
        write_to_program_block(code="(ADD, #%s, %s, %s)" % (array_address, index_mul4_address, result_address))
        semantic_stack.pop()
        semantic_stack.pop()
        semantic_stack.append("@" + str(result_address))






    # rottenness
    # this part is rotten!!!!!!!!

    elif action == '#start_switch':
        flag_address = symbol_table.get_temp()
        write_to_program_block(code="(ASSIGN, #1, %s, )" % flag_address)
        semantic_stack.append(flag_address)
    elif action == '#start_scope':
        write_to_program_block(code="(JP, %s, , )" % (program_block_counter + 2))
        semantic_stack.append(program_block_counter)
        write_to_program_block(code=None)
    elif action == '#case':
        flag_address = semantic_stack[-4]
        switch_expression_address = semantic_stack[-2]
        case_expression_address = semantic_stack[-1]
        semantic_stack.pop()
        comparison_result_address = symbol_table.get_temp()
        write_to_program_block(
            code="(EQ, %s, %s, %s)" % (switch_expression_address, case_expression_address, comparison_result_address))
        semantic_stack.append(comparison_result_address)
        semantic_stack.append(program_block_counter)
        write_to_program_block(code=None)
        write_to_program_block(code="(ASSIGN, #0, %s, )" % flag_address)
    elif action == '#end_case':
        number_of_saved_line = semantic_stack[-1]
        comparison_result_address = semantic_stack[-2]
        write_to_program_block(code="(JPF, %s, %s, )" % (comparison_result_address, program_block_counter),
                               line_number=number_of_saved_line)
        semantic_stack.pop()
        semantic_stack.pop()
    elif action == '#check_default':
        number_of_saved_line = semantic_stack[-1]
        flag_address = semantic_stack[-4]
        write_to_program_block(code="(JPF, %s, %s, )" % (flag_address, program_block_counter),
                               line_number=number_of_saved_line)
        semantic_stack.pop()
    elif action == '#break':
        scope_start_address = semantic_stack[-4]
        write_to_program_block(code="(JP, %s, , )" % scope_start_address)
    elif action == '#end_switch':
        semantic_stack.pop()
    elif action == '#end_scope':
        scope_start_address = semantic_stack[-1]
        semantic_stack.pop()
        write_to_program_block(code="(JP, %s, , )" % program_block_counter, line_number=scope_start_address)
