import os
from typing import List, Dict, Any

import yaml


def load_config(config_file: str) -> Dict[str, Any]:
    """Загружает конфигурацию из YAML файла."""
    with open(config_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def should_ignore(filepath: str, ignore_files: List[str], ignore_dirs: List[str]) -> bool:
    """Проверяет, следует ли игнорировать файл или директорию."""
    if any(filepath.startswith(ignore_dir) for ignore_dir in ignore_dirs):
        return True
    if os.path.basename(filepath) in ignore_files:
        return True
    return False


def process_file(filepath: str, outfile: Any) -> None:
    """Записывает содержимое файла в выходной файл."""
    with open(filepath, 'r', encoding='utf-8') as infile:
        code = infile.read()
        outfile.write(f"Filepath: {filepath}\n")
        outfile.write(code)
        outfile.write("\n================\n")


def process_directory(directory: str, file_formats: List[str], ignore_files: List[str], ignore_dirs: List[str],
                      outfile: Any) -> None:
    """Рекурсивно обрабатывает директорию, записывая содержимое файлов в выходной файл."""
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_files, ignore_dirs)]
        for file in files:
            filepath = os.path.join(root, file)
            if not should_ignore(filepath, ignore_files, ignore_dirs) and filepath.endswith(tuple(file_formats)):
                process_file(filepath, outfile)


def read_code_files(config: Dict[str, Any], output_file: str) -> None:
    """Читает файлы кода и записывает их содержимое в выходной файл."""
    file_formats = config['file_formats']
    ignore_files = config['ignore_files']
    ignore_dirs = config['ignore_dirs']

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for path in config['paths_to_search']:
            if os.path.isfile(path):
                if not should_ignore(path, ignore_files, ignore_dirs) and path.endswith(tuple(file_formats)):
                    process_file(path, outfile)
            elif os.path.isdir(path):
                process_directory(path, file_formats, ignore_files, ignore_dirs, outfile)


if __name__ == "__main__":
    config = load_config('config.yaml')
    output_file = "collected_code.txt"
    read_code_files(config, output_file)
