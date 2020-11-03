import typing
import anytree
from ScannerDFA import dfa
from Scanner import Scanner

non_terminals = set()
grammars = set()
first_sets = dict()
follow_sets = dict()

EPSILON = 'Îµ'

firsts_file = open(file='phase 2/Firsts.txt', mode='r')
follows_file = open(file='phase 2/Follows.txt', mode='r')
predicts_file = open(file='phase 2/Predicts.txt', mode='r')
grammar_file = open(file='phase 2/grammar.txt', mode='r')

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


def dfs(*, label: str, parent: anytree.Node = None):
    global token_presentation, token_type
    # print("--------------------\n\n")
    # print("tokens: ", token, token_type)
    # print("stack:", top, list(reversed(stack)))

    node = anytree.Node(label)
    if parent:
        node.parent = parent
    if label == EPSILON:
        node.name = 'epsilon'
        return node

    # print(token_presentation, token_type, label)
    if label in non_terminals:
        # print("in non terminals")
        # if token_type in table[top]:
        # print(table[label][token_type])
        while (token_type not in table[label]) and token_type != '$':
            print('         syntax error, illegal token', token_type)
            token_type, token_presentation = scanner.get_next_token()
            # print(token_presentation, token_type)
        # if token_type == '$':
        #     return node

        if table[label][token_type] == 'sync':
            pass
            print('         missing %s' % label)
        else:
            # print("replacing ", table[label][token_type])
            for symbol in table[label][token_type]:
                if symbol != EPSILON or len(table[label][token_type]) == 1:
                    dfs(label=symbol, parent=node)
        # else:
        #     print('illegal %s' % token_type)
        #     token = get_next_token()
    else:
        if label == token_type:
            # print("         received token %s" % label)
            node.name = token_presentation
            token_type, token_presentation = scanner.get_next_token()
        else:
            pass
            print('         syntax error, missing %s' % label)
    return node


source = open(file='input.txt', mode="r")
scanner = Scanner(dfa=dfa, source=source)
token_type, token_presentation = scanner.get_next_token()

root = dfs(label='Program', parent=None)

for pre, _, node in anytree.RenderTree(root):
    print("%s%s" % (pre, node.name))
