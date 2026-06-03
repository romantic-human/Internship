def build_tree(items, parent_id=None):
    tree = []
    for item in items:
        if item.get("parent_id") == parent_id:
            children = build_tree(items, item.get("id"))
            if children:
                item["children"] = children
            tree.append(item)
    return tree


def flatten_tree(tree, result=None):
    if result is None:
        result = []
    for node in tree:
        result.append(node)
        if "children" in node:
            flatten_tree(node["children"], result)
    return result