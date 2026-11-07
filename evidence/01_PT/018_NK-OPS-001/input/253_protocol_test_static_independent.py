"""Independent25 input/three raw static tools/exit/report/no-Product checks; not a PASS gate."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG22760-protocol-all-test-static-v1';O=B/'evidence/PG22762-protocol-static-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
 assert not O.exists();m=load(P/'manifest.json');assert m['actualExit']==0 and m['productTestsExecuted']==0 and m['checkedSources']==25;fpath=R/m['freeze']['path'];assert sha(fpath)==m['freeze']['sha256'];f=load(fpath);indexed={}
 for raw in subprocess.check_output(['git','ls-files','--stage','-z','--','src/schubert-nk-protocol/src/test/java'],cwd=R).split(b'\0'):
  if not raw:continue
  meta,n=raw.decode().split('\t',1);mode,oid,stage=meta.split();assert mode=='100644' and stage=='0' and n.endswith('.java') and n.startswith('src/schubert-nk-protocol/');indexed[n]=oid
 assert len(indexed)==25 and set(indexed)==set(f['inputs'])==set(m['inputHashes'])
 for n,h in m['inputHashes'].items():assert sha(R/n)==h==f['inputs'][n]['sha256'] and indexed[n]==f['inputs'][n]['gitBlob'] and hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()==h
 for n,h in m['dependencies'].items():assert sha(n)==h
 for n,h in m['files'].items():assert sha(P/n)==h
 reports={}
 for label,tag in [('pmd','violation'),('checkstyle','error')]:
  root=E.parse(P/(label+'.xml')).getroot();items=[]
  for parent in root.iter():
   if parent.tag.rsplit('}',1)[-1]=='file':
    n=str(Path(parent.get('name')).relative_to(R));assert n in indexed
    for x in parent:
     if x.tag.rsplit('}',1)[-1]==tag:items.append(dict(path=n,**x.attrib,message=' '.join(''.join(x.itertext()).split())[:600],classification='UNCLASSIFIED'))
  errors=[dict(x.attrib) for x in root.iter() if label=='pmd' and x.tag.rsplit('}',1)[-1] in ['error','configerror']];assert not errors;assert items==m['reports'][label]['rawItems'] and len(items)==m['reports'][label]['rawCount'];reports[label]=dict(rawCount=len(items),unclassified=len(items),applicable=None,processingErrors=0)
 for label,s in m['stages'].items():
  assert s==load(P/(label+'-exit.safe.json')) and not s['timedOut']
  for stream in ['stdout','stderr']:assert sha(P/(label+'.'+stream))==s[stream+'Sha256']
  cmd=s['command'];assert 'javac' not in Path(cmd[0]).name and not any(x in cmd for x in ['execute','org.junit.platform.console.ConsoleLauncher','-javaagent','--scan-classpath']);log=(P/(label+'-class-init.stdout')).read_text();assert "Initializing 'java/lang/Object'" in log;assert not re.search(r"Initializing '(?:dev/codex/schubert/nk/|dev\.codex\.schubert\.nk\.)",log);assert m['productInitializations'][label]==[]
  assert any(x.startswith('-Xlog:class+init=info:file=') for x in cmd)
 assert m['stages']['pmd']['actualExit']==(4 if reports['pmd']['rawCount'] else 0)
 assert (m['stages']['checkstyle']['actualExit']==0)==(reports['checkstyle']['rawCount']==0)
 fmt=m['stages']['format'];assert '--dry-run' in fmt['command'] and '--replace' not in fmt['command'] and '--set-exit-if-changed' in fmt['command'];assert fmt['command'][-25:]==sorted(indexed) and fmt['actualExit'] in [0,1]
 formatPaths=(P/'format.stdout').read_text().splitlines();assert all(n in indexed for n in formatPaths);assert (fmt['actualExit']==0)==(not formatPaths)
 assert (P/'sources.txt').read_text()==''.join(str(R/n)+'\n' for n in sorted(indexed));assert m['applicableFindings'] is None and not m['allFindingsClassified'] and not m['wholeF03Accepted']
 O.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),checkedSources=25,reports=reports,formatExit=fmt['actualExit'],formatDifferencePaths=formatPaths,productInitializations=0,sourceBytesUnchanged=True,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,coverageMeasured=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,inputHashes=m['inputHashes'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,reports=reports,formatExit=fmt['actualExit'],formatDifferencePaths=formatPaths,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
