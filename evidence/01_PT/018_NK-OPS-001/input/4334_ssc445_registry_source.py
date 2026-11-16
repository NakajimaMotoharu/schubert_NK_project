"""Apply published cache ownership/private binding design and invert all registration/body changes exactly."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();ref=lambda x:dict(path=str(x.relative_to(r)),sha256=sha(x));pubp=b/'evidence/PG36242-ssc445-design-main-publication-v1/manifest.json';pub=ld(pubp);assert pub['actualExit']==0 and not pub['implementationIncluded'];subprocess.run(['git','merge-base','--is-ancestor',pub['designSource'],'origin/main'],check=True);module=r/'src/schubert-nk-protocol';mains=sorted(module.joinpath('src/main/java').rglob('*.java'));tests=sorted(module.joinpath('src/test/java').rglob('*.java'));resources=sorted(module.joinpath('src/test/resources/protocol').glob('*.tsv'));assert len(mains)==165 and len(tests)==33 and len(resources)==5;main='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog.java';newtest='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalogStateContractTest.java';oldhead=ld(b/'input/4332_ssc445_registry_start.json')['source'];before={str(p.relative_to(r)):p.read_bytes() for p in mains+tests+resources if str(p.relative_to(r))!=newtest};assert all(v==subprocess.check_output(['git','show',('de22e9c0210bd82702795a7d5d0d96b6e5577128' if '/src/main/java/' in n else oldhead)+':'+n]) for n,v in before.items());original=before[main].decode();at=original.index('  private record Mapping(');end=original.rfind('}');records=original[at:end];holder='''  // SSC445_PRIVATE_BINDINGS_BEGIN
  private static final class Mapping {
    private final Class<? extends PayloadData> declaredDataType;
    private final Function<FieldValueSet, ? extends PayloadData> decoderFunction;
    private final Optional<RecordMapping> repeatingBinding;

    private Mapping(
        Class<? extends PayloadData> dataType,
        Function<FieldValueSet, ? extends PayloadData> dataDecoder,
        Optional<RecordMapping> recordMapping) {
      this.declaredDataType = dataType;
      this.decoderFunction = dataDecoder;
      this.repeatingBinding = recordMapping;
    }

    private Class<? extends PayloadData> dataType() {
      return declaredDataType;
    }

    private Function<FieldValueSet, ? extends PayloadData> dataDecoder() {
      return decoderFunction;
    }

    private Optional<RecordMapping> recordMapping() {
      return repeatingBinding;
    }
  }

  private static final class RecordMapping {
    private final Class<? extends PayloadRecord> declaredRecordType;
    private final Function<FieldValueSet, ? extends PayloadRecord> decodeRecord;

    private RecordMapping(
        Class<? extends PayloadRecord> recordType,
        Function<FieldValueSet, ? extends PayloadRecord> recordDecoder) {
      this.declaredRecordType = recordType;
      this.decodeRecord = recordDecoder;
    }

    private Class<? extends PayloadRecord> recordType() {
      return declaredRecordType;
    }

    private Function<FieldValueSet, ? extends PayloadRecord> recordDecoder() {
      return decodeRecord;
    }
  }
  // SSC445_PRIVATE_BINDINGS_END
''';new=original[:at]+holder+original[end:];olddecl='  private static final Map<String, Mapping> STANDARD =';newdecl='  private static final PayloadTypeCatalog INSTANCE = new PayloadTypeCatalog();\n\n  private final Map<String, Mapping> standard =';assert new.count(olddecl)==1;new=new.replace(olddecl,newdecl).replace('Mapping mapping = STANDARD.get(layoutId.value());','Mapping mapping = INSTANCE.standard.get(layoutId.value());');new,count=re.subn(r'mapping\(\s*"([A-Z0-9]{8})",\s*','mapping(',new);assert count==64;assert new.count('      String layoutId,\n')==2;new=new.replace('      String layoutId,\n','');new,count=re.subn(r'new Mapping\(\s*layoutId,\s*','new Mapping(',new);assert count==2;o=b/'evidence/PG36244-ssc445-registry-source-v1';w=r.parent/'pgpt-runs/PG379/pg36244-registry-inverse';assert not o.exists() and not w.exists();o.mkdir();w.mkdir();(o/'PayloadTypeCatalog.before.java.txt').open('xb').write(before[main]);(r/main).write_text(new);fmt=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace']
for path in [r/main,r/newtest]:subprocess.run(fmt+[str(path)],check=True,timeout=30)
current=(r/main).read_text();inverse,n=re.subn(r'  // SSC445_PRIVATE_BINDINGS_BEGIN\n.*?  // SSC445_PRIVATE_BINDINGS_END\n',records,current,flags=re.S);assert n==1 and inverse.count(newdecl)==1;inverse=inverse.replace(newdecl,olddecl).replace('Mapping mapping = INSTANCE.standard.get(layoutId.value());','Mapping mapping = STANDARD.get(layoutId.value());');inverse,n=re.subn(r'(Map\.entry\(\s*"([A-Z0-9]{8})",\s*mapping\()\s*',lambda m:m.group(1)+'"'+m.group(2)+'", ',inverse);assert n==64;inverse,n=re.subn(r'(private static Mapping mapping\()\s*',r'\1\n      String layoutId,\n      ',inverse);assert n==2;inverse,n=re.subn(r'new Mapping\(\s*','new Mapping(layoutId, ',inverse);assert n==2;tmp=w/'PayloadTypeCatalog.java';tmp.write_text(inverse);subprocess.run(fmt+[str(tmp)],check=True,timeout=30);assert tmp.read_bytes()==before[main];(o/'PayloadTypeCatalog.inverse.java.txt').open('xb').write(tmp.read_bytes());assert all((r/n).read_bytes()==v for n,v in before.items() if n!=main)
def entries(text):
 result=[]
 for match in re.finditer(r'Map\.entry\(\s*"([A-Z0-9]{8})",\s*mapping\((.*?)\)\s*\)',text,re.S):
  types=re.findall(r'([A-Za-z0-9_]+)\.class',match.group(2));assert len(types) in [1,2];result.append((match.group(1),types[0],types[1] if len(types)==2 else '-'))
 return result
oldentries=entries(original);newentries=entries(current);assert len(oldentries)==64 and oldentries==newentries;table=r/'src/schubert-nk-protocol/src/test/resources/protocol/named-types-ss323.tsv';expected=[tuple(line.split('\t')) for line in table.read_text().splitlines() if line and not line.startswith('#')];assert len(expected)==64 and {x[0]:x[1:] for x in expected}=={x[0]:x[1:] for x in newentries};assert re.findall(r'\b[A-Za-z0-9_]+::from',original)==re.findall(r'\b[A-Za-z0-9_]+::from',current);wi=b/'evidence/PG36240-ssc445-registry-design-only-v1/all-callers-source-witness.json';witness=ld(wi);assert len(witness['callers'])==37 and all(sha(r/x['path'])==x['sha256'] for x in witness['callers']);v=dict(actualExit=0,designPublication=ref(pubp),mainSource=main,beforeMainSha256=hashlib.sha256(before[main]).hexdigest(),afterMainSha256=sha(r/main),inverseAllBodyRegistrationDiagnosticsFormattedExact=True,all64EntryOrderAndKeyTypeBindingsExact=True,independentNamedTypeTable=ref(table),allDecoderReferencesExact=True,other164MainAnd32Test5ResourcesUnchanged=True,otherSourceHashes={n:sha(r/n) for n in before if n!=main},all37CallerSourcesUnchanged=True,callerWitness=ref(wi),privateBindingValueApiNotExposed=True,newTest=ref(r/newtest),newDefinitions=1,independentConcurrentReaderObservations=128,observationsAreNotTestCount=True,applicationTestsExecuted=0,publicAbiEqualityStillRequired=True,whole451Accepted=False);(o/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,mainChanged=1,inverseExact=True,registryRows64Exact=True,other164Main32Test5ResourcesExact=True,all37CallersUnchanged=True,newDefinitions=1)))
