import re
path = r"D:\Internship\Internship\Internship-core\requirements.txt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
pattern = r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> .*\n'
# Keep HEAD version (our B-task changes) for requirements.txt
resolved = re.sub(pattern, lambda m: m.group(1), content, flags=re.DOTALL)
with open(path, "w", encoding="utf-8") as f:
    f.write(resolved)
print("Resolved requirements.txt")
