"""Fixed public encoder binding and single added private failure test; old28 fully preserved."""
from pathlib import Path
import json,hashlib,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33570-admin-encoding29-source-v1';ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());load=lambda p:json.loads(p.read_text());main='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/BootstrapAdminService.java';test=main.replace('/main/','/test/').replace('BootstrapAdminService.java','BootstrapAdminServiceBoundaryTest.java');old=(e/'original-BootstrapAdminService.java.txt').read_text();new=(r/main).read_text();a=new.index('  public BootstrapAdminService()');z=new.index('  public Outcome create(',a);rest=new[:a]+new[z:];rest=rest.replace('import java.util.function.Function;\n','').replace('  private final Function<char[], String> passwords;','  private final PasswordHasher passwords = new PasswordHasher();').replace('hash = passwords.apply(normalized);','hash = passwords.encode(normalized);')
def tokens(s):return [m.group() for m in re.finditer(r'"""[\s\S]*?"""|//[^\n]*|/\*[\s\S]*?\*/|"(?:[^"\\]|\\.)*"|\w+|[^\s]',s) if not m.group().startswith(('//','/*'))]
assert tokens(rest)==tokens(old)
assert all(s in new for s in ['this(new PasswordHasher()::encode);','BootstrapAdminService(Function<char[], String> encoder)','passwords = Objects.requireNonNull(encoder, "encoder");'])
def methods(s):return {m.group(1):m.group(0).strip() for m in re.finditer(r'  @Test\n  void (\w+)\([^\n]*\)[\s\S]*?(?=\n  @Test|\n  private static)',s)}
o=methods((e/'original-BootstrapAdminServiceBoundaryTest.java.txt').read_text());n=methods((r/test).read_text());assert len(o)==18 and len(n)==19 and all(n[k]==v for k,v in o.items())
pf=load(b/'input/3336_admin_manual28_prefix_profile.json');unchanged={}
for path in pf['mainSources']+[x['path'] for x in pf['testSources']]:
 if path in [main,test]:continue
 h=hashlib.sha256(subprocess.check_output(['git','show','1c2738e25b0478d772346c37648fc71515a72018:'+path])).hexdigest();assert ref(r/path)['sha256']==h;unchanged[path]=h
assert len(unchanged)==7
text=(r/test).read_text();assert all(s in text for s in ['new AtomicReference<char[]>()','new BootstrapAdminService(','assertArrayEquals(new char[12], Objects.requireNonNull(observed.get()));','new BootstrapAdminService(null)'])
# Check every explicit production constructor call remains zero-argument, not merely the tested Main.
calls=[]
for p in (r/'src/schubert-nk-api/src/main/java').rglob('*.java'):
 s=p.read_text()
 for m in re.finditer(r'new BootstrapAdminService\s*\(([^)]*)\)',s):assert m.group(1).strip()=='';calls.append(dict(path=str(p.relative_to(r)),offset=m.start(),arguments=0))
assert calls
m=dict(actualExit=0,newMain=ref(r/main),newTest=ref(r/test),originalMain=ref(e/'original-BootstrapAdminService.java.txt'),originalTest=ref(e/'original-BootstrapAdminServiceBoundaryTest.java.txt'),onlyFixedPublicBinderPackagePrivateNonNullPortAndApplyAdded=True,old18BoundaryTestBodiesByteUnchanged=True,oldUnchangedSourceHashes=unchanged,allOther28DefinitionsPreserved=True,productionCallsStillNoarg=calls,providerOrConfigChanged=False,publicNoargDescriptorPreserved=True,independentExpectedNfcUnits=12,callerUnits=24,newDefinitionAdded=1,newDefinitionsTotalGroup=20,wholeExpected=29,mainSources=5,physicalClasses=6,actualDbOrAdminOrNativeOrHeldClasses=0,newAcceptance=0,formalUpdated=False,effortRate=None)
(e/'manifest.json').open('x').write(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=20,whole=29,unchangedSources=7,old18BodiesSame=True,productionNoargCalls=len(calls)))
