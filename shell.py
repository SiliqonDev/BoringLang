import boring

while True:
    inp = input('boring > ')
    result, error = boring.run("<stdin>", inp)

    if error: print(error.as_string())
    else: print(result)