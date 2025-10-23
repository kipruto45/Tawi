import os,sys
root='.'
# collect templates
tpls=[]
for dirpath,dirs,files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            rel=os.path.join(dirpath.replace('\\','/'),f)
            tpls.append(rel)
# search
matches={tpl:0 for tpl in tpls}
# scan repo files
for dirpath,dirs,files in os.walk('.'):
    # skip virtualenv and staticfiles and .git
    if any(p in dirpath for p in ['.venv','venv','.git','staticfiles','node_modules']):
        continue
    for f in files:
        ap=os.path.join(dirpath,f)
        if f.endswith(('.py','.html','.js','.md','.txt')):
            try:
                s=open(ap,encoding='utf-8',errors='ignore').read()
            except Exception:
                continue
            for tpl in tpls:
                # match by full relative path or just basename
                if tpl in s or tpl.split('/',1)[-1] in s:
                    matches[tpl]+=1
# print results
unused=[]
for tpl,count in sorted(matches.items(), key=lambda x:(x[1],x[0])):
    if count==0:
        print('UNUSED:', tpl)
        unused.append(tpl)
    else:
        print(f'{count:4d} refs: {tpl}')
print('\nTOTAL TEMPLATES:', len(tpls))
print('UNUSED COUNT:', len(unused))
