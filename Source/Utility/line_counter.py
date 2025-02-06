import os
import subprocess

def count_lines_of_code(file_extensions=None, subdirs=None):
    """
    Count the total number of lines of code in Python and C# files
    within specific subdirectories of a Git repository.

    Args:
        file_extensions (list): List of file extensions to include (e.g., ['.py', '.cs']).
        subdirs (list): List of subdirectories to include (e.g., ['src', 'tests']).

    **Note:** This method counts all lines, including comments and blank lines.
    """
    # Default to Python and C# files if no file_extensions are provided
    if file_extensions is None:
        file_extensions = ['.py', '.cs']

    # Get list of files tracked by the Git repository
    result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
    all_files = result.stdout.splitlines()

    # Filter files based on the provided subdirectories and extensions, excluding .cs.meta files
    filtered_files = [
        file for file in all_files
        if any(os.path.abspath(file).startswith(os.path.abspath(subdir) + os.sep) for subdir in subdirs)
        and file.endswith(tuple(file_extensions))
        and not file.endswith('.cs.meta')  # Exclude .cs.meta files
    ]

    total_lines = 0
    file_line_counts = {}  # To store line counts for each file

    for file in filtered_files:
        try:
            # Open the file in read mode, ignoring any encoding errors
            with open(file, 'r', errors='ignore') as f:
                line_count = sum(1 for _ in f)
                total_lines += line_count
                file_line_counts[file] = line_count  # Store line count for the file
        except FileNotFoundError:
            print(f"File not found (likely deleted): {file}")

    # Print the total number of lines found
    print(f"Total lines of code: {total_lines}\n")

    # Print each file with its line count
    print("Lines per file:")
    for file, line_count in file_line_counts.items():
        print(f"{file}: {line_count} lines")


if __name__ == "__main__":
    # Example usage: Count Python and C# files in 'src' and 'tests' subdirectories
    subdirs = ['Source/Configure/', 'Source/Experiment/', 'Source/Evaluate/', 'Source/Visualize/','Source/Utility/', 'Source/iVISPAR/Assets/Scripts']
    #subdirs = ['Source/']
    count_lines_of_code(file_extensions=['.py', '.cs'], subdirs=subdirs)
