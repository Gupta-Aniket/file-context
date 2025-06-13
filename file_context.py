import os

def scan_dir(root):
    folder_counter = 1
    file_counter = 1

    def _scan(path, relative_path=''):
        nonlocal folder_counter, file_counter
        current_folder_num = folder_counter
        folder_counter += 1
        folder_data = {
            'name': os.path.basename(path) if path != '.' else '.',
            'files': {},
            'folders': {}
        }
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            print(f"Skipping folder (no permission): {path}")
            return folder_data

        # Skip hidden files/folders:
        entries = [e for e in entries if not e.startswith('.')]

        for entry in entries:
            full_path = os.path.join(path, entry)
            rel = os.path.join(relative_path, entry)
            if os.path.isdir(full_path):
                folder_data['folders'][folder_counter] = _scan(full_path, rel)
            else:
                folder_data['files'][file_counter] = rel
                file_counter += 1
        return folder_data


    tree = _scan(root)
    return tree

def print_tree(tree, indent='', folder_num=1):
    files = tree.get('files', {})
    folders = tree.get('folders', {})

    if indent == '':
        for fnum, fname in sorted(files.items()):
            print(f"{fnum}. {fname}")

    for fnum, folder in sorted(folders.items()):
        print(f"{folder_num}. {folder['name']}/")
        for fn, fname in sorted(folder['files'].items()):
            print(f"  {folder_num}:{fn} {fname}")
        for sfnum, sfolder in sorted(folder['folders'].items()):
            print(f"  {folder_num}.{sfnum}. {sfolder['name']}/")

def flatten_tree(tree):
    root_files = tree.get('files', {})
    folders = {}
    for fnum, folder in tree.get('folders', {}).items():
        folders[fnum] = {
            'name': folder['name'],
            'files': folder.get('files', {}),
            'folders': folder.get('folders', {})
        }
    return {'root_files': root_files, 'folders': folders}

def parse_selection(selection, data):
    root_files = data['root_files']
    folders = data['folders']

    def expand_all():
        selected = set()
        for fpath in root_files.values():
            selected.add(fpath)
        for fnum, folder in folders.items():
            for fpath in folder['files'].values():
                selected.add(fpath)
            # For now, ignoring nested folders deeper than 1 level
        return selected

    def parse_part(part):
        part = part.strip()
        selected = set()
        # Single folder like '2'
        if ':' not in part:
            # If it is a folder number
            if part.isdigit():
                fnum = int(part)
                if fnum in folders:
                    for fpath in folders[fnum]['files'].values():
                        selected.add(fpath)
                elif fnum in root_files:
                    selected.add(root_files[fnum])
            else:
                # Possibly root file name or invalid
                pass
        else:
            # folder:file e.g. 2:1,2:3
            folder_str, files_str = part.split(':', 1)
            if folder_str.isdigit():
                fnum = int(folder_str)
                if fnum in folders:
                    file_nums = [int(x.strip()) for x in files_str.split(',')]
                    for fn in file_nums:
                        if fn in folders[fnum]['files']:
                            selected.add(folders[fnum]['files'][fn])
        return selected

    selection = selection.strip()
    selected_files = set()
    exclude_files = set()

    if selection.lower() == 'all':
        selected_files = expand_all()
    elif selection.lower().startswith('all except'):
        # parse excludes inside parentheses
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
        # explicit list like 1,2:1,3
        parts = selection.split(',')
        for part in parts:
            selected_files |= parse_part(part)

    return selected_files

def write_file_context(selected_files):
    with open('fileContext.txt', 'w', encoding='utf-8') as out:
        for filepath in sorted(selected_files):
            if not os.path.isfile(filepath):
                continue
            header = filepath + '-' * (60 - len(filepath))
            out.write(header + '\n')
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                out.write(content + '\n')
            except Exception as e:
                out.write(f"// Could not read file: {e}\n")
            out.write('-' * 66 + '\n\n')

def main():
    tree = scan_dir('.')
    print("\nYour file/folder structure:\n")
    print_tree(tree)
    data = flatten_tree(tree)
    print("\nEnter your selection (e.g. all, 1, 2:1, all except (3,4:2)):")
    selection = input("> ").strip()
    selected_files = parse_selection(selection, data)
    if not selected_files:
        print("No files selected.")
        return
    write_file_context(selected_files)
    print(f"\nfileContext.txt created with {len(selected_files)} files!")

if __name__ == "__main__":
    main()
