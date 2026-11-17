"""Public ABI exact; retain every old private member and add only the two declared typed closes."""
from pathlib import Path
import datetime,hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));op=b/'evidence/PG37374-summary-four-main-compile-v1/manifest.json';np=b/'evidence/PG37390-summary-four-main-compile-v2/manifest.json';old=ld(op);new=ld(np);assert old['actualExit']==new['actualExit']==0;target='dev/codex/schubert/nk/batch/repository/InspectionSummaryRepository.class';changed={m:[n for n,h in rows.items() if h!=old['physicalClassHashes'][m].get(n)] for m,rows in new['physicalClassHashes'].items()};assert [n for rows in changed.values() for n in rows]==[target];assert all(set(new['physicalClassHashes'][m])==set(old['physicalClassHashes'][m]) for m in changed)
out=b/'evidence/PG37396-summary23-abi-physical-v1';assert not out.exists();out.mkdir();texts={};commands={}
for label,c in [('old',old),('new',new)]:
 p=Path(c['cwd'])/'src/schubert-nk-batch/target/classes'/target;assert sha(p)==c['physicalClassHashes']['batch'][target]
 for flag in ['-public','-p']:
  cmd=[str(tc/'jdk-25.0.4/bin/javap'),flag,'-s',str(p)];x=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert x.returncode==0 and not x.stderr;key=label+flag;(out/(key+'.stdout')).write_text(x.stdout);texts[(label,flag)]=[z.strip() for z in x.stdout.splitlines() if z.strip()];commands[key]=dict(command=cmd,actualExit=x.returncode)
assert texts[('old','-public')]==texts[('new','-public')]
expected=[['private static void closeRow(java.sql.ResultSet, java.lang.Throwable) throws java.sql.SQLException;','descriptor: (Ljava/sql/ResultSet;Ljava/lang/Throwable;)V'],['private static void closeStatement(java.sql.PreparedStatement, java.lang.Throwable) throws java.sql.SQLException;','descriptor: (Ljava/sql/PreparedStatement;Ljava/lang/Throwable;)V']];filtered=list(texts[('new','-p')])
for declaration,descriptor in expected:
 assert filtered.count(declaration)==1;index=filtered.index(declaration);assert filtered[index+1]==descriptor;del filtered[index:index+2]
assert filtered==texts[('old','-p')]
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=new['sourceCore'],oldSourceCore=old['sourceCore'],oldCompile=ref(op),newCompile=ref(np),physicalUniverse=1101,changedPhysical=changed,changedPhysicalCount=1,unchangedPhysicalCount=1100,publicAbiExact=True,allOldPrivateSignaturesPreserved=True,onlyAddedPrivateMethods=expected,privateAdditionCount=2,stages=commands,productTestsExecuted=0,oldSourceExecTransferred=False,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,changed1=True,unchanged1100=True,publicAbiExact=True,oldPrivatePreserved=True,privateAdded2=True)))
