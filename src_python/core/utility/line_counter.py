import os
import subprocess

import os
import subprocess
from pathlib import Path

def count_lines_of_code(file_extensions=None, subdirs=None):
    """
    Count the total number of lines of code in selected file types
    under all subdirectories from the current working directory.

    Args:
        file_extensions (list): List of file extensions to include (e.g., ['.py', '.cs']).
        subdirs (list or None): If None, all subdirectories will be included.
    """
    if file_extensions is None:
        file_extensions = ['.py', '.cs']

    if subdirs is None:
        # Default to all subdirectories from current directory
        subdirs = [str(p) for p in Path("../..").rglob("*") if p.is_dir()]

    # Get list of files tracked by Git
    result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
    all_files = result.stdout.splitlines()

    # Filter files by subdir and extension
    filtered_files = [
        file for file in all_files
        if any(os.path.abspath(file).startswith(os.path.abspath(subdir) + os.sep) for subdir in subdirs)
        and file.endswith(tuple(file_extensions))
        and not file.endswith('.cs.meta')
    ]

    total_lines = 0
    file_line_counts = {}

    for file in filtered_files:
        try:
            with open(file, 'r', errors='ignore') as f:
                line_count = sum(1 for _ in f)
                total_lines += line_count
                file_line_counts[file] = line_count
        except FileNotFoundError:
            print(f"File not found (likely deleted): {file}")

    print(f"Total lines of code: {total_lines}\n")
    print("Lines per file:")
    for file, count in file_line_counts.items():
        print(f"{file}: {count} lines")



if __name__ == "__main__":
    # Example usage: Count Python and C# files in 'src' and 'tests' subdirectories
    count_lines_of_code(file_extensions=['.py', '.cs'])
