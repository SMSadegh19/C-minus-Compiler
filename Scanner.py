import typing

source_text = open(file='input.txt', mode="r")

i = 0
while True:
    i += 1
    c = source_text.read(1)
    if not c:
        print(c, c, c, c, c)
        break
    a = ord(c)
    print(i, c, a)

