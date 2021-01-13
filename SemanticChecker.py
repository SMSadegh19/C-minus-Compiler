import Scanner

semantic_errors_file = open(file='semantic_errors.txt', mode='w')
has_semantic_error = False


def semantic_check(*, check_error, p1='', p2='', p3='', p4=''):
    global has_semantic_error
    has_semantic_error = True
    semantic_errors_file.write("#%s : Semantic Error! " % Scanner.program_line)
    if check_error == 'break':
        semantic_errors_file.write("No 'while' or 'switch' found for 'break'.\n")
    elif check_error == 'undefined':
        semantic_errors_file.write("\'%s\' is not defined.\n" % p1)
