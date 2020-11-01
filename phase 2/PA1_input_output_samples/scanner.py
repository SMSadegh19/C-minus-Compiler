class Util:
    @classmethod
    def read(cls, file_name):
        with open(file_name + '.txt', 'r') as content_file:
            content = content_file.read()
        return content


file = Util.read('input')
unread_parts = file
line_num = 1
symbol_table = []
errors = {}
tokens = {}
# except for = and ==
symbols = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '<']
keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return']
spaces = [' ', '\n', '\t', '\r', '\v', '\f']


def generate_error(error_token_pair):
    error_type = error_token_pair[0]
    if error_type == 'UNFINISHED_COMMENT_ERROR':
        return f'({error_token_pair[1]}, Unclosed comment)'
    elif error_type == 'UNBALANCED_COMMENT_ERROR':
        return f'({error_token_pair[1]}, Unmatched comment)'
    elif error_type == 'INVALID_NUMBER_ERROR':
        return f'({error_token_pair[1]}, Invalid number)'
    else:
        return f'({error_token_pair[1]}, Invalid input)'


def report():
    global tokens, errors, symbol_table

    with open('symbol_table.txt', 'w') as sym_table_file:
        for i, token in enumerate(symbol_table):
            sym_table_file.write(f'{i + 1}.\t{token}\n')

    with open('lexical_errors.txt', 'w') as errors_file:
        if len(errors.keys()) == 0:
            errors_file.write("")
        else:
            for i in errors.keys():
                errors_file.write('{}.\t'.format(i))
                for v in errors[i]:
                    errors_file.write('{}'.format(v))
                errors_file.write('\n')

    with open('tokens.txt', 'w') as tokens_file:
        for i in tokens.keys():
            tokens_file.write('{}.\t'.format(i))
            for v in tokens[i]:
                tokens_file.write('{}'.format(v))
            tokens_file.write('\n')


def omit_start(token_type, token_len):
    global unread_parts, symbol_table
    token = unread_parts[:token_len]
    unread_parts = unread_parts[token_len:]
    if token_type == 'ID':
        if token not in symbol_table:
            symbol_table.append(token)
    return token_type, token


def valid_char(char):
    return char.isalnum() or char in symbols + spaces + ['/', '=']


def get_next_token():
    global line_num, unread_parts
    if len(unread_parts) == 0:
        return 'EOF', 'EOF'
    if unread_parts[0].isspace():
        for i in range(len(unread_parts)):
            if not unread_parts[i].isspace():
                return omit_start('WHITESPACE', i)
            elif unread_parts[i] == '\n':
                line_num += 1
    if unread_parts[0] == '/':
        if len(unread_parts) > 1 and unread_parts[1] == '/':
            for i in range(len(unread_parts)):
                if unread_parts[i] == '\n':
                    return omit_start('COMMENT', i)
            return 'COMMENT', unread_parts
        elif len(unread_parts) > 1 and unread_parts[1] == '*':
            for i in range(len(unread_parts)):
                if unread_parts[i] == '*' and i + 1 < len(unread_parts) and unread_parts[i + 1] == '/':
                    return omit_start('COMMENT', i + 2)
            # not sure of it
            comment_start = unread_parts[:min(len(unread_parts), 10)] + "..."
            unread_parts = ""
            return 'UNFINISHED_COMMENT_ERROR', comment_start
        return omit_start('ERROR', 1)
    if unread_parts[0] == '=':
        if len(unread_parts) > 1 and unread_parts[1] == '=':
            return omit_start('SYMBOL', 2)
        return omit_start('SYMBOL', 1)
    if len(unread_parts) > 1 and unread_parts[0] == '*' and unread_parts[1] == '/':
        return omit_start('UNBALANCED_COMMENT_ERROR', 2)
    if unread_parts[0] in symbols:
        return omit_start('SYMBOL', 1)
    if unread_parts[0].isalpha():
        length = len(unread_parts)
        for i in range(len(unread_parts)):
            if not unread_parts[i].isalnum():
                if valid_char(unread_parts[i]):
                    length = i
                    break
                else:
                    return omit_start('ERROR', i + 1)
        if unread_parts[:length] in keywords:
            return omit_start('KEYWORD', length)
        else:
            return omit_start('ID', length)
    if unread_parts[0].isnumeric():
        for i in range(len(unread_parts)):
            if not unread_parts[i].isnumeric():
                if valid_char(unread_parts[i]):
                    return omit_start('NUM', i)
                else:
                    return omit_start('INVALID_NUMBER_ERROR', i + 1)
    if unread_parts[0] in spaces:
        return omit_start('WHITESPACE', 1)
    return omit_start('ERROR', 1)


for keyword in keywords:
    symbol_table.append(keyword)

while True:
    token = get_next_token()
    if token[0] == 'EOF':
        break
    if token[0].endswith('ERROR'):
        if line_num in errors.keys():
            errors[line_num] += ' ' + generate_error(token)
        else:
            errors[line_num] = generate_error(token)
    else:
        if token[0] == 'WHITESPACE' or token[0] == 'COMMENT':
            continue
        if line_num in tokens.keys():
            tokens[line_num] += ' (' + token[0] + ', ' + token[1] + ')'
        else:
            tokens[line_num] = '(' + token[0] + ', ' + token[1] + ')'

report()
