"""Apply only published SSC441 metadata/HashMap operation, with exact reverse-source proofs."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pub=b/'evidence/PG35802-ssc441-design-main-publication-v1/manifest.json';publication=ld(pub);assert publication['actualExit']==0 and not publication['implementationIncluded'];assert subprocess.run(['git','merge-base','--is-ancestor',publication['designSource'],'origin/main'],check=False).returncode==0
old=ld(b/'input/4188b_inbox_model21_actual15_profile.json');base='2845d357d0e84e3f1a0d735f9fb88592acdeaa87';main='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/InboxException.java';test='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/InboxRequestValueContractTest.java';paths=old['mainSources']+[x['path'] for x in old['testSources']];before={n:(r/n).read_bytes() for n in paths};assert all(v==subprocess.check_output(['git','show',base+':'+n]) for n,v in before.items());w=r.parent/'pgpt-runs/PG379/pg35804-ssc441-inverse';o=b/'evidence/PG35804-ssc441-inbox-reason-source-v1';assert not w.exists() and not o.exists();w.mkdir();o.mkdir();mt=before[main].decode();tt=before[test].decode();old_reason=re.search(r'^  public enum Reason \{[\s\S]*?^  \}',mt,re.M).group(0);old_helper=mt[mt.index('  private static String sqlState('):mt.rfind('\n}')];new_reason='''  public enum Reason {
    MESSAGE_ID_REUSE("23000"),
    OPERATION_TOKEN_REUSE("23000"),
    FINGERPRINT_KEY_UNAVAILABLE("55000"),
    STATE_CORRUPT("XX000"),
    TRANSACTION_REQUIRED("25000");

    private final String retainedSqlState;

    Reason(String sqlState) {
      this.retainedSqlState = sqlState;
    }

    String sqlState() {
      return retainedSqlState;
    }
  }''';new_helper='''  private static String sqlState(Reason reason) {
    return Objects.requireNonNull(reason, "reason").sqlState();
  }''';assert mt.count(old_reason)==mt.count(old_helper)==1;changed=mt.replace(old_reason,new_reason).replace(old_helper,new_helper);old_operation='Map.of(value, "retained").get(equal)';new_operation='new java.util.HashMap<>(Map.of(value, "retained")).get(equal)';assert tt.count(old_operation)==1
(o/'InboxException.before.java.txt').open('wb').write(before[main]);(o/'InboxRequestValueContractTest.before.java.txt').open('wb').write(before[test]);(r/main).write_text(changed);(r/test).write_text(tt.replace(old_operation,new_operation));fmt=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace']
for name in [main,test]:subprocess.run(fmt+[str(r/name)],check=True,timeout=30)
a=(r/main).read_text();current_reason=re.search(r'^  public enum Reason \{[\s\S]*?^  \}',a,re.M).group(0);current_helper=a[a.index('  private static String sqlState('):a.rfind('\n}')];inverse=a.replace(current_reason,old_reason).replace(current_helper,old_helper);tmp=w/'InboxException.java';tmp.write_text(inverse);subprocess.run(fmt+[str(tmp)],check=True,timeout=30);assert tmp.read_bytes()==before[main];(o/'InboxException.inverse.java.txt').open('wb').write(tmp.read_bytes());text=(r/test).read_text();assert text.count(new_operation)==1;tmp=w/'InboxRequestValueContractTest.java';tmp.write_text(text.replace(new_operation,old_operation));subprocess.run(fmt+[str(tmp)],check=True,timeout=30);assert tmp.read_bytes()==before[test];(o/'InboxRequestValueContractTest.inverse.java.txt').open('wb').write(tmp.read_bytes());unchanged={n:sha(r/n) for n in paths if n not in [main,test]};assert all((r/n).read_bytes()==before[n] for n in unchanged);witness=ld(b/'evidence/PG35800-ssc441-inbox-reason-design-only-v1/callers-source-witness.json');assert len(witness['callers'])==11 and all(sha(r/x['path'])==x['sha256'] for x in witness['callers']);v=dict(actualExit=0,designPublication=ref(pub),mainSource=main,fixtureSource=test,beforeMainSha256=hashlib.sha256(before[main]).hexdigest(),afterMainSha256=sha(r/main),beforeFixtureSha256=hashlib.sha256(before[test]).hexdigest(),afterFixtureSha256=sha(r/test),bothInverseFormattedExact=True,otherThirteenMainAndFiveTestFilesByteExact=True,unchangedInputs=unchanged,allOriginalTwentyOneTestIdsInputsExpectedAssertionsRetained=True,onlyFixtureCollectionOperationChanged=True,elevenCallerSourcesUnchanged=True,allPublicTypeAndMemberDescriptorsExpectedUnchanged=True,applicationTestsExecuted=0,whole451Accepted=False);(o/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,mainChanged=1,fixtureOperationChanged=1,inverseExact=True,otherMain13AndTestFiles5Exact=True,originalTests=21,callers11Unchanged=True)))
