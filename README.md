# Second Brain: Terminal-Based Note-Taking App

`Second Brain` is a Python-based command-line application for managing Markdown notes in a structured directory (`~/second-brain`). It supports creating, editing, listing, deleting, searching, summarizing, formatting, and processing notes with a local Ollama server for AI-driven tasks. Notes are organized in categories (subdirectories) and stored as Markdown files with YAML metadata. The app integrates with Git for syncing notes to a private GitHub repository, enabling access across devices.

## Features

- **Create Notes**: Add new Markdown notes with YAML metadata (title, tags, date).
- **Edit Notes**: Open existing notes in Vim for editing.
- **List Notes**: Browse notes by category or view all, with options to edit, summarize, format, delete, or process.
- **Delete Notes**: Remove notes with confirmation.
- **Search Notes**: Find notes by keyword using `grep` with preview snippets.
- **Summarize Notes**: Generate or manually add summaries using Ollama or user input, stored in YAML metadata.
- **Format Notes**: Reformat notes into professional Markdown (Details, Action Items, Tags) via Ollama.
- **Process Notes**: Apply custom Ollama prompts to notes, review in Vim, and save changes.
- **Git Sync**: Automatically pull and push notes to a private GitHub repo for cross-device syncing (optional, enabled via environment variable).

## Prerequisites

- **Python 3.6+**: For running `main.py`.
- **Vim**: For editing notes (used by default).
- **Git**: For syncing notes to a GitHub repository.
- **grep**: For searching notes (typically pre-installed on Unix-like systems).
- **Ollama**: For AI-driven summarization and formatting (optional; requires a local Ollama server with `llama3.2:latest` model).
- **Python Libraries**: Install via:
  ```bash
  pip install requests pyyaml
  ```
- **GitHub Repository**: A private GitHub repo for note syncing (optional).

## Installation

1. **Clone or Download the Repository**:
   ```bash
   git clone git@github.com:yourusername/your-private-repo.git ~/second-brain
   cd ~/second-brain
   ```
   - Ensure the repo contains `main.py` and your notes (or create the directory structure).

2. **Set Up the Git Repository** (for syncing):
   ```bash
   cd ~/second-brain
   git init
   git remote add origin git@github.com:yourusername/your-private-repo.git
   git add .
   git commit -m "Initial commit"
   git push -u origin master
   ```
   - Use SSH for passwordless auth (`ssh-keygen`, add key to GitHub).
   - If your repo uses `main` instead of `master`, set `export BRAIN_GIT_BRANCH=main`.

3. **Install Dependencies**:
   ```bash
   pip install requests pyyaml
   ```
   - Ensure Vim and Git are installed (`sudo apt install vim git` on Debian/Ubuntu, or equivalent).

4. **Set Up Ollama** (optional, for summarization/formatting):
   - Install Ollama: [https://ollama.ai](https://ollama.ai)
   - Run the server with `llama3.2:latest`:
     ```bash
     ollama run llama3.2:latest
     ```

## Usage

Run the app:
```bash
cd ~/second-brain
python3 main.py
```

The app launches an interactive menu with the following commands:
1. **Add**: Create a new note (e.g., `customers/john-doe` creates `~/second-brain/customers/john-doe.md`).
2. **Edit**: Edit an existing note (select interactively from categories).
3. **List**: List notes by category or all, then select a note for actions (edit, summarize, delete, format, process).
4. **Delete**: Delete a note with confirmation.
5. **Search**: Search notes by keyword with preview snippets.
6. **Summarize**: Generate or add a summary to a note’s YAML metadata.
7. **Format**: Reformat a note’s content using Ollama.
8. **Process**: Apply a custom Ollama prompt to a note, edit in Vim, and save.
9. **Exit**: Quit the app.

### Example Workflow
1. Start the app:
   ```bash
   python3 main.py
   ```
2. Choose `1` to add a note, enter `projects/meeting-notes`.
3. Edit the note in Vim, save, and exit.
4. If Git sync is enabled, the note is committed and pushed to your GitHub repo.

### Git Sync
To enable syncing with your private GitHub repo:
```bash
export BRAIN_GIT_SYNC=true
```
- The app pulls changes before each command and pushes after modifications (`add`, `edit`, `delete`, `summarize`, `format`, `process`).
- The default branch is `master`. To use a different branch (e.g., `main`):
  ```bash
  export BRAIN_GIT_BRANCH=main
  ```
- A `.gitignore` file is created automatically to ignore Vim temp files (`*.swp`, `*.swo`).

## Directory Structure

```
~/second-brain/
├── .gitignore           # Ignores Vim temp files
├── main.py              # The note-taking script
├── notes/               # Default category for notes
│   └── example.md
├── customers/           # Example category
│   └── john-doe.md
```

Each note (e.g., `customers/john-doe.md`) is a Markdown file with YAML metadata:
```markdown
---
title: john-doe
tags: []
date: 2025-09-28
summary: Optional AI-generated or user-provided summary
---
Note content here...
```

## Troubleshooting

- **Git Errors**: Ensure Git is installed (`git --version`) and the repo is initialized (`git remote -v`). Check SSH auth (`ssh -T git@github.com`).
- **Vim Not Found**: Install Vim (`sudo apt install vim`).
- **Ollama Unavailable**: Ensure the Ollama server is running (`ollama run llama3.2:latest`).
- **No Notes Found**: Verify `~/second-brain` contains `.md` files.
- **Branch Issues**: If `master` fails, check your repo’s default branch (`git branch -r`) and set `BRAIN_GIT_BRANCH` accordingly.

## Contributing

Feel free to fork this repo and submit pull requests for improvements. Ideas:
- Add a `sync` command for manual Git pull/push.
- Improve conflict handling for Git merges.
- Support alternative editors (e.g., nano, VS Code).
- Add configuration file support instead of environment variables.

## License

MIT License. Use and modify freely, but no warranty is provided.