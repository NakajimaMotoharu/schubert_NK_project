"""Primary UI223 table + independent synthetic claims, never production getters or factory outputs."""
from pathlib import Path
import argparse,hashlib,json,re
r=Path.cwd();doc=r/'documents/200_UI/220_画面・認証/223_現行機能画面設計.md';text=doc.read_text();section=text.split('## 6. SCR-008～010 Animation',1)[1].split('## 7. SCR-011～013 Music',1)[0];rows=[]
for line in section.splitlines():
 if not re.match(r'^\|\s*\d+\s*\|',line):continue
 parts=[x.strip().strip('`') for x in line.strip().strip('|').split('|')];assert len(parts)==6;order=int(parts[0]);rows.append((order,*parts[1:]))
assert len(rows)==20 and [x[0] for x in rows]==list(range(1,21));assert sum(x[3]=='メインパート' for x in rows)==15 and sum(x[3]=='OVA' for x in rows)==4 and sum(x[3]=='オープニング' for x in rows)==1
metadata=''.join('\t'.join(map(str,x))+'\n' for x in rows);wire='';sha='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad';stamp='2026-01-02T03:04:05Z'
for order,logical,title,category,source,parent in rows:
 fields=[str(1000+order),logical,'VIDEO',title,category,None,'video/fixture-'+str(order)+'.mp4',source,source.rsplit('/',1)[-1],'3',sha,'video/mp4',None if parent=='-' else parent,None,None,str(order),stamp]
 assert len(fields)==17 and all(x is None or not any(c in x for c in '\t\r\n\\') for x in fields)
 wire+='\t'.join('\\N' if x is None else x for x in fields)+'\n'
base=r/'src/schubert-nk-bootstrap/src/test/resources/fixtures';outputs={base/'migration-video-catalogue-20.tsv':metadata.encode(),base/'migration-video-copy-20.wire':wire.encode()};a=argparse.ArgumentParser();a.add_argument('--create',action='store_true');args=a.parse_args()
if args.create:assert not any(p.exists() for p in outputs)
for p,data in outputs.items():
 if args.create:p.parent.mkdir(parents=True,exist_ok=True);p.open('xb').write(data)
 else:assert p.read_bytes()==data
print(json.dumps(dict(actualExit=0,sourceDocument=dict(path=str(doc.relative_to(r)),sha256=hashlib.sha256(doc.read_bytes()).hexdigest()),rows20=True,metadataColumns=6,copyColumns=17,resources=[dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)) for p,data in outputs.items()],syntheticClaims='targetId1000+UIorder; targetPathvideo/fixture-{order}.mp4; abc SHA/3bytes; fixed UTC timestamp; no actual asset or production method',create=args.create),ensure_ascii=False))
