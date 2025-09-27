import argparse
from pathlib import Path
import subprocess
from datetime import date
import requests
import yaml
import re
import os
import time

HOME = Path.home() / 'second-brain'

def clear_screen() -> None:
    """
    Clear the terminal screen.
    """
    os.system('clear' if os.name != 'nt' else 'cls')

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

def select_category_interactively() -> str | None:
    """
    Display a list of all categories and let the user select one interactively.
    Returns the category path (e.g., 'customers') or None for all notes or if cancelled.
    """
    categories = set()
    for file in HOME.rglob('*.md'):
        rel_path = file.relative_to(HOME).parent
        categories.add(str(rel_path))
    if not categories:
        print("No categories found.")
        time.sleep(1)
        return None
    categories = sorted(categories)
    print("\n=== Select a Category ===")
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category}")
    print(f"  {len(categories) + 1}. All notes")
    try:
        choice = input("\nEnter the number of the category (or 'q' to cancel): ").strip()
        if choice.lower() == 'q':
            print("Category selection cancelled.")
            time.sleep(1)
            return None
        choice_idx = int(choice) - 1
        if choice_idx == len(categories):
            return None  # All notes
        if 0 <= choice_idx < len(categories):
            return categories[choice_idx]
        else:
            print("ERROR: Invalid selection. Please choose a valid number.")
            time.sleep(1)
            return None
    except ValueError:
        print("ERROR: Invalid input. Please enter a number or 'q'.")
        time.sleep(1)
        return None

def select_note_in_category(category: str | None) -> str | None:
    """
    Display a list of notes in the specified category (or all notes if None) and let the user select one.
    Returns the relative note path (e.g., 'notes/example' or 'customers/john-doe') or None if cancelled.
    """
    notes = []
    if category:
        dir_path = HOME / category
        if not dir_path.is_dir():
            print(f"ERROR: Category '{category}' not found.")
            time.sleep(1)
            return None
        notes = [str(file.relative_to(HOME).with_suffix('')) for file in dir_path.glob('*.md')]
    else:
        for file in HOME.rglob('*.md'):
            rel = file.relative_to(HOME)
            note_name = str(rel.with_suffix(''))
            notes.append(note_name)
    if not notes:
        print(f"ERROR: No notes found{' in category ' + category if category else ''}.")
        time.sleep(1)
        return None
    print(f"\n=== Select a Note{' in ' + category if category else ''} ===")
    for i, note in enumerate(sorted(notes), 1):
        print(f"  {i}. {note}")
    try:
        choice = input("\nEnter the number of the note (or 'q' to cancel): ").strip()
        if choice.lower() == 'q':
            print("Note selection cancelled.")
            time.sleep(1)
            return None
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(notes):
            return sorted(notes)[choice_idx]
        else:
            print("ERROR: Invalid selection. Please choose a valid number.")
            time.sleep(1)
            return None
    except ValueError:
        print("ERROR: Invalid input. Please enter a number or 'q'.")
        time.sleep(1)
        return None

def select_note_interactively() -> str | None:
    """
    Select a category interactively, then select a note within that category.
    Returns the relative note path (e.g., 'notes/example' or 'customers/john-doe') or None if cancelled.
    """
    category = select_category_interactively()
    if category is None and category != '':
        return None  # Cancelled or all notes selected
    return select_note_in_category(category)

def add_note(name: str) -> None:
    """
    Create a new Markdown note with YAML metadata and open in VIM.
    """
    dir_path, basename, file_path = parse_name(name)
    if file_path.exists():
        print(f"ERROR: Note '{name}' already exists.")
        time.sleep(1)
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
        print(f"ERROR: Error creating note: {e}")
        time.sleep(1)
        return
    try:
        subprocess.run(['vim', str(file_path)], check=True)
        print(f"Note '{name}' added successfully.")
        print("Returning to menu...")
        time.sleep(1)
    except FileNotFoundError:
        print("ERROR: VIM not found. Please install VIM.")
        time.sleep(1)
    except subprocess.CalledProcessError:
        print("ERROR: VIM exited with an error.")
        time.sleep(1)
    except Exception as e:
        print(f"ERROR: Error opening VIM: {e}")
        time.sleep(1)

def edit_note(name: str | None) -> None:
    """
    Open an existing note in VIM for editing. If no name is provided, prompt for category and note selection.
    """
    if not name:
        name = select_note_interactively()
        if not name:
            return
    _, _, file_path = parse_name(name)
    if not file_path.exists():
        print(f"ERROR: Note '{name}' not found.")
        time.sleep(1)
        return
    try:
        subprocess.run(['vim', str(file_path)], check=True)
        print(f"Note '{name}' edited successfully.")
        print("Returning to menu...")
        time.sleep(1)
    except FileNotFoundError:
        print("ERROR: VIM not found. Please install VIM.")
        time.sleep(1)
    except subprocess.CalledProcessError:
        print("ERROR: VIM exited with an error.")
        time.sleep(1)
    except Exception as e:
        print(f"ERROR: Error opening VIM: {e}")
        time.sleep(1)

def list_notes(category: str | None = None) -> None:
    """
    List notes in a specific category or all notes, then allow the user to select a note and choose an action.
    If category is None, prompt for interactive category selection.
    """
    if category is None:
        category = select_category_interactively()
        if category is None and category != '':
            return  # Cancelled or all notes selected
    name = select_note_in_category(category)
    if not name:
        return
    print(f"\n=== Selected Note: {name} ===")
    actions = [
        ('edit', 'Edit the note'),
        ('summarize', 'Summarize the note'),
        ('delete', 'Delete the note'),
        ('format', 'Format the note'),
        ('cancel', 'Cancel')
    ]
    print("\nAvailable actions:")
    for i, (action, desc) in enumerate(actions, 1):
        print(f"  {i}. {action}: {desc}")
    try:
        choice = input("\nEnter the number of the action (or 'q' to cancel): ").strip()
        if choice.lower() == 'q':
            print("Action cancelled.")
            time.sleep(1)
            return
        choice_idx = int(choice) - 1
        if not 0 <= choice_idx < len(actions):
            print("ERROR: Invalid selection. Please choose a valid number.")
            time.sleep(1)
            return
        action = actions[choice_idx][0]
        if action == 'cancel':
            print("Action cancelled.")
            time.sleep(1)
            return
        elif action == 'edit':
            edit_note(name)
        elif action == 'summarize':
            summarize_note(name)
        elif action == 'delete':
            delete_note(name)
        elif action == 'format':
            format_note(name)
    except ValueError:
        print("ERROR: Invalid input. Please enter a number or 'q'.")
        time.sleep(1)
    except Exception as e:
        print(f"ERROR: {e}")
        time.sleep(1)

def delete_note(name: str | None) -> None:
    """
    Delete a note after user confirmation. If no name is provided, prompt for category and note selection.
    """
    if not name:
        name = select_note_interactively()
        if not name:
            return
    _, _, file_path = parse_name(name)
    if not file_path.exists():
        print(f"ERROR: Note '{name}' not found.")
        time.sleep(1)
        return
    confirm = input(f"Confirm deletion of '{name}'? (y/n): ")
    if confirm.lower() == 'y':
        try:
            file_path.unlink()
            print(f"Note '{name}' deleted successfully.")
            print("Returning to menu...")
            time.sleep(1)
        except OSError as e:
            print(f"ERROR: Error deleting note: {e}")
            time.sleep(1)
    else:
        print("Deletion cancelled.")
        time.sleep(1)

def search_notes(keyword: str) -> None:
    """
    Search for a keyword across all notes using grep and display matching notes with previews.
    """
    try:
        result = subprocess.run(
            ['grep', '-r', '-i', '--include=*.md', keyword, str(HOME)],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode not in (0, 1):
            print("ERROR: Error running grep command.")
            time.sleep(1)
            return
        output = result.stdout.strip()
        if not output:
            print(f"No matches found for keyword '{keyword}'.")
            time.sleep(1)
            return
        matches = {}
        for line in output.splitlines():
            if ':' in line:
                file_path, content = line.split(':', 1)
                rel_path = Path(file_path).relative_to(HOME).with_suffix('')
                preview = content[:50] + ('...' if len(content) > 50 else '')
                if str(rel_path) not in matches:
                    matches[str(rel_path)] = []
                matches[str(rel_path)].append(preview)
        if matches:
            print(f"\n=== Search Results for '{keyword}' ===")
            for note, previews in sorted(matches.items()):
                print(f"- {note}:")
                for preview in previews:
                    print(f"  {preview}")
        else:
            print(f"No matches found for keyword '{keyword}'.")
        print("\nPress Enter to continue...")
        input()
    except FileNotFoundError:
        print("ERROR: grep not found. Please install grep.")
        time.sleep(1)
    except Exception as e:
        print(f"ERROR: Error searching notes: {e}")
        time.sleep(1)

def extract_yaml_and_content(file_path: Path) -> tuple[dict, str]:
    """
    Extract YAML metadata and content from a Markdown file.
    """
    try:
        content = file_path.read_text()
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if yaml_match:
            yaml_data = yaml.safe_load(yaml_match.group(1)) or {}
            body = yaml_match.group(2).strip()
        else:
            yaml_data = {}
            body = content.strip()
        return yaml_data, body
    except OSError as e:
        print(f"ERROR: Error reading note: {e}")
        time.sleep(1)
        return {}, ""

def call_ollama(prompt: str, content: str) -> str | None:
    """
    Call the Ollama server with the given prompt and content using llama3.2:latest.
    """
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'llama3.2:latest', 'prompt': f"{prompt}\n\n{content}"},
            timeout=30
        )
        response.raise_for_status()
        result = ''
        for line in response.text.splitlines():
            try:
                json_data = yaml.safe_load(line)
                if json_data.get('done') and not json_data.get('response'):
                    continue
                result += json_data.get('response', '')
            except yaml.YAMLError:
                continue
        return result.strip()
    except (requests.RequestException, yaml.YAMLError) as e:
        print(f"ERROR: Ollama server unavailable: {e}")
        time.sleep(1)
        return None

def summarize_note(name: str | None) -> None:
    """
    Summarize a note using the Ollama server and append summary to YAML metadata.
    If no name is provided, prompt for category and note selection.
    Prompt for confirmation before saving the summary.
    """
    if not name:
        name = select_note_interactively()
        if not name:
            return
    _, _, file_path = parse_name(name)
    if not file_path.exists():
        print(f"ERROR: Note '{name}' not found.")
        time.sleep(1)
        return
    yaml_data, content = extract_yaml_and_content(file_path)
    if not content:
        print(f"ERROR: No content found in note '{name}' to summarize.")
        time.sleep(1)
        return

    if 'summary' in yaml_data:
        print(f"\n=== Existing Summary for '{name}' ===")
        print(yaml_data['summary'])
        confirm = input("\nThis note already has a summary. Do you want to re-summarize it? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Summarization cancelled.")
            time.sleep(1)
            return
        prompt = "Summarize this note concisely, focusing on key points."
        summary = call_ollama(prompt, content)
        if summary is None:
            print("Ollama server unavailable: Summarization skipped.")
            time.sleep(1)
            return
        print(f"\n=== Proposed New Summary for '{name}' ===")
        print(summary)
        confirm_save = input("\nDo you want to save this summary? (y/n): ").strip().lower()
        if confirm_save != 'y':
            print("Summary not saved. Returning to menu...")
            time.sleep(1)
            return
    else:
        print(f"\n=== Content of '{name}' ===")
        print("-" * 50)
        print(content)
        print("-" * 50)
        print("\nNo summary found. Choose an option:")
        print("  1. Add summary")
        print("  2. Generate new summary")
        print("  3. Exit")
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice == '3':
            print("Summarization cancelled.")
            time.sleep(1)
            return
        elif choice == '1':
            summary = input("Enter the summary: ").strip()
            if not summary:
                print("ERROR: Summary cannot be empty.")
                time.sleep(1)
                return
            print(f"\n=== Proposed Summary for '{name}' ===")
            print(summary)
            confirm_save = input("\nDo you want to save this summary? (y/n): ").strip().lower()
            if confirm_save != 'y':
                print("Summary not saved. Returning to menu...")
                time.sleep(1)
                return
        elif choice == '2':
            prompt = "Summarize this note concisely, focusing on key points."
            summary = call_ollama(prompt, content)
            if summary is None:
                print("Ollama server unavailable: Summarization skipped.")
                time.sleep(1)
                return
            print(f"\n=== Proposed New Summary for '{name}' ===")
            print(summary)
            confirm_save = input("\nDo you want to save this summary? (y/n): ").strip().lower()
            if confirm_save != 'y':
                print("Summary not saved. Returning to menu...")
                time.sleep(1)
                return
        else:
            print("ERROR: Invalid choice. Summarization cancelled.")
            time.sleep(1)
            return

    yaml_data['summary'] = summary
    try:
        new_content = f"""---
{yaml.safe_dump(yaml_data, sort_keys=False)}
---
{content}
"""
        file_path.write_text(new_content)
        print(f"Note '{name}' summarized successfully.")
        print("Returning to menu...")
        time.sleep(1)
    except OSError as e:
        print(f"ERROR: Error updating note with summary: {e}")
        time.sleep(1)

def format_note(name: str | None) -> None:
    """
    Format a note using the Ollama server, preserving YAML metadata.
    If no name is provided, prompt for category and note selection.
    """
    if not name:
        name = select_note_interactively()
        if not name:
            return
    _, _, file_path = parse_name(name)
    if not file_path.exists():
        print(f"ERROR: Note '{name}' not found.")
        time.sleep(1)
        return
    yaml_data, content = extract_yaml_and_content(file_path)
    if not content:
        print(f"ERROR: No content found in note '{name}' to format.")
        time.sleep(1)
        return
    prompt = "Format this note as professional Markdown with sections: Details, Action Items, Tags."
    formatted_content = call_ollama(prompt, content)
    if formatted_content is None:
        print("Ollama server unavailable: Formatting skipped.")
        time.sleep(1)
        return
    try:
        new_content = f"""---
{yaml.safe_dump(yaml_data, sort_keys=False)}
---
{formatted_content}
"""
        file_path.write_text(new_content)
        print(f"Note '{name}' formatted successfully.")
        print("Returning to menu...")
        time.sleep(1)
    except OSError as e:
        print(f"ERROR: Error updating note with formatted content: {e}")
        time.sleep(1)

def main_interactive() -> None:
    """
    Main entry point for the interactive brain CLI app.
    Displays a menu of commands and handles user input.
    """
    commands = [
        ('add', 'Add a new note'),
        ('edit', 'Edit an existing note'),
        ('list', 'List notes and select an action'),
        ('delete', 'Delete a note'),
        ('search', 'Search notes by keyword'),
        ('summarize', 'Summarize a note'),
        ('format', 'Format a note'),
        ('exit', 'Exit the program')
    ]
    while True:
        clear_screen()
        print("\n=== Brain: Terminal-based Note-taking App ===")
        print("Available commands:")
        for i, (cmd, desc) in enumerate(commands, 1):
            print(f"  {i}. {cmd}: {desc}")
        try:
            choice = input("\nEnter the number of the command (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                print("Exiting Brain. Goodbye!")
                time.sleep(1)
                break
            choice_idx = int(choice) - 1
            if not 0 <= choice_idx < len(commands):
                print("ERROR: Invalid selection. Please choose a valid number.")
                time.sleep(1)
                continue
            command = commands[choice_idx][0]
            if command == 'exit':
                print("Exiting Brain. Goodbye!")
                time.sleep(1)
                break
            elif command == 'add':
                clear_screen()
                print("\n=== Add a New Note ===")
                name = input("Enter note name (e.g., customers/john-doe): ").strip()
                if not name:
                    print("ERROR: Note name cannot be empty.")
                    time.sleep(1)
                    continue
                add_note(name)
            elif command == 'edit':
                clear_screen()
                print("\n=== Edit a Note ===")
                edit_note(None)
            elif command == 'list':
                clear_screen()
                print("\n=== List Notes ===")
                list_notes(None)
            elif command == 'delete':
                clear_screen()
                print("\n=== Delete a Note ===")
                delete_note(None)
            elif command == 'search':
                clear_screen()
                print("\n=== Search Notes ===")
                keyword = input("Enter keyword to search: ").strip()
                if not keyword:
                    print("ERROR: Keyword cannot be empty.")
                    time.sleep(1)
                    continue
                search_notes(keyword)
            elif command == 'summarize':
                clear_screen()
                print("\n=== Summarize a Note ===")
                summarize_note(None)
            elif command == 'format':
                clear_screen()
                print("\n=== Format a Note ===")
                format_note(None)
        except ValueError:
            print("ERROR: Invalid input. Please enter a number or 'q'.")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nERROR: Operation cancelled. Returning to menu...")
            time.sleep(1)
        except Exception as e:
            print(f"ERROR: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main_interactive()
