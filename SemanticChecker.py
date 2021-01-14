import Scanner

semantic_errors_file = open(file='semantic_errors.txt', mode='w')
has_semantic_error = False


def semantic_check(*, check_error, p1='', p2='', p3='', p4=''):
    global has_semantic_error
    has_semantic_error = True
    semantic_errors_file.write("#%s : Semantic Error! " % Scanner.program_line)
    if check_error == 'break':
        # 4
        semantic_errors_file.write("No 'while' or 'switch' found for 'break'.\n")
    elif check_error == 'undefined':
        # 1
        semantic_errors_file.write("\'%s\' is not defined.\n" % p1)
    elif check_error == 'void_var':
        # 2
        semantic_errors_file.write("Illegal type of void for \'%s\'.\n" % p1)
    elif check_error == 'arguments_count':
        # 3
        semantic_errors_file.write("Mismatch in numbers of arguments of \'%s\'.\n" % p1)
