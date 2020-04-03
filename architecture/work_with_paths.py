import architecture.work_with_files
from re import compile

BACKSLASH_RE = compile(r'\\')


def turn_slash(path_file):
    """заменяет обратные слеши прямыми"""
    return BACKSLASH_RE.sub('/', path_file)


def put_memory_path(memory_path_file, path_file):
    """возвращает сохраненный путь до файла, если новый не указан"""
    if path_file is None:
        return turn_slash(architecture.work_with_files.read_file(memory_path_file))
    architecture.work_with_files.write_file(memory_path_file, turn_slash(path_file))
    return turn_slash(path_file)
