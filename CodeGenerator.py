import typing
import re
from SymbolTable import SymbolTable

symbol_table = SymbolTable()

semantic_stack = []

program_block = {}
program_block_counter = 0


def write_to_program_block(*, code: typing.Union[None, str], line_number: int = None):
    global program_block_counter
    print("appending", code, " to line", line_number)
    print("                 ", program_block_counter)
    if line_number is None:
        program_block[program_block_counter] = code
        program_block_counter += 1
    else:
        program_block[line_number] = code


def generate_code(*, action: str, label: str):
    global program_block_counter
    print('generating code for %s and %s' % (action, label))
    if action == "#push_id":
        identifier = re.match(r'\((\w+), (\w+)\)', label).group(2)
        # print("hellllo ")
        # print(identifier)
        address = symbol_table.get_symbol(identifier)[1]
        # print(address)
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
        comparison_result_address = semantic_stack[-2]
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
        result_address = symbol_table.get_temp()
        write_to_program_block(code="(ADD, #%s, %s, %s)" % (array_address, index_address, result_address))
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
