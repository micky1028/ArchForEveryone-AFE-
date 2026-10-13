import os
from pathlib import Path

def create_symlink(source, destination):
    src_path = Path(source).resolve()
    dest_path = Path(destination)
    
    if dest_path.is_symlink() or dest_path.exists():
        dest_path.unlink()
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.symlink_to(src_path)