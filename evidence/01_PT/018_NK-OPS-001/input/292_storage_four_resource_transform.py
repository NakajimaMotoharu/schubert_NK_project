"""Four original Test lexical ownership corrections only; no Test compile/run or native work."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';F=B/'evidence/PG22914-storage-four-resource-original-v1';G=B/'evidence/PG22916-storage-four-resource-guard-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());T='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/';NAMES=['OwnedDirectoryFactoryTest.java','StorageRootInspectionTest.java','OwnedTransferDirectoryTest.java']
def one(text,a,b):assert text.count(a)==1,(a,text.count(a));return text.replace(a,b,1)
def method(text,name,end_marker='\n  @Test'):
 a=text.index('void '+name+'(');z=text.index(end_marker,a);return a,z,text[a:z]
def wrap_method(text,name,start_decl,end_marker='\n  @Test'):
 a,z,part=method(text,name,end_marker);part=one(part,start_decl,'try ('+start_decl[:-1]+') {');j=part.rindex('\n  }');part=part[:j]+'\n    }'+part[j:];return text[:a]+part+text[z:]
def transform(name,text):
 if name=='OwnedDirectoryFactoryTest.java':return wrap_method(text,'dirfactory003CloseFailureConsumesDescriptorAndConfiguredRootStillRefusesSlash','var root = OwnedTransferDirectory.openRoot(calls);','\n  private static final class Calls')
 if name=='StorageRootInspectionTest.java':
  a=text.index('DirectoryStream<Path> ordinary =');z=text.index('assertThrows(NullPointerException.class, () -> StorageRootInspection.requireSecureStream(null));',a);part=text[a:z];part=one(part,'DirectoryStream<Path> ordinary =','try (DirectoryStream<Path> ordinary =');part=one(part,'        };\n    assertThrows(','        }) {\n    assertThrows(');part=one(part,'StorageRootInspection.requireSecureStream(ordinary));','StorageRootInspection.requireSecureStream(ordinary));\n    }');return text[:a]+part+text[z:]
 assert name=='OwnedTransferDirectoryTest.java';a,z,part=method(text,'f02ExistingDateIndependentChildLifetimeAndSafeIoFailures');part=one(part,'var parent = OwnedTransferDirectory.open(calls, root);\n    var child = parent.openDate(DATE);','try (var parent = OwnedTransferDirectory.open(calls, root);\n        var child = parent.openDate(DATE)) {');j=part.rindex('\n  }');part=part[:j]+'\n    }'+part[j:];text=text[:a]+part+text[z:];return one(text,'try (var parent = OwnedTransferDirectory.open(calls, root);\n        var executor = Executors.newFixedThreadPool(2)) {\n      var child = parent.openDate(DATE);','try (var parent = OwnedTransferDirectory.open(calls, root);\n        var child = parent.openDate(DATE);\n        var executor = Executors.newFixedThreadPool(2)) {')
def main():
 mode=sys.argv[1];assert mode in ['apply','guard']
 if mode=='apply':
  assert not F.exists();h=B/'input/288_storage_current88.py';s=importlib.util.spec_from_file_location('resource88_freeze',h);lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);base,raw,hashes,previous=lib.current();rp=B/'evidence/PG22910-storage-resource-independent-v1/manifest.json';assert sha(rp)=='184b8b614376f7dfb7df091ef73f851e44a03ac7d409a333954d022be6a8eefb';rm=load(rp);assert rm['inputHashes']==hashes;plan={n:transform(n,(R/(T+n)).read_text()) for n in NAMES};F.mkdir();inputs=[]
  for name in NAMES:
   n=T+name;p=R/n;snap=F/name;snap.write_bytes(p.read_bytes());inputs.append(dict(path=n,sha256=sha(p),snapshotPath=str(snap.relative_to(R))))
  m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputs=inputs,currentInputHashes=hashes,allCurrentRaw=raw,reviewedFindings=previous+rm['reviewedFindings'],baseline=base,reviewManifest=dict(path=str(rp.relative_to(R)),sha256=sha(rp)),productTestsExecuted=0,originalTestsCompiled=False);(F/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
  for item in inputs:
   p=R/item['path'];assert sha(p)==item['sha256'];p.write_text(plan[p.name])
  print('original3 frozen and four ownership scopes source-fixed only');return
 assert not G.exists();m=load(F/'manifest.json');p=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';s=importlib.util.spec_from_file_location('four_resource_token_guard',p);lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);tok=lib.java_tokens;negative=0
 for i in m['inputs']:
  old=R/i['snapshotPath'];assert sha(old)==i['sha256'];expected=transform(old.name,old.read_text());actual=(R/i['path']).read_text();assert tok(actual)==tok(expected);markers=['try (var root ='] if old.name=='OwnedDirectoryFactoryTest.java' else ['try (DirectoryStream<Path> ordinary ='] if old.name=='StorageRootInspectionTest.java' else ['try (var parent = OwnedTransferDirectory.open(calls, root);\n        var child = parent.openDate(DATE)) {','var child = parent.openDate(DATE);\n        var executor = Executors.newFixedThreadPool(2)']
  for marker in markers:assert marker in actual;assert tok(actual.replace(marker,'BROKEN_OWNERSHIP',1))!=tok(expected);negative+=1
 G.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalManifest=dict(path=str((F/'manifest.json').relative_to(R)),sha256=sha(F/'manifest.json')),currentHashes={i['path']:sha(R/i['path']) for i in m['inputs']},correctedOwnershipSites=4,sourceFixedFiles=3,metadataNegativeGuards=negative,productTestsExecuted=0,originalTestsCompiled=False);(G/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,scopes=4,negative=negative)))
if __name__=='__main__':main()
