from pathlib import Path
import urllib.request,zipfile,io,hashlib,json
repo=Path(__file__).resolve().parent;target=repo/'research/craft-i18n'
sha='e02939ef009218e81c44e8ec001fbb7603461de4'
if not target.exists():
 op=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:7888'}))
 with op.open(urllib.request.Request(f'https://codeload.github.com/storytold/craft-i18n/zip/{sha}',headers={'User-Agent':'Photocraft-dev'}),timeout=90) as response:data=response.read(40*1024*1024)
 with zipfile.ZipFile(io.BytesIO(data)) as archive:
  for member in archive.infolist():
   p=target/Path(*Path(member.filename).parts[1:]);assert p.resolve().is_relative_to(target.resolve())
   if member.is_dir():p.mkdir(parents=True,exist_ok=True)
   else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.read(member))
 (repo/'research/i18n-source.json').write_text(json.dumps({'sha':sha,'archive_sha256':hashlib.sha256(data).hexdigest()},indent=2))
# Keep translations local to this edition; do not modify the old edition or remote catalogs.
overlay=json.loads((repo/'native-source/i18n-overlay.json').read_text(encoding='utf8'))
for code,rows in overlay.items():
 p=target/'locales'/code/'photocraft.tsv';original=p.read_text(encoding='utf8');keys={tuple(line.split('\t')[:2]) for line in rows}
 keep=[line for line in original.splitlines() if tuple(line.split('\t')[:2]) not in keys]
 p.write_text('\n'.join(keep+rows)+'\n',encoding='utf8')
print('Pinned catalogs ready',target,flush=True)
