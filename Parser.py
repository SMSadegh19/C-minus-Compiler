import typing
from anytree import Node, RenderTree
from ScannerDFA import dfa
from Scanner import Scanner
import re
from CodeGenerator import generate_code

non_terminals = set()
grammars = set()
first_sets = dict()
follow_sets = dict()
has_syntax_error = False

EPSILON = 'ε'

firsts_file = open(file='Firsts.txt', mode='r', encoding='utf-8')
follows_file = open(file='Follows.txt', mode='r', encoding='utf-8')
predicts_file = open(file='Predicts.txt', mode='r', encoding='utf-8')
grammar_file = open(file='AugmentedGrammar.txt', mode='r', encoding='utf-8')

lines = firsts_file.readlines()
for line in lines:
    symbols = line.split()
    beginning_non_terminal = symbols[0]
    first_sets[beginning_non_terminal] = set(symbols[1:])

lines = follows_file.readlines()
for line in lines:
    symbols = line.split()
    beginning_non_terminal = symbols[0]
    follow_sets[beginning_non_terminal] = set(symbols[1:])

predict_lines = predicts_file.readlines()

grammar_lines = grammar_file.readlines()
for line in grammar_lines:
    symbols = line.split()
    beginning_non_terminal = symbols[0]
    if beginning_non_terminal not in non_terminals:
        non_terminals.add(beginning_non_terminal)

table = dict()
for non_terminal in non_terminals:
    table[non_terminal] = dict()

for i in range(len(predict_lines)):
    line = grammar_lines[i]
    symbols = line.split()
    left_non_terminal = symbols[0]
    rule = symbols[2:]
    predict_line = predict_lines[i]
    predict_terminals = set(predict_line.split())
    for p in predict_terminals:
        table[left_non_terminal][p] = rule

for non_terminal in non_terminals:
    if EPSILON not in first_sets[non_terminal]:
        for follow_terminal in follow_sets[non_terminal]:
            if follow_terminal not in first_sets[non_terminal]:
                table[non_terminal][follow_terminal] = 'sync'


def print_error(error_line: int, error_message: str):
    syntax_errors_file.write("#%s : %s\n" % (error_line, error_message))
    global has_syntax_error
    has_syntax_error = True


source = open(file='input.cpp', mode="r", encoding='utf-8')
scanner = Scanner(dfa=dfa, source=source)
last_token_type = None
token_type, token_presentation, token_line = scanner.get_next_token()
EOF_error = False
syntax_errors_file = open(file='syntax_errors.txt', mode='w')
parse_tree_file = open(file='parse_tree.txt', mode='w', encoding='utf-8')


root = Node(name='Program', parent=None)

stack = [root]
stack: typing.List[Node]

while stack:
    node = stack.pop()
    label = node.name
    if label == EPSILON:
        node.name = 'epsilon'
        continue

    if re.match(r'#\w+', label):
        generate_code(action=label, label=last_token_type)
        last_token_type = token_presentation
        node.parent = None
        continue

    error_node = False
    if label in non_terminals:
        while token_type not in table[label] and token_type != '$':
            print_error(token_line, "بذsyntax error, illegal %s" % token_type)
            last_token_type = token_presentation
            token_type, token_presentation, token_line = scanner.get_next_token()
        if token_type == '$' and token_type not in table[label]:
            print_error(token_line, "syntax error, Unexpected EOF")
            node.parent = None
            break
        elif table[label][token_type] == 'sync':
            print_error(token_line, "syntax error, missing %s" % label)
            error_node = True
        else:
            children = []
            for symbol in table[label][token_type]:
                children.append(Node(name=symbol, parent=node))
            for child in reversed(children):
                stack.append(child)
    else:
        if label == token_type:
            node.name = token_presentation
            last_token_type = token_presentation
            token_type, token_presentation, token_line = scanner.get_next_token()
        else:
            print_error(token_line, "syntax error, missing %s" % label)
            error_node = True
    if error_node:
        node.parent = None

while stack:
    stack.pop().parent = None

parse_tree_file.write(RenderTree(root).by_attr("name"))

if not has_syntax_error:
    syntax_errors_file.write("There is no syntax error.")


from CodeGenerator import program_block

for line_number, line in program_block.items():
    print("%s: %s" % (line_number, line))
