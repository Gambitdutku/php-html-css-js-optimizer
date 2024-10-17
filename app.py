import os
import re
import shutil
from bs4 import BeautifulSoup
from suricata.update.configs import directory

# A dictionary to store user-provided values for PHP variables
php_variable_cache = {}

def process_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.html') or file.endswith('.php'):
                file_path = os.path.join(root, file)
                process_file(file_path)

def resolve_php_variables(path):
    # Find all PHP variables in the path
    php_variables = re.findall(r'\<\?php\s+echo\s+\$(\w+);\s*\?>', path)
    for var in php_variables:
        # Check if we already have a value for this variable
        if var not in php_variable_cache:
            # Ask the user for input and store it in the cache
            value = input(f"Please provide a value for PHP variable '{var}': ")
            php_variable_cache[var] = value
        # Replace the PHP variable in the path with the cached value
        path = path.replace(f"<?php echo ${var};?>", php_variable_cache[var])
    return path

def process_file(file_path):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Extract CSS and JS files referenced in the HTML/PHP
    css_files = [link['href'] for link in soup.find_all('link', rel='stylesheet') if 'href' in link.attrs]
    js_files = [script['src'] for script in soup.find_all('script') if 'src' in script.attrs]

    # Set up directories for filtered CSS and JS files
    base_path = os.path.dirname(file_path)
    css_dir = os.path.join(base_path, 'css')
    js_dir = os.path.join(base_path, 'js')
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)

    used_css_files = []
    used_js_files = []

    # Extract class and ID names from the HTML content
    classes_ids = set(re.findall(r'class=["\'](.*?)["\']|id=["\'](.*?)["\']', content))
    classes_ids = {cls_id for pair in classes_ids for cls_id in pair if cls_id}

    # Extract JS function names from the HTML content
    js_functions = set(re.findall(r'function\s+(\w+)\s*\(', content))

    # Check each CSS file for usage
    for css_file in css_files:
        css_file = resolve_php_variables(css_file)
        try:
            css_file_path = os.path.join(base_path, css_file)
            with open(css_file_path, 'r', encoding='utf-8') as css:
                css_content = css.read()
                if any(cls in css_content for cls in classes_ids):
                    used_css_files.append(css_file_path)
                    shutil.copy(css_file_path, css_dir)
        except FileNotFoundError:
            print(f"CSS file not found: {css_file}")

    # Check each JS file for usage
    for js_file in js_files:
        js_file = resolve_php_variables(js_file)
        try:
            js_file_path = os.path.join(base_path, js_file)
            if js_file_path not in used_js_files:
                with open(js_file_path, 'r', encoding='utf-8') as js:
                    js_content = js.read()
                    if any(func in js_content for func in js_functions):
                        used_js_files.append(js_file_path)
                        shutil.copy(js_file_path, js_dir)
        except FileNotFoundError:
            print(f"JS file not found: {js_file}")
        except shutil.SameFileError:
            print(f"JS file already copied: {js_file_path}")

    # Extract inline CSS and JS
    inline_css = soup.find_all('style')
    inline_js = soup.find_all('script', {'src': False})

    # Write inline CSS to a new file
    if inline_css:
        inline_css_file = os.path.join(css_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_inline.css")
        with open(inline_css_file, 'w', encoding='utf-8') as css_out:
            for style_tag in inline_css:
                css_out.write(style_tag.text)
                style_tag.decompose()
        print(f"Extracted inline CSS to {inline_css_file}")

    # Write inline JS to a new file
    if inline_js:
        inline_js_file = os.path.join(js_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_inline.js")
        with open(inline_js_file, 'w', encoding='utf-8') as js_out:
            for script_tag in inline_js:
                js_out.write(script_tag.text)
                script_tag.decompose()
        print(f"Extracted inline JS to {inline_js_file}")

    # Update HTML/PHP file with only necessary CSS and JS
    for link in soup.find_all('link', rel='stylesheet'):
        if link['href'] not in used_css_files:
            link.decompose()

    for script in soup.find_all('script', {'src': True}):
        if script['src'] not in used_js_files:
            script.decompose()

    # Add filtered CSS and JS files back into the HTML
    for css_file in used_css_files:
        relative_css_path = os.path.relpath(css_file, base_path)
        new_css_tag = soup.new_tag('link', rel='stylesheet', href=relative_css_path)
        soup.head.append(new_css_tag)

    for js_file in used_js_files:
        relative_js_path = os.path.relpath(js_file, base_path)
        new_js_tag = soup.new_tag('script', src=relative_js_path)
        soup.body.append(new_js_tag)

    # Save the modified HTML/PHP file
    new_file_name = f"{os.path.splitext(file_path)[0]}_filtered{os.path.splitext(file_path)[1]}"
    with open(new_file_name, 'w', encoding='utf-8') as new_file:
        new_file.write(str(soup))

    print(f"Filtered file saved as: {new_file_name}")

directory = input("Paste path to use: ")
process_directory(directory)
