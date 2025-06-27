import os
import string
import sys
import time

EXTENSION_LANG_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'jsx',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.dart': 'dart',
    '.json': 'json',
    '.html': 'html',
    '.css': 'css',
    '.sh': 'bash',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.md': 'markdown',
    '.txt': '',
}


def get_language_from_extension(filename):
    ext = os.path.splitext(filename)[1].lower()
    return EXTENSION_LANG_MAP.get(ext, '')


def scan_directory(root='.'):
    folder_labels = iter(string.ascii_uppercase)
    file_counter = 1
    files = {}
    folders = {}
    folder_mapping = {}

    entries = sorted(os.listdir(root))
    EXCLUDE_FILES = {'fileContext.md', 'file_context.py'}

    entries = [e for e in entries if not e.startswith('.') and e not in EXCLUDE_FILES]

    dirs = []

    for entry in entries:
        full_path = os.path.join(root, entry)
        if os.path.isdir(full_path):
            dirs.append(entry)
        else:
            files[file_counter] = full_path
            file_counter += 1

    for folder in dirs:
        folder_code = next(folder_labels)
        folder_mapping[folder_code] = folder
        folder_path = os.path.join(root, folder)
        folder_files = {}
        sub_entries = sorted(os.listdir(folder_path))
        sub_entries = [e for e in sub_entries if not e.startswith('.') and e not in EXCLUDE_FILES]

        sub_counter = 1
        for sub_entry in sub_entries:
            sub_full_path = os.path.join(folder_path, sub_entry)
            if os.path.isfile(sub_full_path):
                folder_files[sub_counter] = sub_full_path
                sub_counter += 1
        folders[folder_code] = folder_files

    return {
        'files': files,
        'folders': folders,
        'folder_mapping': folder_mapping
    }


def display_structure(data):
    files = data['files']
    folders = data['folders']
    folder_mapping = data['folder_mapping']

    print("\nYour file/folder structure:\n")
    for fnum, path in sorted(files.items()):
        print(f"{fnum}. {path}")

    for fcode in sorted(folders.keys()):
        print(f"{fcode}. {folder_mapping[fcode]}/")
        subfiles = folders[fcode]
        for snum, subpath in sorted(subfiles.items()):
            print(f"  {fcode}:{snum} {subpath}")


def parse_selection(selection, data):
    files = data['files']
    folders = data['folders']

    def expand_all():
        selected = set(files.values())
        for subfiles in folders.values():
            selected.update(subfiles.values())
        return selected

    def parse_part(part):
        part = part.strip()
        selected = set()
        if ':' not in part:
            if part.isdigit():
                if int(part) in files:
                    selected.add(files[int(part)])
            elif part.isalpha():
                if part in folders:
                    selected.update(folders[part].values())
        else:
            folder_code, files_str = part.split(':', 1)
            folder_code = folder_code.strip().upper()
            if folder_code in folders:
                file_nums = [int(x.strip()) for x in files_str.split(',')]
                for fn in file_nums:
                    if fn in folders[folder_code]:
                        selected.add(folders[folder_code][fn])
        return selected

    selection = selection.strip()
    selected_files = set()
    exclude_files = set()

    if selection.lower() == 'all':
        selected_files = expand_all()
    elif selection.lower().startswith('all except'):
        import re
        m = re.search(r'all except\s*\((.*)\)', selection, re.I)
        if not m:
            print("Invalid syntax for 'all except'.")
            return set()
        excludes = m.group(1).split(',')
        selected_files = expand_all()
        for ex in excludes:
            exclude_files |= parse_part(ex)
        selected_files -= exclude_files
    else:
        parts = selection.split(',')
        for part in parts:
            selected_files |= parse_part(part)

    return selected_files





def build_markdown_tree(selected_files):
    tree = {}
    for path in selected_files:
        parts = path.split(os.sep)
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part + '/', {})
        current.setdefault(parts[-1], None)
    return tree


def render_tree(tree, prefix=''):
    lines = []
    entries = sorted(tree.items())
    for i, (name, subtree) in enumerate(entries):
        connector = '└── ' if i == len(entries) - 1 else '├── '
        lines.append(prefix + connector + name)
        if isinstance(subtree, dict):
            extension = '    ' if i == len(entries) - 1 else '│   '
            lines.extend(render_tree(subtree, prefix + extension))
    return lines


def write_file_context(selected_files):

    print("\n----------------------------------------------------------------------------------------------")
    print("\nReading files...")

    tree_data = build_markdown_tree(selected_files)
    tree_lines = render_tree(tree_data)

    with open('fileContext.md', 'w', encoding='utf-8') as out:
        out.write("## 📂 Project Structure\n\n")
        out.write("```\n")
        for line in tree_lines:
            out.write(line + '\n')
        out.write("```\n\n")

        for filepath in sorted(selected_files):
            if not os.path.isfile(filepath):
                continue
            rel_path = os.path.relpath(filepath)
            print(f"{rel_path}")
            filename = os.path.basename(filepath)
            lang = get_language_from_extension(filename)

            out.write(f"### {filename}\n")
            out.write(f"```{lang}\n")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                out.write(content + '\n')
            except UnicodeDecodeError:
                out.write("// Binary file - skipped\n")
            except Exception as e:
                out.write(f"// Could not read file: {e}\n")
            out.write("```\n\n")

    print(f"\n✅ fileContext.md created with {len(selected_files)} files!")
    output_path = os.path.abspath('fileContext.md')
    print(f"\n📁 Markdown output saved to:\n{output_path}")
    print("\n----------------------------------------------------------------------------------------------")




def main():
    data = scan_directory()
    display_structure(data)

    print("\nEnter your selection (e.g. all, 1, A:1, all except (B,4)):")
    selection = input("> ").strip()
    selected_files = parse_selection(selection, data)
    if not selected_files:
        print("No files selected.")
        return
    write_file_context(selected_files)

    print("\n💡 Tip: Add a short comment at the top of each file :")
    print("         // This file manages login logic for users") 
    print("Helps both humans and LLM's understand your code faster 😊 \n")


if __name__ == "__main__":
    main()
