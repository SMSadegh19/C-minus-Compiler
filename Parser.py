import typing
from anytree import AnyNode, RenderTree, Node
import anytree
from Scanner import get_next_token

# root = AnyNode(name='Program')
# c1 = AnyNode(parent=root, name)

non_terminals = set()
grammars = set()
first_sets = dict()
follow_sets = dict()

EPSILON = 'Îµ'

firsts_file = open(file='Firsts.txt', mode='r')
follows_file = open(file='Follows.txt', mode='r')
predicts_file = open(file='Predicts.txt', mode='r')
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


token = get_next_token()


def dfs(*, label: str, parent: Node = None):
    global token
    token_type = token[1] if token[0] in ['SYMBOL', 'KEYWORD'] else token[0]
    # print("--------------------\n\n")
    # print("tokens: ", token, token_type)
    # print("stack:", top, list(reversed(stack)))
    node = anytree.Node(label)
    if parent:
        node.parent = parent

    if label in non_terminals:
        # print("in non terminals")
        # if token_type in table[top]:
        # print(table[label][token_type])

        if table[label][token_type] != 'sync':
            # print("replacing ", table[label][token_type])
            for symbol in table[label][token_type]:
                if symbol != EPSILON:
                    dfs(label=symbol, parent=node)
        else:
            pass
            print('         missing non terminal %s' % label)
        # else:
        #     print('illegal %s' % token_type)
        #     token = get_next_token()
    else:
        if label == token_type:
            # print("         received token %s" % label)
            node.name = token
            token = get_next_token()
        else:
            pass
            print('         missing terminal %s' % label)
    return node


root = dfs(label='Program', parent=None)
# print(RenderTree(root, style=anytree.render.DoubleStyle))

for pre, _, node in RenderTree(root):
    print("%s%s" % (pre, node.name))
