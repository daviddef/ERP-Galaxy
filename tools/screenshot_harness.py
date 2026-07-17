import sys
state=sys.argv[1]
src=open("/Users/daviddefranceski/Claude/Projects/ERP Galaxy/sap-table-explorer.html",errors="replace").read()
acts={
 "graph":  "",
 "detail": "jumpTo('BSEG'); openMobilePanel('BSEG');",
 "drawer": "toggleTools(true);",
 "impact": ("LOCKS=['BSEG','BKPF','COSS','GLPCA','T001']; saveLocks();"
            "onlyLocked=true; renderLockBar(); updateGraph(); renderImpact();"),
}[state]
# one state, held forever — no competing timers, so a slow screenshot can't miss it
seq = "setTimeout(()=>{try{%s}catch(e){console.log(e);}},3000);" % acts if acts else ""
src=src.replace("window.addEventListener('load',init);",
                "window.addEventListener('load',()=>{init();"+seq+"});")
open("/Users/daviddefranceski/Claude/Projects/ERP Galaxy/ERPGalaxy/Resources/Web/erp-galaxy.html","w").write(src)
print("state:", state)
