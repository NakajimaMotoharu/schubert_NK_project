"""Independent XML/site-set and fresh source projection seal; no engine or Test execution."""
from pathlib import Path
import collections,copy,datetime,hashlib,json,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];OPS=R/'evidence/01_PT/018_NK-OPS-001/evidence';P=OPS/'PG22606-ordinary85-classification-source-seal-v1';OUT=OPS/'PG22608-ordinary85-classification-source-seal-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
attrs=['beginline','endline','begincolumn','endcolumn','rule','ruleset','package','class','method','variable','externalInfoUrl','priority']
def ident(p,a):return (p,json.dumps(a,sort_keys=True))
def exact(rows,expected):return len(rows)==len(expected)==346 and len({ident(x['path'],x['originalAttributes']) for x in rows})==346 and {ident(x['path'],x['originalAttributes']) for x in rows}==expected

def main():
 assert not OUT.exists();m=load(P/'manifest.json');assert m['actualExit']==0 and m['productTestsExecuted']==0;assert sha(P/'sites.json')==m['files']['sites.json'];rows=load(P/'sites.json');raw=R/m['originalRawManifest']['path'];rm=load(raw);assert sha(raw)==m['originalRawManifest']['sha256'];assert sha(raw.parent/'pmd.xml')==rm['files']['pmd.xml'];orig={}
 for f in E.parse(raw.parent/'pmd.xml').getroot():
  for x in f:
   if x.tag.rsplit('}',1)[-1]=='violation':orig[ident(str(Path(f.get('name')).relative_to(R)),dict(x.attrib))]=' '.join(''.join(x.itertext()).split())[:600]
 assert len(orig)==347;removed=m['removedActualDefect'];rk=ident(removed['path'],removed['attributes']);assert removed['attributes']['rule']=='CloseResource' and rk in orig;up=load(R/m['removedDefectPost']['path']);assert sha(R/m['removedDefectPost']['path'])==m['removedDefectPost']['sha256'] and up['actualExit']==0 and up['finallyRecoveryPresent'];expected=set(orig)-{rk};assert exact(rows,expected)
 assert len(m['currentSourceHashes'])==85
 for n,h in m['currentSourceHashes'].items():assert '/src/test/java/' in n and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()
 changed={n for n,h in m['currentSourceHashes'].items() if h!=rm['begin']['inputHashes'][n]};assert len(changed)==9 and {x['path'] for x in m['changedSources']}==changed
 for b in m['changedSources']:
  assert b['sha256']==m['currentSourceHashes'][b['path']];post=load(R/b['post']['path']);assert sha(R/b['post']['path'])==b['post']['sha256'] and post['actualExit']==0
  assert post.get('testSha256')==b['sha256'] or post.get('inputHashes',{}).get(b['path'])==b['sha256']
 counts=[93,158,14,6,12,11,52];assert [x['count'] for x in m['classificationParts']]==counts and sum(counts)==346;proofs={}
 for x in m['classificationParts']:
  for k in ['collector','independentPost']:
   p=R/x[k]['path'];assert sha(p)==x[k]['sha256'] and load(p)['actualExit']==0
  proofs[x['independentPost']['path']]=(x['count'],x['independentPost']['sha256'])
 assert collections.Counter(x['independentPost']['path'] for x in rows)=={p:c for p,(c,h) in proofs.items()}
 # Independently recover the new PMD projections as exact XML-style attributes, no stable matching algorithm shared.
 projections={}
 for directory in [R/'evidence/01_PT/010_NK-ADM-001/evidence/PG22432-user-audit-cleanup-static-applicability-v1',R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22518-seven-security-port-static-applicability-v1']:
  v=load(directory/'manifest.json')
  for x in v['individualClassifications']:
   if x['sourcePath'] in changed:
    a={k:x[k] for k in attrs if k in x};projections[ident(x['sourcePath'],a)]=x['message'];assert v['inputHashes'][x['sourcePath']]==m['currentSourceHashes'][x['sourcePath']]
 q=OPS/'PG22488-question-bounded-wait-static-v1';qm=load(q/'manifest.json');assert sha(q/'pmd.xml')==qm['files']['pmd.xml']
 for f in E.parse(q/'pmd.xml').getroot():
  for x in f:
   if x.tag.rsplit('}',1)[-1]=='violation':projections[ident(str(Path(f.get('name')).relative_to(R)),dict(x.attrib))]=' '.join(''.join(x.itertext()).split())[:600]
 currentchanged={ident(x['path'],x['currentAttributes']):x['message'] for x in rows if x['path'] in changed};assert currentchanged==projections
 for x in rows:
  assert x['classification']=='NOT_APPLICABLE_INDIVIDUALLY_JUSTIFIED' and x['currentSourceSha256']==m['currentSourceHashes'][x['path']] and x['message']==orig[ident(x['path'],x['originalAttributes'])];assert x['independentPost']['sha256']==proofs[x['independentPost']['path']][1]
  if x['path'] not in changed:assert x['currentAttributes']==x['originalAttributes'] and x['freshProjection'] is None
 assert not exact(rows[:-1],expected) and not exact(rows+[rows[0]],expected);bad=copy.deepcopy(rows);bad[0]['originalAttributes']['rule']='MISSING_RULE';assert not exact(bad,expected)
 assert m['reconstructedNotFreshAll85EngineRun'] and m['questionDynamicHold'] and not any(m[k] for k in ['formalUpdated','wholeF03Accepted','whole451Accepted','ykt2177Closed']);OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),originalRawSites=347,removedActualDefects=1,currentComposedRaw=346,independentlyBoundClassifications=346,currentSourceCount=85,changedSourceCount=9,unchangedSourceCount=76,applicableSites=0,unclassifiedSites=0,duplicateSites=0,missingSites=0,metadataNegativeGuards=3,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,effortRate=None,reconstructedNotFreshAll85EngineRun=True,questionDynamicHold=True,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sourceFiles=85,composed=346,unclassified=0)))
if __name__=='__main__':main()
