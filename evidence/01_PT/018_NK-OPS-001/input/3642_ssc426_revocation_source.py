"""Replace nine exact TWR acquisition scopes with nonnull typed ownership; preserve old8 oracles."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pub=ld(b/'evidence/PG34072-ssc426-design-main-publication-v1/manifest.json');assert pub['actualExit']==0 and pub['ssc']=='SSC426';p=r/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthSessionRevocationService.java';old=p.read_text();assert old.encode()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(r))]);head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();changes=[]
def matching(s,start,left,right):
 depth=0;quoted=False;escaped=False
 for n in range(start,len(s)):
  x=s[n]
  if quoted:
   if escaped:escaped=False
   elif x=='\\':escaped=True
   elif x=='"':quoted=False
  elif x=='"':quoted=True
  elif x==left:depth+=1
  elif x==right:
   depth-=1
   if depth==0:return n
 raise AssertionError('unbalanced exact source')
s=old;counts={'statement':0,'row':0}
while (m:=re.search(r'try \(var (statement|row)\s*=',s)):
 start=m.start();paren=s.index('(',start);end=matching(s,paren,'(',')');brace=s.index('{',end);close=matching(s,brace,'{','}');header=s[paren+1:end];name=m[1];expr=header.split('=',1)[1].strip();body=s[brace+1:close];idx=len(changes)+1;primary='jdbcFailure'+str(idx);method='closeStatement' if name=='statement' else 'closeRows';new='{\nvar '+name+' = requireValue('+expr+');\n@Nullable Throwable '+primary+' = null;\ntry {'+body+'} catch (SQLException | RuntimeException | Error failure) {\n'+primary+' = failure;\nthrow failure;\n} finally {\nJdbcResourceCleanup.'+method+'('+primary+', '+name+');\n}\n}';original=s[start:close+1];changes.append(dict(old=original,new=new));counts[name]+=1;s=s[:start]+new+s[close+1:]
assert counts==dict(statement=5,row=4)
# Restore in reverse order BEFORE formatting: only explicit ownership wrappers differ.
back=s
for change in reversed(changes):assert back.count(change['new'])==1;back=back.replace(change['new'],change['old'],1)
assert back==old;s=s.replace('import dev.codex.schubert.nk.protocol.header.AuthenticationContext;','import dev.codex.schubert.nk.api.database.JdbcResourceCleanup;\nimport dev.codex.schubert.nk.protocol.header.AuthenticationContext;').replace('import java.util.UUID;','import java.util.UUID;\nimport org.jspecify.annotations.Nullable;');p.write_text(s)
test=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/SessionRevocationJdbcPortTest.java';prior=test.read_text();assert prior.count('@Test')==8;original='    try (var workers = Executors.newFixedThreadPool(2)) {';finite='    var workers = Executors.newFixedThreadPool(2);\n    try {';assert prior.count(original)==1;t=prior.replace(original,finite);end=t.rindex('    }\n  }\n}');t=t[:end]+'    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n'+t[end:];t=t.replace('import org.junit.jupiter.api.Test;','import org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;').replace('final class SessionRevocationJdbcPortTest {','@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class SessionRevocationJdbcPortTest {');hooks=[('    String failAt = "";','    String failAt = "";\n    String nullStatementAt = "";\n    String nullRowAt = "";'),('    PreparedStatement statement(String sql) throws SQLException {','    @Nullable PreparedStatement statement(String sql) throws SQLException {'),('      fault(label + ".prepare");','      fault(label + ".prepare");\n      if (label.equals(nullStatementAt)) return null;'),('    ResultSet row(String label, String name) {','    @Nullable ResultSet row(String label, String name) {\n      if (label.equals(nullRowAt)) return null;')]
for a,z in hooks:assert t.count(a)==1;t=t.replace(a,z)
newtests='''
  @Test
  void resource001NullStatementsFailClosedForLogoutAndAdministrativeRevocation() throws Exception {
    for (boolean admin : new boolean[] {false, true}) {
      for (String label : admin ? List.of(T, A, X, L) : List.of(U, S, X, L)) {
        Fixture f = new Fixture();
        f.nullStatementAt = label;
        infra(f, admin);
        assertEquals(label, f.order.getLast());
      }
    }
  }

  @Test
  void resource002NullRowsStillCloseTheirOwnedStatementExactlyOnce() throws Exception {
    for (boolean admin : new boolean[] {false, true}) {
      for (String label : admin ? List.of(T, A) : List.of(U, S)) {
        Fixture f = new Fixture();
        f.nullRowAt = label;
        infra(f, admin);
        assertEquals(label, f.order.getLast());
      }
    }
  }
''';t=t.rstrip()[:-1]+newtests+'}\n';test.write_text(t);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p),str(test)],check=True,timeout=30)
current=test.read_text();inv=current[:current.index('  @Test\n  void resource001')].rstrip()+'\n}\n';inv=inv.replace('import org.junit.jupiter.api.Timeout;\n','').replace('@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\n','').replace('    var workers = Executors.newFixedThreadPool(2);\n    try {',original).replace('    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n','    }\n',1)
# The replacement above already supplies the original closing brace.
inv=inv.replace('    }\n    }\n  }\n}', '    }\n  }\n}')
for a,z in reversed(hooks):assert inv.count(z)==1;inv=inv.replace(z,a)
formatted=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert formatted.returncode==0 and formatted.stdout==prior.encode();assert re.findall(r'"(?:[^"\\]|\\.)*"',old)==re.findall(r'"(?:[^"\\]|\\.)*"',p.read_text())
security=['AuthSessionRevocationService','RevokedContext','AuthenticatedActor','AuthorizationService','AuthorizationException','AuthContextIdentity','SessionRevocationReason','SessionAuditWriter','ContextHash','AuthenticationInfrastructureException','AuthenticationContextException','package-info'];main=['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/'+x+'.java' for x in security]+['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/'+x+'.java' for x in ['RequiredColumn','JdbcResourceCleanup','package-info']]+['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/domain/'+x+'.java' for x in ['Role','package-info']];assert len(main)==17
sdk=ld(b/'evidence/PG34030-ssc425-source-binding-v1/manifest.json')['sdkHashes'];out=b/'evidence/PG34074-ssc426-source-oracle-inverse-v1';out.mkdir();v=dict(actualExit=0,sourceBefore=head,designPublication=pub,mainSources=main,testSources=[dict(path=str(test.relative_to(r)),tests=10)],inputHashes={n:sha(r/n) for n in main+[str(test.relative_to(r))]},sdkHashes=sdk,mainOwnershipWrapperInverseBeforeFormattingExact=True,resourceScopes=counts,originalEightAssertionsInverseFormattedExact=True,oldTestSha256=hashlib.sha256(prior.encode()).hexdigest(),mainLiteralSequenceExact=True,newDefinitions=2,necessaryPriorDefinitions=8,expectedTests=10,targets=['dev/codex/schubert/nk/api/security/AuthSessionRevocationService'],memoryProxyOnly=True,actualDbFixtureNotCopiedOrExtracted=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=17,resourceScopes=counts,old8InverseExact=True,tests=10)))
