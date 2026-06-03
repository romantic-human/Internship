#!/usr/bin/env python3
"""Push current branch to remote feature/sunyf via GitHub API.
Fixed: uses core.quotepath=false to get correct Chinese filenames."""
import json, os, subprocess, sys, base64, urllib.request, urllib.error

OWNER, REPO = "romantic-human", "Internship"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"
GIT_DIR = os.path.join(os.path.dirname(__file__), ".git")

def git(args):
    r = subprocess.run(["git", "--git-dir", GIT_DIR] + args, capture_output=True, text=True)
    if r.returncode:
        print(f"git error: {r.stderr}", file=sys.stderr), sys.exit(1)
    return r.stdout.strip()

def git_lines(args):
    r = subprocess.run(["git", "--git-dir", GIT_DIR] + args, capture_output=True, text=True)
    if r.returncode:
        print(f"git error: {r.stderr}", file=sys.stderr), sys.exit(1)
    return r.stdout.strip().split("\n")

def api(method, path, data=None, token=None):
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "push"}
    if token: headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{API_URL}/{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API {e.code}: {e.read().decode()}", file=sys.stderr), sys.exit(1)

def main():
    token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_TOKEN")
    if not token:
        print("Usage: push.py <token>", file=sys.stderr), sys.exit(1)

    # Get the base tree from remote develop
    base_sha = api("GET", "git/refs/heads/develop", token=token)["object"]["sha"]
    print(f"Base develop: {base_sha}")

    # Use core.quotepath=false to get correct unicode paths for Chinese filenames
    lines = git_lines(["-c", "core.quotepath=false", "ls-tree", "-r", "HEAD"])
    print(f"Files: {len(lines)}")

    blobs = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        mode, typ, sha, path = line.split(maxsplit=3)
        content = git(["show", sha])
        blob = api("POST", "git/blobs", token=token, data={
            "content": base64.b64encode(content.encode()).decode(), "encoding": "base64"
        })
        blobs.append({"path": path, "mode": mode, "type": "blob", "sha": blob["sha"]})
        if (i+1) % 20 == 0:
            print(f"  ... {i+1}/{len(lines)}")

    new_tree = api("POST", "git/trees", token=token, data={"tree": blobs})["sha"]
    print(f"Tree: {new_tree}")

    msg = git(["log", "HEAD", "--format=%B", "-1"])
    commit = api("POST", "git/commits", token=token, data={
        "message": msg, "tree": new_tree, "parents": [base_sha]
    })["sha"]
    print(f"Commit: {commit}")

    # Create the ref (branch was deleted, so POST is fine)
    api("POST", "git/refs", token=token, data={
        "ref": "refs/heads/feature/sunyf", "sha": commit
    })
    print(f"✅ feature/sunyf created -> {commit}")

if __name__ == "__main__":
    main()