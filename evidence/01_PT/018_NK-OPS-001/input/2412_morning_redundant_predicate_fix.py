"""Remove a proved redundant code condition, not a coverage exclusion or changed test oracle."""
from pathlib import Path
import hashlib,json,datetime,subprocess,os,re,xml.etree.ElementTree as X
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG29874-morning-dominated-condition-source-v1';assert not e.exists();e.mkdir();p=r/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningSqlFailures.java';old=p.read_text();mp=b/'evidence/PG29864-morning-pure-sql12-post-v3/manifest.json';m=json.loads(mp.read_text());test=r/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningSqlFailuresTest.java';assert hashlib.sha256(test.read_bytes()).hexdigest()==m['inputHashes'][str(test.relative_to(r))];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['inputHashes'][str(p.relative_to(r))];(e/'MorningSqlFailures.before.java.txt').write_text(old)
a='''    else if ((primary instanceof SQLException || primary instanceof BatchRepositoryException)
        && secondary instanceof SQLException) {
''';z='''    else if (primary instanceof SQLException || primary instanceof BatchRepositoryException) {
''';assert old.count(a)==1;new=old.replace(a,z);assert new.replace(z,a)==old;p.write_text(new)
primary=['NULL','SQL','IO','BATCH','RUNTIME','ERROR'];secondary=['SQL','IO','RUNTIME','ERROR'];expectedReplace=[[True,True,True,True],[False,True,True,True],[False,True,True,True],[False,True,True,True],[False,False,False,False],[False,False,False,False]];expectedGraph=[[False]*4,[True,False,False,False],[False]*4,[True,False,False,False],[False]*4,[False]*4]
def symbolic(pk,sk,old_version):
 known=pk in ['SQL','IO','BATCH']
 if pk=='NULL' or known and sk!='SQL':return True,False
 if not known:return False,False
 guard=pk in ['SQL','BATCH'] and (sk=='SQL' if old_version else True)
 return False,guard
proof=[]
for i,pk in enumerate(primary):
 for j,sk in enumerate(secondary):
  expected=(expectedReplace[i][j],expectedGraph[i][j]);assert symbolic(pk,sk,True)==symbolic(pk,sk,False)==expected;proof.append(dict(primary=pk,secondary=sk,expectedSelectCleanup=expected[0],expectedKnownSqlPairGraph=expected[1],beforeAndAfterEquivalent=True))
tc=r.parent/'toolchain';java=tc/'jdk-25.0.4/bin/java';gjf=tc/'google-java-format-1.36.1-all-deps.jar';cs=tc/'static-gates-20261015/checkstyle-14.3.0-all.jar';fmt=[str(java),'-jar',str(gjf),'--skip-reflowing-long-strings'];commands=[]
for label,args in [('format',fmt+['--replace',str(p)]),('format-check',fmt+['--dry-run','--set-exit-if-changed',str(p)]),('checkstyle',[str(java),'-jar',str(cs),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(e/'checkstyle.xml'),str(p)])]:
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (e/(label+'.stdout')).open('xb') as out,(e/(label+'.stderr')).open('xb') as err:
  child=subprocess.Popen(args,cwd=r,stdin=subprocess.DEVNULL,stdout=out,stderr=err);code=child.wait(timeout=180)
 commands.append(dict(label=label,command=args,pid=child.pid,ownerPid=os.getpid(),startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actualExit=code));assert code==0
assert not X.parse(e/'checkstyle.xml').findall('.//error');normalize=lambda s:subprocess.check_output(fmt+['-'],input=s.encode());assert p.read_bytes()==normalize(new) and normalize(new.replace(z,a))==normalize(old);assert hashlib.sha256(test.read_bytes()).hexdigest()==m['inputHashes'][str(test.relative_to(r))];literals=lambda t:re.findall(r'"(?:[^"\\]|\\.)*"',t);assert literals(old)==literals(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();targets=json.loads((b/'evidence/PG29868-morning-pure-branch-partial-and-sweep-v1/manifest.json').read_text())['targets'];rows=[]
for row in targets:
 q=r/row['path'];current=sha(q)
 if q!=p:assert current==row['sha256']
 rows.append(dict(path=row['path'],beforeSha256=row['sha256'],afterSha256=current,disposition=row['disposition'],changed=q==p))
write=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMainBefore='cc46ac4df68bd3f189f63a75b649e7ead4b7dd12',MainChanged=1,path=str(p.relative_to(r)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=sha(p),oneConjunctionOnlyNormalizedInverseEqual=True,allJavaLiteralsUnchanged=True,independentSymbolicExpectedSource='SS341 literal six-by-four type selection and SQL graph applicability table',symbolicCases=proof,symbolicNotProductPt=True,testsUnchangedSource='733989ec6296f355083cf47ee0ccb2f2392deeb5',testSourceSha256=sha(test),old12ResultsPreserved=True,noCoverageExclusionOrUnreachableWaiver=True,sourceGjfCheckstyle0=True,commands=commands,horizontalTargets=rows,BUG='BUG-2857',YKT='YKT-2406',productTestsExecuted=0,coverage=None,actualDbRootVmNativeKeyAuthorityActions=0,fullNormalRetestPending=True);(e/'manifest.json').write_text(json.dumps(write,ensure_ascii=False,indent=2)+'\n');print('one redundant conjunction removed; fixed12Test bytes; independent24 type cases equivalent; sixYKTtargets reviewed; GJF-CS0, no runtime action')
