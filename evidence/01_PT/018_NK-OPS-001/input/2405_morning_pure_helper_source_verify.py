"""Refactor only pure policy for genuine unit testability; no Root/DB or class initialization."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,os,xml.etree.ElementTree as X
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG29798-morning-pure-helper-source-v1';assert not e.exists();e.mkdir();root=r/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository';main=root/'MorningDatabaseSession.java';helper=root/'MorningSqlFailures.java';test=r/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningSqlFailuresTest.java';old=main.read_text();assert main.read_bytes()==subprocess.check_output(['git','show','cc51f9d7a8c126cf62d4905d082b24cd7ea824b1:'+str(main.relative_to(r))]);(e/'MorningDatabaseSession.before.java.txt').write_text(old)
start=old.index('  private static void preserveCatalogFatal(');end=old.index('  private record RoleObservation',start);oldblock=old[start:end];newblock='''  private static void preserveCatalogFatal(Throwable failure) {
    MorningSqlFailures.preserveCatalogFatal(failure);
  }

  private static boolean closeReplace(@Nullable Throwable primary, Throwable secondary) {
    return MorningSqlFailures.closeReplace(primary, secondary);
  }

''';new=old[:start]+newblock+old[end:];assert new.replace(newblock,oldblock,1)==old
literal=lambda t:re.findall(r'"(?:[^"\\]|\\.)*"',t);assert literal(new)==literal(old);main.write_text(new)
def body(text,name):
 m=re.search(r'(?:void|boolean)\s+'+name+r'\([^)]*\)\s*\{',text);assert m;start=m.end();i=start;depth=1
 while depth:
  c=text[i]
  if c=='{':depth+=1
  elif c=='}':depth-=1
  i+=1
 return text[start:i-1]
normalize=lambda s:re.sub(r'\s+',' ',s).strip();h=helper.read_text()
for name in ['preserveCatalogFatal','closeReplace']:
 former=body(old,name).replace('dev.codex.schubert.nk.storage.StorageIoException.','StorageIoException.');current=body(h,name);current=current.replace('    Objects.requireNonNull(failure, "known catalog failure");\n','').replace('    Objects.requireNonNull(secondary, "cleanup failure");\n','');assert normalize(former)==normalize(current),name
assert len(re.findall(r'^  @Test$',test.read_text(),re.M))==12;tc=r.parent/'toolchain';java=tc/'jdk-25.0.4/bin/java';gjf=tc/'google-java-format-1.36.1-all-deps.jar';cs=tc/'static-gates-20261015/checkstyle-14.3.0-all.jar';fmt=[str(java),'-jar',str(gjf),'--skip-reflowing-long-strings'];commands=[]
for label,args in [('format',fmt+['--replace',str(main),str(helper),str(test)]),('format-check',fmt+['--dry-run','--set-exit-if-changed',str(main),str(helper),str(test)]),('checkstyle',[str(java),'-jar',str(cs),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(e/'checkstyle.xml'),str(main),str(helper),str(test)])]:
 starttime=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (e/(label+'.stdout')).open('xb') as out,(e/(label+'.stderr')).open('xb') as err:
  child=subprocess.Popen(args,cwd=r,stdin=subprocess.DEVNULL,stdout=out,stderr=err);code=child.wait(timeout=180)
 commands.append(dict(label=label,command=args,pid=child.pid,ownerPid=os.getpid(),startUTC=starttime,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actualExit=code));assert code==0
assert not X.parse(e/'checkstyle.xml').findall('.//error');normjava=lambda t:subprocess.check_output(fmt+['-'],input=t.encode());assert main.read_bytes()==normjava(new);assert normjava(new.replace(newblock,oldblock,1))==normjava(old);assert literal(main.read_text())==literal(old)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pd=r/'documents/400_PGPT/470_PMO';ip=pd/'485_WBS網羅性・受入対応.json';a=json.loads(ip.read_text())
for rows in [a['artifacts'],a['currentPhysicalCandidate']['artifacts']]:
 row=next(x for x in rows if x['path']==str(helper.relative_to(r)));assert row['owner']=='WBS-P017-01';row.update(sha256=sha(helper),state='SOURCE_CREATED_PURE12_TEST_DEFINITIONS_NOT_RUN')
ip.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');p=pd/'486_WBS現行実績.json';a=json.loads(p.read_text());a['inventorySha256']=sha(ip);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMainBefore='cc51f9d7a8c126cf62d4905d082b24cd7ea824b1',mainChanges=[str(main.relative_to(r)),str(helper.relative_to(r))],knownPolicyBodiesEqualExceptExplicitInternalNonnullGuards=True,allOtherMorningSourceNormalizedInverseEqual=True,allMorningJavaLiteralsSqlUnchanged=True,existing20CallerOuterFatalPrimaryOwnerLifetimeUnchanged=True,newIndependentTestDefinitions=12,productTestsExecuted=0,coverage=None,sourceGjfCheckstyle0=True,commands=commands,files={str(p.relative_to(r)):sha(p) for p in [main,helper,test]},toolHashes={str(p):sha(p) for p in [java,gjf,cs]},actualDbVmRootNativeKeyPermitActions=0,wholeMorning65Runtime='NOT_RUN_HOLD',pureHelper12Runtime='NOT_RUN_QUALIFICATION_NEXT_SEPARATE_GROUP',formalAcceptanceAdded=0,SS='SSC-341',BUG='BUG-2852');(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('Morning private wrappers retainall20/outer/resourcecode; purepolicy unchanged+nonnullcontract, newwhole12 definitions/GJF-CS0; tests NOT_RUN')
