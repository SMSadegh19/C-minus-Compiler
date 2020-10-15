import Scanner

lexical_errors = open(file='lexical_errors.txt', mode="w")
tokens_file = open(file='tokens.txt', mode="w")
symbol_table_file = open(file='symbol_table.txt', mode="w")

def write_to_file(file, content: str):
    file.write(content)


def append_token_to_file(token_type: str, token_content: str, line_number: int):
    write_to_file(tokens_file, "%d.  (%s, %s)\n" % (line_number, token_type, token_content))


def append_lexical_error_to_file(token_type: str, token_content: str, line_number: int):
    write_to_file(lexical_errors, "%d. (%s, %s)\n" % (line_number, token_type, token_content))


def process_dfa_token(token_type, token_content, line_number):
    if token_type in ['NUM', 'SYMBOL', 'KEYWORD', 'ID']:
        append_token_to_file(token_type, token_content, line_number)
    if token_type in ['Invalid number', 'Invalid input', 'Unmatched comment', 'Unclosed comment']:
        append_lexical_error_to_file(token_type, token_content, line_number)


token = Scanner.get_next_token()
while token != 'EOF':
    process_dfa_token(token[0], token[1], token[2])
    token = Scanner.get_next_token()
