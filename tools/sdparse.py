import re, html as H

def parse(sd_html):
    """Extract (keyFields, allFieldCount, desc) from a sapdatasheet /abap/tabl/ page."""
    # field rows look like: <a id="FIELD_X"></a> N ... name="field_X" ... checked ...
    rows = re.findall(r'<tr>(.*?)</tr>', sd_html, re.S)
    keys=[]; nfields=0
    for r in rows:
        m = re.search(r'<a id="FIELD_([A-Z0-9_/]+)"></a>\s*(\d+)', r)
        if not m: continue
        fname, pos = m.group(1), int(m.group(2))
        nfields += 1
        cb = re.search(r'name="field_'+re.escape(fname)+r'"([^>]*)>', r)
        if cb and 'checked' in cb.group(1):
            keys.append((pos, fname))
    keys.sort()
    d = re.search(r'<title>\s*SAP ABAP Table\s+\S+\s*\((.*?)\)', sd_html)
    return [f for _,f in keys], nfields, (H.unescape(d.group(1)).strip() if d else None)

if __name__ == "__main__":
    k,n,d = parse(open("probe_bkpf.html",errors="replace").read())
    print("BKPF ->", k, "| fields:", n, "| desc:", d)
    print("expected: ['MANDT','BUKRS','BELNR','GJAHR']  match:", k==['MANDT','BUKRS','BELNR','GJAHR'])
