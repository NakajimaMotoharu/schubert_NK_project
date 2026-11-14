from pathlib import Path
import hashlib,json,collections
r=Path.cwd();folder=r/'src/schubert-nk-bootstrap/src/test/resources/fixtures';e=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG31384-music-catalogue-source-twentyfour-v1';e.mkdir()
paths=['曲/ゲーム/01-01 Alpha.ogg','曲/ゲーム/01-02 Alpha inst.ogg','曲/ゲーム/01-03 Beta.ogg','曲/ゲーム/01-04 Beto inst.ogg','曲/ゲーム/01-05 Alone.ogg','曲/ゲーム/01-06 Zzzzzzz inst.ogg','曲/アニメ/01-01 Anime.m4a','曲/キャラクターソング/01-01 Character.flac','曲/Zebra/01-01 Other.wav','BGM/ゲーム/01.ogg','BGM/アニメ/02.mp3','AOther/ZZZ/03.wav','😀Other/😀Sec/04.flac']+[f'BGM/ゲーム/filler-{n:03}.ogg' for n in range(116)]
assert len(paths)==129
stamp='2026-01-02T03:04:05Z';sha=hashlib.sha256(b'abc').hexdigest();mime={'.m4a':'audio/mp4','.mp3':'audio/mpeg','.ogg':'audio/ogg','.wav':'audio/wav','.flac':'audio/flac'};logical=lambda p:hashlib.sha256(b'SCHUBERT-NK:MUSIC:'+p.encode()).hexdigest()
# Pair assignments are independently declared, not computed by a copy of the Java matching algorithm.
song_assign={'曲/ゲーム/01-01 Alpha.ogg':('alpha','M',1),'曲/ゲーム/01-02 Alpha inst.ogg':('alpha','I',1),'曲/ゲーム/01-03 Beta.ogg':('beta','M',2),'曲/ゲーム/01-04 Beto inst.ogg':('beta','I',2),'曲/ゲーム/01-05 Alone.ogg':('alone','M',3),'曲/ゲーム/01-06 Zzzzzzz inst.ogg':('zzzzzzz','I',4),'曲/アニメ/01-01 Anime.m4a':('anime','M',1),'曲/キャラクターソング/01-01 Character.flac':('character','M',1),'曲/Zebra/01-01 Other.wav':('other','M',1)}
metadata=[];fields=[];groups=collections.defaultdict(list)
for n,p in enumerate(paths):
 ext='.'+p.rsplit('.',1)[1];target=f'music/fixture-{n:03}{ext}';metadata.append([p,target,str(10000+n),logical(p)]);parts=p.split('/');groups[tuple(parts[:2])].append(p)
for group in groups.values():group.sort()
for p,target,targetid,lid in sorted(metadata):
 parts=p.split('/');category,section=parts[:2];name=parts[-1];title=name.rsplit('.',1)[0]
 key,role,order=song_assign[p] if category=='曲' else (None,'N',groups[(category,section)].index(p)+1)
 fields.append([targetid,lid,'MUSIC',title,category,section,target,p,name,'3',sha,mime['.'+name.rsplit('.',1)[1]],None,key,role,str(order),stamp])
wire=''.join('\t'.join('\\N' if c is None else c for c in row)+'\n' for row in fields)
replacements=['Solo.ogg','BGM/a.ogg','BGM/ゲーム/.ogg','BGM/ゲーム/😀.ogg','BGM/ゲーム/\ue000.ogg','BGM/ゲーム/bad.xyz','BGM/ゲーム/noextension','BGM/ゲーム/UPPER.OGG','曲/ゲーム/01-07 Alpha.ogg','曲/ゲーム/01-07 Alpha inst.ogg','曲/ゲーム/!!!.ogg','BGM/ゲーム/'+('a'*257)+'.ogg']
resources={'migration-music-catalogue-129.tsv':''.join('\t'.join(row)+'\n' for row in sorted(metadata)),'migration-music-copy-129.wire':wire,'migration-music-extra-id-vectors.tsv':''.join(p+'\t'+logical(p)+'\n' for p in replacements)}
refs=[]
for name,text in resources.items():
 p=folder/name;p.open('x').write(text);refs.append(dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=len(p.read_bytes())))
proof=dict(method='Synthetic metadata only; Python hashlib ASCII prefix+UTF8, explicit song key/role/order table and independent Python codepoint non-song sort; no Production/Current executable/original asset access.',musicRows=129,videoRows=20,combinedRows=149,syntheticShaAbc=sha,resources=refs,manualSongAssignments={p:list(v) for p,v in song_assign.items()},expectedCombinedSha256=hashlib.sha256((folder/'migration-video-copy-20.wire').read_bytes()+wire.encode()).hexdigest(),productionExpectedCalls=0)
(e/'independent-fixtures.json').open('x').write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');(e/'independent-fixtures-generator.py').open('x').write(Path('/tmp/pgpt361-fixtures.py').read_text());print({'newResources':len(refs),'musicRows':129,'combinedRows':149,'expectedMusicWireBytes':len(wire.encode())})
