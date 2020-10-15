import typing
import Scanner

lexical_errors_file = open(file='lexical_errors.txt', mode="w")
tokens_file = open(file='tokens.txt', mode="w")
symbol_table_file = open(file='symbol_table.txt', mode="w")

tokens = []


def append_token_to_file(token_type: str, token_content: str):
    tokens_file.write("(%s, %s) " % (token_type, token_content))


def write_line_tokens(correct_tokens: typing.List, line_number: int):
    if not correct_tokens:
        return
    tokens_file.write("%d.\t" % (line_number))
    for token in correct_tokens:
        append_token_to_file(token[0], token[1])
    tokens_file.write("\n")



def append_lexical_error_to_file(token_type: str, token_content: str):
    lexical_errors_file.write("(%s, %s) " % (token_content, token_type))


def write_line_lexical_errors(lexical_error_tokens: typing.List, line_number: int):
    if not lexical_error_tokens:
        return
    lexical_errors_file.write("%d.\t" % (line_number))
    for token in lexical_error_tokens:
        append_lexical_error_to_file(token[0], token[1])
    lexical_errors_file.write("\n")


def process_line_tokens(line_number: int):
    global tokens
    correct_tokens = []
    lexical_error_tokens = []
    for token in tokens:
        if token[0] in ['NUM', 'SYMBOL', 'KEYWORD', 'ID']:
            correct_tokens.append(token)
        elif token[0] in ['Invalid number', 'Invalid input', 'Unmatched comment', 'Unclosed comment']:
            lexical_error_tokens.append(token)
    write_line_tokens(correct_tokens, line_number)
    write_line_lexical_errors(lexical_error_tokens, line_number)
    # emptying (tokens) list
    tokens = []


token = Scanner.get_next_token()
current_line = token[2]
while token != 'EOF':
    if token[2] != current_line:
        process_line_tokens(current_line)
        current_line = token[2]
    tokens.append(token)
    token = Scanner.get_next_token()

# last line
process_line_tokens(current_line)