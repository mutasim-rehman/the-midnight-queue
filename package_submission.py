"""
Packaging Script for The Midnight Queue Assignment 2 Deliverables.
Produces:
- 24i-2514-A2-A.zip
- 24i-2514-A2-B.zip
- 2514-A2-Section.zip
Strictly excludes dataset files (creditcard.csv), cache, and git history.
"""
import os
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {
    ".git", "__pycache__", ".pytest_cache", "mlg-ulb", ".venv", "venv", "env"
}

EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".pyd"
}

EXCLUDE_FILES = {
    "creditcard.csv"
}

def make_zip(zip_name):
    root_dir = Path(".")
    count = 0
    total_uncompressed = 0
    
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for current_path, dirs, files in os.walk(root_dir):
            # Prune excluded dirs
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                if file.endswith(".zip") and file != zip_name:
                    continue
                if file == zip_name:
                    continue
                
                full_path = Path(current_path) / file
                rel_path = full_path.relative_to(root_dir)
                
                zf.write(full_path, rel_path)
                count += 1
                total_uncompressed += full_path.stat().st_size
                
    zip_size = Path(zip_name).stat().st_size
    print(f"Created '{zip_name}': {count} files, Uncompressed: {total_uncompressed/1024/1024:.2f} MB, Zip Size: {zip_size/1024/1024:.2f} MB")
    
    # Verify no creditcard.csv inside
    with zipfile.ZipFile(zip_name, "r") as zf:
        namelist = zf.namelist()
        for name in namelist:
            assert "creditcard.csv" not in name.lower(), f"CRITICAL: Found creditcard.csv in {name}!"
    print(f"Verified: '{zip_name}' strictly excludes creditcard.csv and caches.")

if __name__ == "__main__":
    make_zip("24i-2514-A2-A.zip")
    make_zip("24i-2514-A2-B.zip")
    make_zip("2514-A2-Section.zip")
    print("All submission zip archives successfully generated!")
