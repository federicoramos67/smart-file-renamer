# Smart File Renamer

A modern dark-mode Windows desktop app for safely previewing and bulk-renaming files with Python and Tkinter.

The project includes two independent launchers:

- `main.py`: English UI
- `main_es.py`: Spanish UI

Both versions share the same backend logic in `renamer.py` and `utils.py`.

## Features

- Select a folder
- Preview the current and future file names
- Bulk rename files
- Remove special characters
- Replace spaces with underscores
- Add numbering
- Add a date prefix
- Detect duplicate target filenames
- Block unsafe renames when duplicates or filename conflicts are found
- EXE-ready project structure

## Project Structure

```text
Smart File Renamer/
|-- main.py
|-- main_es.py
|-- renamer.py
|-- utils.py
|-- requirements.txt
`-- README.md
```

## Run From Source

Use Python 3.10 or newer on Windows.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Run the English version:

```powershell
python main.py
```

Run the Spanish version:

```powershell
python main_es.py
```

## Build a Windows EXE

The app is ready to package with PyInstaller.

English version:

```powershell
pip install -r requirements.txt
pyinstaller --name "Smart File Renamer" --windowed --onefile main.py
```

Spanish version:

```powershell
pip install -r requirements.txt
pyinstaller --name "Renombrador Inteligente de Archivos" --windowed --onefile main_es.py
```

The executables will be created in the `dist` folder.

## Rename Safety

The app always creates a preview before renaming. Renaming is blocked when:

- two or more files would receive the same name
- a new target filename already exists in the selected folder

During the actual rename, files are first moved through temporary names. This allows file swaps and case-only changes to complete more reliably on Windows.
