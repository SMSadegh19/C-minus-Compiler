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

# stack = ["Program"]
# token = get_next_token()
"""
while token != '$':
    top = stack.pop()
    token_type = token[1] if token[0] in ['SYMBOL', 'KEYWORD'] else token[0]
    print("--------------------\n\n")
    print("tokens: ", token, token_type)
    print("stack:", top, list(reversed(stack)))
    if top in non_terminals:
        print("in non terminals")
        # if token_type in table[top]:
        print(table[top][token_type])

        if table[top][token_type] != 'sync':
            print("replacing ", table[top][token_type])
            for symbol in reversed(table[top][token_type]):
                if symbol != EPSILON:
                    stack.append(symbol)
            print("after stack:", list(reversed(stack)))
        else:
            print('         missing non terminal %s' % top)
        # else:
        #     print('illegal %s' % token_type)
        #     token = get_next_token()
    else:
        if top == token_type:
            print("         received token %s" % top)
            token = get_next_token()
        else:
            print('         missing terminal %s' % top)
    # input()
"""


def print_error(error_line: int, error_message: str):
    syntax_errors_file.write("#%s : %s\n" % (error_line, error_message))


def dfs(*, label: str, parent: anytree.Node = None):
    # print("entering node ", label)
    global token_presentation, token_type, token_line

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
syntax_errors_file = open(file='syntax_errors.txt', mode='w')
parse_tree_file = open(file='parse_tree.txt', mode='w', encoding='utf-8')

root = dfs(label='Program', parent=None)

for pre, _, node in anytree.RenderTree(root):
    s = "%s%s\n" % (pre, node.name)
    parse_tree_file.writelines(s)
