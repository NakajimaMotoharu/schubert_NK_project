from pathlib import Path
import ast,datetime,hashlib,json,re,subprocess,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'input';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
f=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/InspectorUnitProbeFixture.java';producer=I/'2203_mpol_static_closure_correction.py';tree=ast.parse(producer.read_text());texts={}
for x in tree.body:
 if isinstance(x,ast.Assign) and len(x.targets)==1 and isinstance(x.targets[0],ast.Name) and x.targets[0].id in ['a','b']:texts[x.targets[0].id]=ast.literal_eval(x.value)
text=f.read_text();start=text.index('      int currentState = stateAt;');end=text.index('\n    }',start);actual=text[start:end];tokens=lambda v:re.findall(r'"(?:[^"\\]|\\.)*"|[A-Za-z0-9_$]+|[^\s]',v);assert tokens(actual)==tokens(texts['b']);inverse=text[:start]+texts['a']+text[end:];original=ld(B/'evidence/PG28804-mpol-whole8-current-source-oracle-closure-v1/manifest.json');assert hashlib.sha256(inverse.encode()).hexdigest()==original['testInputHashes'][str(f.relative_to(R))]
p=R/'documents/900_OTHER/910_台帳/915_障害表.md';p.write_text(p.read_text()+'\nBUG2785同種追加：2203もhelper field chainのGJF再改行でraw snippet逆変換assert停止。再編集/producer再演せず2203bで文字列literal保持token同一→該当method領域のみ逆変換しPG28804全helper SHAと一致。ProductPT0、元失敗維持。\n')
# Execute only the unstarted metadata/post-tool suffix; the fixture edit and formatter are not replayed.
source=producer.read_text();suffix=source[source.index("old=B/'evidence/PG28804-"):];exec(compile(suffix,str(producer)+'#metadata-only-suffix','exec'),globals())
