import glob, py_compile, sys
errs = []
for p in glob.glob('**/views.py', recursive=True):
    try:
        py_compile.compile(p, doraise=True)
    except Exception as e:
        errs.append((p, e))
for p,e in errs:
    print(p, '->', type(e).__name__ + ':', e)
if not errs:
    print('No syntax errors in any views.py')
