import re
def parse(h):
    """leanx.eu: key field rows carry class bg-blue-50; field name is the first font-medium div."""
    keys=[]
    for m in re.finditer(r'<tr class="([^"]*)">(.*?)</tr>', h, re.S):
        cls, row = m.group(1), m.group(2)
        n = re.search(r'<div class="font-medium[^"]*">\s*([A-Z0-9_/]{2,30})\s*</div>', row)
        if not n: continue
        if "bg-blue-50" in cls: keys.append(n.group(1))
    return keys
