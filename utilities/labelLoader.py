def load_lables_from_file(path: str):
    classes=[]
    file= open(path,'r')

    while True:
        name=file.readline().strip('\n')
        classes.append(name)
        if not name:
            break
    return classes
