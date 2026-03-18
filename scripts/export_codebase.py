import os

def export_codebase():
    # Configuration
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(project_root, "megh_full_codebase.txt")
    
    # Files/Dirs to ignore
    ignore_dirs = {'.git', '__pycache__', '.venv', '.gemini', 'node_modules', 'saved'}
    ignore_exts = {'.db', '.keras', '.pkl', '.png', '.webp', '.jpg', '.jpeg', '.gif', '.pyc'}
    
    # Readable extensions
    readable_exts = {'.py', '.md', '.txt', '.csv', '.json', '.yaml', '.yml', '.env', '.example'}

    count = 0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("====================================================\n")
        outfile.write("MEGH FULL CODEBASE EXPORT\n")
        outfile.write(f"Generated on: {os.path.basename(output_file)}\n")
        outfile.write("====================================================\n\n")

        for root, dirs, files in os.walk(project_root):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in readable_exts or file in ('.env', '.gitignore'):
                    if file_ext in ignore_exts:
                        continue
                        
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_root)
                    
                    print(f"Adding: {rel_path}")
                    
                    outfile.write(f"\n--- FILE: {rel_path} ---\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]\n")
                    
                    outfile.write("\n")
                    count += 1

    print(f"\n✅ Export complete! {count} files exported to: {output_file}")

if __name__ == "__main__":
    export_codebase()
