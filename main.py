import argparse
from pathlib import Path
import subprocess
from datetime import date

HOME = Path.home() / 'second-brain'

def parse_name(name: str) -> tuple[Path, str, Path]:
    """
    Parse the name to determine category path, basename, and file path.
    """
    parts = name.split('/')
    if len(parts) == 1:
        category_path = Path('notes')
        basename = parts[0]
    else:
        category_path = Path('/'.join(parts[:-1]))
        basename = parts[-1]
    dir_path = HOME / category_path
    file_path = dir_path / f"{basename}.md"
    return dir_path, basename, file_path

def add_note(name: str) -> None:
    """
    Create a new Markdown note with YAML metadata and open in VIM.
    """
    dir_path, basename, file_path = parse_name(name)
    if file_path.exists():
        print(f"Note '{name}' already exists.")
        return
    dir_path.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    content = f"""---
title: {basename}
tags: []
date: {today}
---

"""
    try:
        file_path.write_text(content)
    except OSError as e:
        print(f"Error creating note: {e}")
        return
    try:
        subprocess.run(['vim', str(file_path)], check=True)
        print(f"Note '{name}' added successfully.")
    except FileNotFoundError:
        print("VIM not found. Please install VIM.")
    except subprocess.CalledProcessError:
        print("VIM exited with an error.")
    except Exception as e:
        print(f"Error opening VIM: {e}")

def edit_note(name: str) -> None:
    """
    Open an existing note in VIM for editing.
    """
    _, _, file_path = parse_name(name)
    if not file_path.exists():
        print(f"Note '{name}' not found.")
        return
    try:
        subprocess.run(['vim', str(file_path)], check=True)
        print(f"Note '{name}' edited successfully.")
    except FileNotFoundError:
        print("VIM not found. Please install VIM.")
    except subprocess.CalledProcessError:
        print("VIM exited with an error.")
    except Exception as e:
        print(f"Error opening VIM: {e}")

def list_notes(category: str | None = None) -> None:
    """
    List all notes or notes in a specific category.
    """
    if category:
        dir_path = HOME / category
        if not dir_path.is_dir():
            print(f"Category '{category}' not found.")
            return
        notes = [f.stem for f in dir_path.glob('*.md')]
        if not notes:
            print(f"No notes in category '{category}'.")
            return
        for note in sorted(notes):
            print(note)
    else:
        notes = []
        for file in HOME.rglob('*.md'):
            rel = file.relative_to(HOME)
            note_name = str(rel.with_suffix(''))
            notes.append(note_name)
        if not notes:
            print("No notes found.")
            return
        for note in sorted(notes):
            print(note)

def delete_note(name: str) -> None:
    """
    Delete a note after user confirmation.
    """
    _, _, file_path = parse_name(name)
    if not file_path.exists():
        print(f"Note '{name}' not found.")
        return
    confirm = input(f"Confirm deletion of '{name}'? (y/n): ")
    if confirm.lower() == 'y':
        try:
            file_path.unlink()
            print(f"Note '{name}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting note: {e}")
    else:
        print("Deletion cancelled.")

def main() -> None:
    """
    Main entry point for the brain CLI app.
    """
    parser = argparse.ArgumentParser(description="Brain: A terminal-based note-taking app.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    add_parser = subparsers.add_parser('add', help='Add a new note')
    add_parser.add_argument('name', help='Name of the note (e.g., customers/john-doe)')

    edit_parser = subparsers.add_parser('edit', help='Edit an existing note')
    edit_parser.add_argument('name', help='Name of the note (e.g., customers/john-doe)')

    list_parser = subparsers.add_parser('list', help='List notes')
    list_parser.add_argument('category', nargs='?', help='Optional category to list (e.g., customers)')

    delete_parser = subparsers.add_parser('delete', help='Delete a note')
    delete_parser.add_argument('name', help='Name of the note (e.g., customers/john-doe)')

    args = parser.parse_args()

    if args.command == 'add':
        add_note(args.name)
    elif args.command == 'edit':
        edit_note(args.name)
    elif args.command == 'list':
        list_notes(args.category)
    elif args.command == 'delete':
        delete_note(args.name)

if __name__ == '__main__':
    main()
