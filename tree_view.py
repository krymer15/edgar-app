# tree_view.py

import os

def print_tree(start_path=".", output_file=None):
    tree_lines = []

    for root, dirs, files in os.walk(start_path, topdown=True):
        # Ignore hidden folders
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        # Sort dirs and files for clean output
        dirs.sort()
        files.sort()

        level = root.count(os.sep)
        indent = "│   " * (level - 1) + ("├── " if level > 0 else "")
        tree_lines.append(f"{indent}{os.path.basename(root)}/")

        subindent = "│   " * level
        for idx, f in enumerate(files):
            if not f.startswith("."):
                connector = "├── " if idx < len(files) - 1 else "└── "
                tree_lines.append(f"{subindent}{connector}{f}")

    tree_output = "\n".join(tree_lines)

    # Print to console
    print(tree_output)

    # Optionally write to a .txt file
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(tree_output)

if __name__ == "__main__":
    # Output to console and also write to a tree.txt file
    print_tree(".", output_file="tree.txt")
