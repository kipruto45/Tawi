import subprocess, collections, sys
p = subprocess.run([sys.executable, '-m', 'flake8', '.', '--max-line-length=120', '--exclude=.venv,venv,ENV,env,build,dist', "--format=%(path)s::%(code)s"], capture_output=True, text=True)
output = (p.stdout or '') + '\n' + (p.stderr or '')
lines = output.strip().splitlines()
counts = collections.Counter()
perfile = {}
for line in lines:
    if not line:
        continue
    parts = line.split('::', 1)
    if len(parts) != 2:
        continue
    path, code = parts
    counts[path] += 1
    perfile.setdefault(path, []).append(code)

top = sorted(counts.items(), key=lambda x: -x[1])[:40]
print('Top files by flake8 findings (count, path, {code: count}):')
for path, c in top:
    codes = collections.Counter(perfile[path])
    print(f"{c:4d}  {path}  {dict(codes)}")

# Also print total issues and top error codes overall
allcodes = collections.Counter()
for codes in perfile.values():
    allcodes.update(codes)
print('\nTop error codes overall:')
for code, cnt in allcodes.most_common(20):
    print(f"{code}: {cnt}")
print('\nFull flake8 output truncated (first 100 lines):')
for L in lines[:100]:
    print(L)
