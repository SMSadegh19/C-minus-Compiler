import typing
import anytree
from ScannerDFA import dfa
from Scanner import Scanner

non_terminals = set()
grammars = set()
first_sets = dict()
follow_sets = dict()

EPSILON = 'ε'
# EPSILON = 'Îµ'

firsts_file = open(file='Firsts.txt', mode='r', encoding='utf-8')
follows_file = open(file='Follows.txt', mode='r', encoding='utf-8')
predicts_file = open(file='Predicts.txt', mode='r', encoding='utf-8')
grammar_file = open(file='grammar.txt', mode='r', encoding='utf-8')

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
        if p != EPSILON:
            table[left_non_terminal][p] = rule

for non_terminal in non_terminals:
    if EPSILON not in first_sets[non_terminal]:
        for follow_terminal in follow_sets[non_terminal]:
            if follow_terminal not in first_sets[non_terminal]:
                table[non_terminal][follow_terminal] = 'sync'

def print_error(error_line: int, error_message: str):
    syntax_errors_file.write("#%s : %s\n" % (error_line, error_message))


def dfs(*, label: str, parent: anytree.Node = None):
    global token_presentation, token_type, token_line, EOF_error
    if EOF_error:
        return
    # print("entering node ", label, token_type, token_presentation)
    node = anytree.Node(label)
    if parent:
        node.parent = parent
    if label == EPSILON:
        node.name = 'epsilon'
        return node

    error_node = False
    if label in non_terminals:
        while (token_type not in table[label]) and token_type != '$':
            print_error(token_line, "syntax error, illegal %s" % token_type)
            token_type, token_presentation, token_line = scanner.get_next_token()
        if token_type == '$' and token_type not in table[label]:
            print_error(token_line, "syntax error, Unexpected EOF")
            EOF_error = True
            error_node = True
        elif table[label][token_type] == 'sync':
            print_error(token_line, "missing %s" % label)
            error_node = True
        else:
            for symbol in table[label][token_type]:
                if symbol != EPSILON or len(table[label][token_type]) == 1:
                    dfs(label=symbol, parent=node)
    else:
        if label == token_type:
            node.name = token_presentation
            token_type, token_presentation, token_line = scanner.get_next_token()
        else:
            print_error(token_line, "syntax error, missing %s" % label)
            error_node = True
    if error_node:
        node.parent = None
    return node



source = open(file='input.txt', mode="r", encoding='utf-8')
scanner = Scanner(dfa=dfa, source=source)
token_type, token_presentation, token_line = scanner.get_next_token()
EOF_error = False
syntax_errors_file = open(file='syntax_errors.txt', mode='w')
parse_tree_file = open(file='parse_tree.txt', mode='w', encoding='utf-8')

# root = dfs(label='Program', parent=None)
root = None

stack = [('Program', None)]

while stack:
    # print("entering node ", label, token_type, token_presentation)
    # print(stack)
    label, parent = stack.pop()
    node = anytree.Node(label)
    if parent:
        node.parent = parent
    if label == EPSILON:
        node.name = 'epsilon'
        continue
    if label == "Program":
        root = node

    error_node = False
    if label in non_terminals:
        while (token_type not in table[label]) and token_type != '$':
            print_error(token_line, "syntax error, illegal %s" % token_type)
            token_type, token_presentation, token_line = scanner.get_next_token()
        if token_type == '$' and token_type not in table[label]:
            print_error(token_line, "syntax error, Unexpected EOF")
            node.parent = None
            break
        elif table[label][token_type] == 'sync':
            print_error(token_line, "missing %s" % label)
            error_node = True
        else:
            for symbol in reversed(table[label][token_type]):
                if symbol != EPSILON or len(table[label][token_type]) == 1:
                    stack.append((symbol, node))
    else:
        if label == token_type:
            node.name = token_presentation
            token_type, token_presentation, token_line = scanner.get_next_token()
        else:
            print_error(token_line, "syntax error, missing %s" % label)
            error_node = True
    if error_node:
        node.parent = None


for pre, _, node in anytree.RenderTree(root):
    s = "%s%s\n" % (pre, node.name)
    parse_tree_file.writelines(s)
