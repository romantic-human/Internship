import re
path = r"D:\Internship\Internship\Internship-core\apps\menu\views.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
pattern = r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> .*\n'
resolved = re.sub(pattern, lambda m: m.group(1), content, flags=re.DOTALL)
with open(path, "w", encoding="utf-8") as f:
    f.write(resolved)
print("Resolved")
