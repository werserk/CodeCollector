import os
from typing import List, Any

import click


def should_ignore(filepath: str, ignore_paths: List[str]) -> bool:
    """Check if the file or directory should be ignored."""
    basename = os.path.basename(filepath)
    if any(
        filepath.startswith(ignore_path.rstrip("/") + "/")
        for ignore_path in ignore_paths
    ):
        return True
    if basename in ignore_paths:
        return True
    # Ignore hidden files and directories
    if basename.startswith(".") and filepath not in ignore_paths:
        return True
    return False


def tree(
    directory: str, prefix: str, ignore_paths: List[str], tree_lines: List[str]
) -> None:
    """A recursive function to generate the tree structure."""
    prefix += "    "
    items = sorted(os.listdir(directory))
    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        if should_ignore(path, ignore_paths):
            continue
        connector = "└── " if index == len(items) - 1 else "├── "
        if os.path.isdir(path):
            tree_lines.append(f"{prefix}{connector}{item}/")
            tree(
                path,
                prefix + ("    " if connector == "└── " else "│   "),
                ignore_paths,
                tree_lines,
            )
        else:
            tree_lines.append(f"{prefix}{connector}{item}")


def generate_tree_structure(paths_to_search: List[str], ignore_paths: List[str]) -> str:
    """Generate a tree structure of the project."""
    tree_lines = []
    for path in paths_to_search:
        if os.path.isdir(path):
            tree_lines.append(os.path.abspath(path) + "/")
            tree(path, "", ignore_paths, tree_lines)
        elif os.path.isfile(path) and not should_ignore(path, ignore_paths):
            tree_lines.append(f"{os.path.basename(path)}")
    return "\n".join(tree_lines)


def process_file(filepath: str, outfile: Any) -> None:
    """Write the contents of the file to the output file."""
    with open(filepath, "r", encoding="utf-8") as infile:
        code = infile.read()
        outfile.write(f"Filepath: {filepath}\n")
        outfile.write(code)
        outfile.write("\n================\n")


def process_directory(
    directory: str, file_formats: List[str], ignore_paths: List[str], outfile: Any
) -> None:
    """Recursively process a directory, writing file contents to the output file."""
    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d for d in dirs if not should_ignore(os.path.join(root, d), ignore_paths)
        ]
        for file in files:
            filepath = os.path.join(root, file)
            if not should_ignore(filepath, ignore_paths):
                if not file_formats or filepath.endswith(tuple(file_formats)):
                    process_file(filepath, outfile)


def read_code_files(
    paths_to_search: List[str],
    file_formats: List[str],
    ignore_paths: List[str],
    output_file: str,
) -> None:
    """Read code files and write their contents to the output file."""
    with open(output_file, "w", encoding="utf-8") as outfile:
        tree_structure = generate_tree_structure(paths_to_search, ignore_paths)
        outfile.write("Project Structure:\n")
        outfile.write(tree_structure)
        outfile.write("\n\nCode Files:\n")
        outfile.write("================\n")

        for path in paths_to_search:
            if os.path.isfile(path):
                if not should_ignore(path, ignore_paths):
                    if not file_formats or path.endswith(tuple(file_formats)):
                        process_file(path, outfile)
            elif os.path.isdir(path):
                process_directory(path, file_formats, ignore_paths, outfile)


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--formats",
    "-f",
    multiple=True,
    help="File formats to include. If not specified, all files are included.",
)
@click.option(
    "--ignore-paths",
    "-i",
    multiple=True,
    type=click.Path(),
    help="Paths (files or directories) to ignore.",
)
@click.option("--output", "-o", default="collected_code.txt", help="Output file name.")
def cli(
    paths: List[str], formats: List[str], ignore_paths: List[str], output: str
) -> None:
    """Collect code from files and directories."""
    read_code_files(paths, formats, ignore_paths, output)


if __name__ == "__main__":
    cli()
