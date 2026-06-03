#!/usr/bin/env python3
"""Fix quoted filenames in git repo."""
import subprocess, os

REPO = "Internship"

# Map from SHA content prefix to correct filename
fix_map = {
    "345274200345217221346265201347250213346214207345215227": "开发流程指南.md",
    "345274200345217221350247204350214203": "开发规范.md",
    "346250241345235227345210222345210206344270216345274200345217221345210206345267245": "模块划分与开发分工.md",
    "347216257345242203346220255345273272346214207345215227": "环境搭建指南.md",
    "347273204347273207346236266346236204346250241345235227350256276350256241346226271346241210": "组织架构模块设计方案.md",
}

result = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "HEAD"], capture_output=True, text=True)
lines = result.stdout.strip().split("\n")

os.chdir(REPO)

for line in lines:
    if not line.strip():
        continue
    parts = line.split(maxsplit=3)
    if len(parts) != 4:
        continue
    mode, typ, sha, quoted_path = parts
    
    # Check if path starts with quote
    if quoted_path.startswith('"') and quoted_path.endswith('"'):
        # Extract the hex-encoded name
        inner = quoted_path[1:-1]  # remove surrounding quotes
        hex_key = inner.replace("\\", "")
        
        if hex_key in fix_map:
            correct_name = fix_map[hex_key]
            print(f"Fixing: {quoted_path} -> {correct_name}")
            # Remove old entry from index
            subprocess.run(["git", "rm", "--cached", quoted_path], capture_output=True)
            # Add with correct name, same blob sha
            subprocess.run(["git", "update-index", "--add", "--cacheinfo", mode, sha, correct_name], capture_output=True)
            print(f"  ✅ Fixed")
        else:
            print(f"⚠️  Unknown quoted file: {quoted_path}")

os.chdir("..")
print("Done")