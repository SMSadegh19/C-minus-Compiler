# compiler exercise 2
# Amir Mohammad Ghasemi - 97100495
# Mohammad Sadegh Salimi - 97101829
import Parser


# import typing
# from Scanner import Scanner
# from ScannerDFA import dfa
# from Scanner import KEYWORDS
#
# lexical_errors_file = open(file='lexical_errors.txt', mode="w")
# tokens_file = open(file='tokens.txt', mode="w")
# symbol_table_file = open(file='symbol_table.txt', mode="w")
#
# tokens = []
# symbol_table = dict()
# symbol_table: typing.Dict
# symbol_table_counter = 1
#
#
# def add_to_symbol_table(lexeme: str):
#     global symbol_table_counter
#     if lexeme in symbol_table:
#         return
#     symbol_table[lexeme] = symbol_table_counter
#     symbol_table_file.write("%d.\t%s\n" % (symbol_table_counter, lexeme))
#     symbol_table_counter += 1
#
#
# for keyword in KEYWORDS:
#     add_to_symbol_table(keyword)
#
#
# def append_token_to_file(token_type: str, token_content: str):
#     tokens_file.write("(%s, %s) " % (token_type, token_content))
#
#
# def write_line_tokens(correct_tokens: typing.List, line_number: int):
#     if not correct_tokens:
#         return
#     tokens_file.write("%d.\t" % (line_number))
#     for token in correct_tokens:
#         append_token_to_file(token[0], token[1])
#     tokens_file.write("\n")
#
#
# def append_lexical_error_to_file(token_type: str, token_content: str):
#     lexical_errors_file.write("(%s, %s) " % (token_content, token_type))
#
#
# def write_line_lexical_errors(lexical_error_tokens: typing.List, line_number: int):
#     if not lexical_error_tokens:
#         return
#     lexical_errors_file.write("%d.\t" % (line_number))
#     for token in lexical_error_tokens:
#         append_lexical_error_to_file(token[0], token[1])
#     lexical_errors_file.write("\n")
#
#
# def process_line_tokens(line_number: int):
#     global tokens, has_lexical_error
#     correct_tokens = []
#     lexical_error_tokens = []
#     for token in tokens:
#         # write to symbol_table.txt
#         if token[0] in ['KEYWORD', 'ID']:
#             add_to_symbol_table(token[1])
#         # write to tokens.txt and lexical_errors.txt
#         if token[0] in ['NUM', 'SYMBOL', 'KEYWORD', 'ID']:
#             correct_tokens.append(token)
#         elif token[0] in ['Invalid number', 'Invalid input', 'Unmatched comment', 'Unclosed comment']:
#             has_lexical_error = True
#             lexical_error_tokens.append(token)
#     write_line_tokens(correct_tokens, line_number)
#     write_line_lexical_errors(lexical_error_tokens, line_number)
#     # emptying (tokens) list
#     tokens = []
#
#
# source = open(file='input.txt', mode="r")
# scanner = Scanner(dfa=dfa, source=source)
#
# has_lexical_error = False
# token_presentation = scanner._get_next_token()
# current_line = token_presentation[2]
# while token_presentation[0] != 'EOF':
#     if token_presentation[2] != current_line:
#         process_line_tokens(current_line)
#         current_line = token_presentation[2]
#     tokens.append(token_presentation)
#     token_presentation = scanner._get_next_token()
#
# # last line
# process_line_tokens(current_line)
#
# # print "There is no lexical error." in lexical_errors.txt
# if not has_lexical_error:
#     lexical_errors_file.write("There is no lexical error.")
