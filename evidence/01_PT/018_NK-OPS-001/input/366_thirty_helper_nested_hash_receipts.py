"""Follow only the787 already matched public receipts for explicit nested class-hash schemas; metadata only."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';ip=B/'evidence/PG23194-thirty-helper-receipt-audit-v1/manifest.json';O=B/'evidence/PG23202-thirty-helper-nested-hash-schema-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());m=load(ip);assert m['actualExit']==0 and len(m['helperRows'])==30;assert not O.exists();pins=m['sourceHashPins'];fq={}
for helper,h in pins.items():
 text=(R/helper).read_text();assert sha(R/helper)==h;pkg=re.search(r'^package\s+([A-Za-z0-9_.]+)\s*;',text,re.M);assert pkg;fq[helper]=pkg.group(1)+'.'+Path(helper).stem
paths={r['manifest']['path']:r['manifest']['sha256'] for row in m['helperRows'] for r in row['records']};assert len(paths)==787;rows={n:[] for n in pins};FIELDS={'classHashes','compiledTestClasses','classes'}
def maps(v,pointer=''):
 if isinstance(v,dict):
  for k,x in v.items():
   if k in FIELDS and isinstance(x,dict):yield pointer+'/'+k,x
   elif isinstance(x,(dict,list)):yield from maps(x,pointer+'/'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):
   if isinstance(x,(dict,list)):yield from maps(x,pointer+'/'+str(i))
for path,h in paths.items():
 p=R/path;assert sha(p)==h;data=load(p)
 current={row['helper'] for row in m['helperRows'] if any(r['manifest']['path']==path and any(b['currentSourceEqual'] for b in r['sourceBindings']) for r in row['records'])}
 for pointer,values in maps(data):
  for helper in current:
   hits={}
   for key,value in values.items():
    if not isinstance(key,str) or not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):continue
    normalized=key[:-6] if key.endswith('.class') else key;normalized=normalized.replace('/','.')
    if normalized==fq[helper] or normalized.startswith(fq[helper]+'$'):hits[key]=value
   if hits:rows[helper].append(dict(manifest=dict(path=path,sha256=h),field=pointer,declaredExit=data.get('actualExit') if isinstance(data,dict) else None,currentSourceSha256=pins[helper],declaredHashes=hits,compilerOutputOrClasspathBindingNotYetVerified=True))
O.mkdir();result=[dict(helper=n,currentSourceSha256=pins[n],declaredFqnFromSource=fq[n],currentPinNestedClassHashReceipts=rows[n],receiptCount=len(rows[n]),status='CURRENT_SOURCE_WITH_DECLARED_CLASS_HASHES_NEEDS_OUTPUT_BINDING' if rows[n] else 'NO_SUPPORTED_CURRENT_CLASS_HASH_SCHEMA_UNKNOWN_NOT_ABSENT') for n in pins];value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],originalIndex=dict(path=str(ip.relative_to(R)),sha256=sha(ip)),supportedSchemaExtension='Root and nested begin dictionaries, FQN dot or classfile-relative slash keys; explicit64hex values only. Not compiler or runtime qualification.',matchedReceiptCount=787,helperRows=result,helpersWithDeclaredCurrentHashes=sum(bool(rows[n]) for n in pins),helpersWithoutSupportedCurrentHashes=sum(not rows[n] for n in pins),originalTestsCompiled=0,productTestsExecuted=0,actualProductProcessActions=0,binaryFilesRead=0,archivesOrPrivateRawRead=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,declaredHelperHashes=value['helpersWithDeclaredCurrentHashes'],unresolved=value['helpersWithoutSupportedCurrentHashes'],binaryReads=0,UnitReplays=0,manifestSha256=sha(O/'manifest.json'))))
