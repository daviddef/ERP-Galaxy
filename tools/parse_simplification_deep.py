import re, json, sys
t=open("simpl2025.txt",errors="replace").read()
# strip page furniture
t=re.sub(r'\n\s*(Private Edition 2025[^\n]*|Public Cloud[^\n]*|Page \| \d+|\d+\s*)\n','\n',t)

# item body heading: "N.N.N. S4TWL - Title" NOT in the TOC (TOC lines end with page number + dots)
head=re.compile(r'^\s*(\d+(?:\.\d+){1,3})\.?\s+(S4TWL|ABAPTWL)\s*[-–]\s*(.+?)\s*$', re.M)
heads=[m for m in head.finditer(t) if not re.search(r'\.{5,}\s*\d+\s*$', m.group(0)) and "Application Component" in t[m.start():m.start()+400]]
print("item bodies:", len(heads), file=sys.stderr)

def field(seg, label, nxt):
    m=re.search(re.escape(label)+r'\s*(.*?)(?='+'|'.join(re.escape(n) for n in nxt)+r'|\Z)', seg, re.S)
    return re.sub(r'\s+',' ',m.group(1)).strip() if m else None

SECTIONS=["Related Notes","Symptom","Reason and Prerequisites","Solution","Description",
          "Business Process related information","Required and Recommended Action",
          "How to Determine Relevancy","Application Component"]
out={}
for i,m in enumerate(heads):
    end=heads[i+1].start() if i+1<len(heads) else len(t)
    seg=t[m.start():end]
    # note numbers: 10-digit zero-padded, strip leading zeros
    notes=[]
    rn=re.search(r'Related Notes(.*?)(?=Symptom|Solution|Description|Required|How to|\Z)', seg, re.S)
    if rn:
        for nm in re.finditer(r'\b0*(\d{6,7})\b', rn.group(1)):
            n=nm.group(1)
            if n not in notes: notes.append(n)
    action=field(seg,"Required and Recommended Action", ["How to Determine","Business Process","\n\n\n"])
    out[m.group(1)]={"title":re.sub(r'\s+',' ',m.group(3)).strip(),
                     "notes":notes[:4],
                     "action":(action[:500] if action else None)}
json.dump(out, open("items2025.json","w"), indent=1)
print("parsed items:", len(out), "| with a note:", sum(1 for v in out.values() if v["notes"]),
      "| with an action:", sum(1 for v in out.values() if v["action"]), file=sys.stderr)
