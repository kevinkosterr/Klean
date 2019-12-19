with open('filelist', 'r') as f:
    for filename in f:
        filename = str(filename).split("\n")[0]
        c = open(f"C:\\Users\\koste\\PycharmProjects\\Klean\\files\\{filename}", 'x')
