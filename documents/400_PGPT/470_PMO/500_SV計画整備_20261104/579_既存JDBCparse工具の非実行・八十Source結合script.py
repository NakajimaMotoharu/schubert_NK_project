"""S parse-only resource candidate inventory; no Product code execution."""
import base64,hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path.cwd();BASE=ROOT/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg18534-sv80-jdbc-ast-v1'
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18534-sv80-jdbc-ast-v1/manifest.json'
TOOL=ROOT/'tools/quality/SourceJdbcOwnershipInventory.java'
JDK=ROOT.parent/'toolchain/jdk-25.0.4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 assert not SLOT.exists() and not OUT.exists()
 matrix=json.loads((BASE/'503_Source証拠再利用判定.json').read_bytes())
 sources={r['path']:r for r in matrix['rows'] if r['evidenceStatus']=='PARTIAL'};assert len(sources)==80
 for name,info in sources.items():
  assert '/src/main/java/' in name and Path(name).name not in {'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java','SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py'}
  assert sha(ROOT/name)==info['sha256']
 linePath=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18532-sv80-line-static-resume-v1/manifest.json';assert sha(linePath)=='6cbcf4309cfb2f7b91274fdb7875d7f8edea8e8a5466bc12c13e5da4c922c763'
 lineData=json.loads(linePath.read_bytes());anchors={s['path']:s['lineAnchors'] for r in lineData['results']+lineData['reusedStaticSuccess'] for s in r['sourceRows']};assert set(anchors)==set(sources)
 SLOT.mkdir();classes=SLOT/'classes';classes.mkdir();stages=[]
 def run(args,label):
  result=subprocess.run(args,cwd=ROOT,capture_output=True,timeout=60,check=False)
  for suffix,raw in (('stdout',result.stdout),('stderr',result.stderr)):
   with (SLOT/(label+'.'+suffix)).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  m={'command':args,'actualExit':result.returncode,'stdoutSha256':sha(SLOT/(label+'.stdout')),'stderrSha256':sha(SLOT/(label+'.stderr')),'stdoutBytes':len(result.stdout),'stderrBytes':len(result.stderr)};stages.append(m);write(SLOT/(label+'.terminal.json'),m)
  return result
 first=run([str(JDK/'bin/javac'),'--release','25','-proc:none','-d',str(classes),str(TOOL)],'compile')
 if first.returncode:write(OUT,{'actualExit':first.returncode,'source':matrix['source'],'stages':stages,'phase':'TOOL_COMPILE_FAILURE','newProductPT':0});raise SystemExit(first.returncode)
 parsed=run([str(JDK/'bin/java'),'-cp',str(classes),'SourceJdbcOwnershipInventory',*sorted(sources)],'parse')
 rows=[]
 if parsed.returncode==0:
  for ordinal,line in enumerate(parsed.stdout.decode().splitlines(),1):
   fields=[base64.b64decode(x).decode() for x in line.split('\t')];assert len(fields)==14
   name=str(Path(fields[0]).relative_to(ROOT));assert name in sources
   start,end=int(fields[3]),int(fields[4]);assert start>0 and end>=start
   rows.append({'candidateId':'S-JDBC-AST-'+str(ordinal).zfill(3),'path':name,'sourceSha256':sources[name]['sha256'],'logicalOwnerOriginal':sources[name]['owner'],'methodNameNotOverloadIdentity':fields[1],'variable':fields[2],'acquisitionLines':[start,end],'operation':fields[12],'immediateDirectFinallyPattern':fields[11]=='true','codeSnippetSha256':{key:hashlib.sha256(fields[n].encode()).hexdigest() for key,n in [('resource',5),('primary',7),('body',8),('catch',9),('finally',10),('declarations',13)]},'missingAcquisitionLineAnchors':[x for x in anchors[name] if start<=x['sourceLine']<=end],'decision':'STRUCTURAL_CANDIDATE_REQUIRES_SS_AND_BODY_REVIEW_NOT_BUG_OR_SAFETY_PROOF','newAcceptance':False})
 for name,info in sources.items():assert sha(ROOT/name)==info['sha256']
 outcome={'actualExit':parsed.returncode,'source':matrix['source'],'scope':'PARSE_ONLY_EXACT80_MAIN_FILES_NO_ANALYZE_GENERATE_OR_CLASSLOAD_PRODUCT','toolSourceSha256':sha(TOOL),'compiledToolSha256':sha(classes/'SourceJdbcOwnershipInventory.class'),'stages':stages,'parsedSourceFiles':80 if parsed.returncode==0 else None,'candidates':rows,'sourceDisposition':[{'path':p,'candidateIds':[r['candidateId'] for r in rows if r['path']==p],'noCandidateMeansNoJDBCOrNoDefect':False} for p in sorted(sources)],'candidateCount':len(rows),'candidateSourceFiles':len({r['path'] for r in rows}),'notImmediatePatternCount':sum(not r['immediateDirectFinallyPattern'] for r in rows),'sourceFilesWithNoNarrowPatternCandidate':80-len({r['path'] for r in rows}),'uncoveredAcquisitionCandidates':sum(bool(r['missingAcquisitionLineAnchors']) for r in rows),'wholeJDBCOrResourceScopeComplete':False,'actualProductClassLoaded':False,'productTests':0,'coverageAdded':0,'newAcceptance':0,'formalUpdated':False,'rawBusinessOrPrivateOriginalLogsRead':False,'wholeCodeBodiesPublished':False}
 write(OUT,outcome)
 print(json.dumps({'actualExit':parsed.returncode,'sha256':sha(OUT),'parsedSourceFiles':outcome['parsedSourceFiles'],'candidateCount':len(rows),'candidateSourceFiles':outcome['candidateSourceFiles'],'uncoveredAcquisitionCandidates':outcome['uncoveredAcquisitionCandidates'],'notImmediatePatternCount':outcome['notImmediatePatternCount'],'newProductPT':0}))
 raise SystemExit(parsed.returncode)
if __name__=='__main__':main()
