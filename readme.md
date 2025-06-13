# File Context - For llms

This Python script recursively scans the current directory (excluding hidden files/folders), allows you to select specific files or folders using a flexible CLI input syntax, and then writes the contents of the selected files to a `fileContext.txt` file.\\

---

## How It Works

1. **Scans** the directory tree.
2. **Prints** a numbered view of folders and files.
3. **Prompts** you for a selection input (like `1`, `2:1`, `all`, etc.).
4. **Creates** a `fileContext.txt` file containing the contents of selected files.

---

## Usage

windows: 
```bash
python your_script_name.py
```
mac
```bash
python3 your_script_name.py
```

Then follow the on-screen prompt to enter your selection.

---

## Selection Syntax

You can use the following formats to select files:

* `all`

  * Selects all files in root and subfolders.

* `all except (2, 3:1)`

  * Selects everything except:

    * All files inside folder `2`
    * File number `1` inside folder `3`

* `1, 2:1, 3:2,3`

  * Selects:

    * File `1` in the root directory
    * File `1` in folder `2`
    * Files `2` and `3` in folder `3`

---

## Example Output

```
Your file/folder structure:

1. main.py
2. README.md
1. src/
  1:1 app.py
  1:2 utils.py
2. data/
  2:1 data.csv
```

Then your `fileContext.txt` will include:

```
src/utils.py--------------------------------------------------------
# content of utils.py
------------------------------------------------------------------

data/data.csv-------------------------------------------------------
id,name
1,Aniket
------------------------------------------------------------------
```

---

## Requirements

* Python 3.x
* No external dependencies

---

## Notes

* Hidden files and folders (starting with `.`) are automatically ignored.
* Nested folders deeper than one level are currently not parsed in the selection logic.
