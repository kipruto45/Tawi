import os,re
# gather all template files
tpls=[]
for dirpath,dirs,files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            # store path relative to templates/
            rel=os.path.join(dirpath,f).replace('\\','/')
            rel2=rel.split('templates/',1)[-1] if 'templates/' in rel else rel
            tpls.append(rel2)
# gather all template-string references in repo
refs=set()
pattern=re.compile(r"['\"]([\w\-/]+\.html)['\"]")
for dirpath,dirs,files in os.walk('.'):
    if any(p in dirpath for p in ['.venv','venv','.git','staticfiles','node_modules']):
        continue
    for f in files:
        ap=os.path.join(dirpath,f)
        if not f.endswith(('.py','.html','.js','.md','.txt')):
            continue
        try:
            s=open(ap,encoding='utf-8',errors='ignore').read()
        except Exception:
            continue
        for m in pattern.findall(s):
            refs.add(m)
# Now check which templates are referenced
unused=[]
used=[]
for tpl in sorted(tpls):
    if tpl in refs:
        used.append(tpl)
    else:
        unused.append(tpl)
# print summary
for u in unused:
    print('UNUSED:', u)
print('\nTOTAL TEMPLATES:', len(tpls))
print('USED:', len(used))
print('UNUSED:', len(unused))
print('\nSAMPLE referenced template strings found in code (first 50):')
for i,t in enumerate(sorted(refs)):
    if i<50:
        print(' ',t)
    else:
        break
