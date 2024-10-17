# CSS and JS Filter Script

## Overview

This project is a script that processes a directory of `.html` and `.php` files to filter out unused CSS and JavaScript. It extracts only the necessary CSS/JS resources referenced in each file and creates filtered versions of the files with only the essential assets.

### Key Features

- Recursively scans directories for HTML and PHP files.
- Filters out unused CSS and JavaScript files.
- Supports inline and external CSS/JS.
- Handles PHP variables dynamically by prompting the user for values.
- Saves optimized files in the same directory, without unnecessary assets.

## How It Works

1. **Directory Traversal:** 
   The script will ask for a directory path to scan for HTML and PHP files.
   
2. **Processing Files:** 
   - For each file, it will extract the referenced CSS and JS files.
   - If PHP variables are used to generate file paths, you will be prompted to provide the values.
   
3. **Filtering:** 
   The script analyzes the file's content (HTML structure, classes, IDs, JS functions) to determine which CSS and JS files are actually used.
   
4. **Output:** 
   - Used CSS and JS files are copied to `css` and `js` directories inside the processed directory.
   - Inline CSS and JS are extracted to separate files.
   - The original files are saved with a `_filtered` suffix, containing only the necessary CSS and JS references.

## Installation

1. Clone this repository to your local machine.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
## Usage
```bash
   python3 app.py
or

```bash
   python app.py

