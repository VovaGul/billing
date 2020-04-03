class IteratorFile:
    """итератор файла"""
    def __init__(self, path_file):
        self.file = open(path_file, 'r')

    def __iter__(self):
        return self

    def __next__(self):
        line = self.file.readline()
        if line != '':
            return line.rstrip('\n')
        self.file.close()
        raise StopIteration


def read_file(path_file):
    """читает файл"""
    with open(path_file, 'r') as file:
        return file.read()


def write_file(path_file, content):
    """записывает информацию в файл"""
    with open(path_file, 'w') as file:
        file.write(content)
