import boring

while True:
    inp = input('boring > ')
    if inp.strip() == "": continue
    result, error = boring.run("<stdin>", inp)

    if error: print(error.as_string())
    elif result:
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))