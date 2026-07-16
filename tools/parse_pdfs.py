import re, os, json, glob
TXT="txt"
tables={}; tcodes={}

def add(name, desc, ttype, src, bucket):
    name=name.strip().upper()
    if not re.fullmatch(r'[A-Z0-9_/]{2,30}', name): return
    desc=re.sub(r'\s+',' ',desc).strip(' .;:')
    e=bucket.setdefault(name, {"desc":desc, "type":ttype, "sources":set()})
    e["sources"].add(src)
    if len(desc)>len(e["desc"]): e["desc"]=desc

for path in sorted(glob.glob(f"{TXT}/*.txt")):
    base=os.path.basename(path)[:-4]
    raw=open(path, errors="replace").read()
    bl=base.lower()
    bucket = tcodes if ("transaction" in bl or "tcode" in bl) else tables

    if base=="SAP EHS Tables":
        TYPES=r'(Transparent Table|General View Structure|Append Structure|Pooled Table|Cluster Table|Structure|View)'
        head=re.compile(r'^\s*(\d+)\s+([A-Z0-9_/]{2,30})\s{2,}(.+?)\s{2,}'+TYPES+r'\s*$')
        cur=None; col=None
        def flush():
            if cur: add(cur["n"], cur["d"], cur["t"], base, bucket)
        for r in raw.split("\n"):
            r=r.replace("\x0c"," ").rstrip()
            if not r.strip():
                continue
            m=head.match(r)
            if m:
                flush()
                cur={"n":m.group(2),"d":m.group(3).strip(),"t":m.group(4)}
                col=m.start(3)                      # where the description column begins
            elif cur is not None:
                indent=len(r)-len(r.lstrip())
                # a continuation must align to THIS row's description column (+/- 3),
                # which rejects page artifacts and the trailing table-of-contents
                if abs(indent-col)<=3:
                    cur["d"]+=" "+r.strip()
                else:
                    flush(); cur=None; col=None
        flush()
        continue

    if base=="SAP HR Infotypes":
        for line in raw.splitlines():
            m=re.match(r'^([A-Z][A-Z0-9_/]{1,29})\s+(\S.*)$', line.strip())
            if m: add(m.group(1), m.group(2), "Transparent Table", base, bucket)
        continue

    r=re.sub(r'\n\s*\n','\n',raw)
    for p in re.split(r'^\s*[•\-\*]\s*', r, flags=re.M)[1:]:
        p=" ".join(l.strip() for l in p.splitlines()).strip()
        m=re.match(r'^([A-Z0-9_/]{2,30})\s*:\s*(.*)$', p)
        if not m: continue
        d=re.sub(r'^\(\s*Category\s*:\s*([A-Z0-9\-]+)\s*\)?\s*','',m.group(2))
        d=re.sub(r'^(?:This (?:table|transaction)\s*)?(?:contains?|contain|stores the data of|is used to)\s*','',d,flags=re.I)
        add(m.group(1), d, "Transparent Table", base, bucket)

for b,n in ((tables,"tables"),(tcodes,"tcodes")):
    for v in b.values(): v["sources"]=sorted(v["sources"])
    json.dump(b, open(f"{n}.json","w"), indent=1, sort_keys=True)
print("tables:", len(tables), "| tcodes:", len(tcodes))
