"""Individual source judgments, immutable raw findings and current declarations; no Product action."""
from pathlib import Path
import collections,datetime,hashlib,json,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22598-remaining52-map-owners-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
 assert not OUT.exists();cfgpath=R/'evidence/01_PT/018_NK-OPS-001/input/229_remaining52_map_owners.json';cfg=load(cfgpath);raw=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1/manifest.json';assert sha(raw)=='e4eea946c71b78db2cca778259ef366cd4cd60c208708941a61067f48cee25a2';old=load(raw);rp=raw.parent/'pmd.xml';assert sha(rp)==old['files']['pmd.xml'];original=[]
 for f in E.parse(rp).getroot():
  for v in f:
   if v.tag.rsplit('}',1)[-1]=='violation':original.append((str(Path(f.get('name')).relative_to(R)),dict(v.attrib)))
 inv=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22502-test-wait85-source-inventory-v1';im=load(inv/'manifest.json');assert sha(inv/'parse.stdout')==im['files']['parse.stdout'];vars=[s.split('\t') for s in (inv/'parse.stdout').read_text().splitlines() if s.startswith('VAR\t')];inputs={};rows=[]
 for row in cfg['sites']:
  p=row['path'];a=row['originalAttributes'];assert (p,a) in original;assert '/src/test/java/' in p and not any(x in p for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/p)==row['sourceSha256'];inputs[p]=sha(R/p);text=(R/p).read_text();assert all(w in text for w in row['witnesses']) and row['reason'];r=dict(row)
  if a['rule']=='UseConcurrentHashMap':
   vs=[v for v in vars if v[1]==p and v[2]==a['class'] and v[3]==a.get('method','<field>') and v[4]==a['variable']];assert len(vs)==1;v=vs[0];line=int(v[7]);assert 'Map' in v[5] and 'HashMap' in v[6];r.update(currentDeclarationLine=line,declaration=text.splitlines()[line-1].strip(),oldAstVariable=v)
  else:r.update(currentDeclarationLine=int(a['beginline']),declaration=text.splitlines()[int(a['beginline'])-1].strip())
  rows.append(r)
 OUT.mkdir();(OUT/'sites.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',inputHashes=inputs,config=dict(path=str(cfgpath.relative_to(R)),sha256=sha(cfgpath)),originalRawManifest=dict(path=str(raw.relative_to(R)),sha256=sha(raw)),selectedMapSites=52,selectedReflectionSites=0,newIndividualClassifications=52,originalRaw347Preserved=True,currentReconstructedRaw=346,currentSubsetClassifiedBefore=294,currentSubsetClassifiedAfter=346,currentSubsetUnclassifiedBefore=52,currentSubsetUnclassifiedAfter=0,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,effortRate=None,wholeF03Accepted=False,whole451Accepted=False,suppressionAdded=False,files={'sites.json':sha(OUT/'sites.json')},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=52,remaining=0)))
if __name__=='__main__':main()
