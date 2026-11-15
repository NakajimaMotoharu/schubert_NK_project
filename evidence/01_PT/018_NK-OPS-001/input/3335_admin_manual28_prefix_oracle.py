"""SSC412 static transformation/oracle provenance; no original DB/Main or provider operation."""
from pathlib import Path
import json,hashlib,re,textwrap,collections,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33526-admin-manual28-source-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));base='src/schubert-nk-api/src/';service=base+'main/java/dev/codex/schubert/nk/api/application/admin/BootstrapAdminService.java';boundary=service.replace('/main/','/test/').replace('BootstrapAdminService.java','BootstrapAdminServiceBoundaryTest.java');hasher=base+'main/java/dev/codex/schubert/nk/api/security/PasswordHasher.java';ht=hasher.replace('/main/','/test/').replace('.java','Test.java');oldservice=(e/'original-BootstrapAdminService.java.txt').read_text();news=(r/service).read_text()
def strings(s):
 result=[]
 for m in re.finditer(r'"""[\s\S]*?"""|"(?:[^"\\]|\\.)*"',s):
  v=m.group();v=textwrap.dedent(v[3:-3]).removeprefix('\n') if v.startswith('"""') else json.loads(v)
  if v.strip().lower().startswith(('select ','lock table ','insert ')):result.append(re.sub(r'\s+',' ',v).strip())
 return collections.Counter(result)
assert strings(oldservice)==strings(news) and len(strings(news))==6
assert not re.search(r'\btry\s*\(',news) and all(s in news for s in ['if (primary == null) throw failure;','if (primary != failure) primary.addSuppressed(failure);','RESULT_VOID = 0','RESULT_GRANTED = 1','RESULT_EXISTS = 2','RESULT_ID = 3','MAXIMUM_USER_ID = 999_999_999_999L','read(statement, RESULT_ID)','Arrays.fill(password,','Objects.requireNonNull(password, "password")'])
assert news.count('catch (SQLException | RuntimeException | Error failure)')==7 and news.count('closeStatement(statement, primary);')==4 and news.count('closeResult(result, primary);')==1
oldh=(e/'original-PasswordHasher.java.txt').read_text();newh=(r/hasher).read_text();a=oldh.index('  public PasswordHasher() {');z=oldh.index('\n  /**',a);aa=newh.index('  public PasswordHasher() {');zz=newh.index('\n  /**\n   * Caller must',aa);assert oldh[:a]+oldh[z:]==newh[:aa]+newh[zz:]
assert all(s in newh for s in ['this(defaultEncoder());','PasswordHasher(PasswordEncoder encoder)','Objects.requireNonNull(encoder, "encoder")','return new DelegatingPasswordEncoder("pbkdf2-v1", Map.of("pbkdf2-v1", v1));'])
def methods(s):return {m.group(1):m.group(0).strip() for m in re.finditer(r'  @Test\n  void (\w+)\([^\n]*\)[\s\S]*?(?=\n  @Test|\n  private static)',s)}
oldb=methods((e/'original-BootstrapAdminServiceBoundaryTest.java.txt').read_text());newb=methods((r/boundary).read_text());assert len(oldb)==len(newb)==18
same=[k for k in oldb if not k.startswith('bootbound016')];assert len(same)==17 and all(newb[k]==oldb[k] for k in same)
o=methods((e/'original-PasswordHasherTest.java.txt').read_text());n=methods((r/ht).read_text());assert len(o)==3 and len(n)==4 and all(n[k]==v for k,v in o.items())
old={}
for path in [base+'main/java/dev/codex/schubert/nk/api/security/'+s+'.java' for s in ['PasswordPolicy','LoginUsername']]+[service.replace('BootstrapAdminService','UserCommandMetadata')]+[base+'test/java/dev/codex/schubert/nk/api/security/'+s+'Test.java' for s in ['PasswordPolicy','LoginUsername']]:
 h=hashlib.sha256(subprocess.check_output(['git','show','23bb667e26cb7e879a5d2d07589fc7e3ba723745:'+path])).hexdigest();assert sha(r/path)==h;old[path]=h
for p in [r/service,r/hasher,r/boundary,r/ht]:assert b'\x00' not in p.read_bytes()
text=(r/ht).read_text();assert all(s in text for s in ['AtomicReference<CharSequence>','new AssertionError("synthetic encoder fault")','new IllegalStateException("synthetic encoder fault")','Objects.requireNonNull(observed.get()).toString()','new PasswordHasher(null)'])
originalRaw=load(b/'evidence/PG33514-admin-boundary27-unfiltered-measurement-v6/manifest.json');assert not originalRaw['rawFour100']
m=dict(actualExit=0,sourceInputs=[ref(r/p) for p in [service,hasher,boundary,ht]],originalSnapshots=[ref(e/('original-'+Path(p).name+'.txt')) for p in [service,hasher,boundary,ht]],allSixSqlLiteralsAndNormalBindingsPreserved=True,sqlValues=dict(strings(news)),manualCleanupPrimarySecondaryAndSelfIdentity=True,borrowedConnectionOwnerPreserved=True,publicHashCtorPinnedSameFactory=True,allFourOriginalHasherNonConstructorMethodsByteUnchanged=True,old17BoundaryTestBodiesUnchanged=True,original3HasherTestBodiesUnchanged=True,oldUnchangedSourceHashes=old,independentJcaOraclePreserved=True,newRuntimeAndErrorEncoderFailureTests=True,originalUnqualifiedRaw=ref(b/'evidence/PG33514-admin-boundary27-unfiltered-measurement-v6/manifest.json'),original27NotCountedQualified=True,newDefinitionAddedThisSupplement=1,newDefinitionsTotalGroup=19,wholeExpected=28,mainSources=5,physicalClasses=6,providerOrBackendOrAuthorityOrHeldClasses=0,newAcceptance=0,formalAccepted=False,effortRate=None)
(e/'hash-prefix-corrected-manifest.json').open('x').write(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,sql6Unchanged=True,new=19,all=28,main=5,physical=6))
