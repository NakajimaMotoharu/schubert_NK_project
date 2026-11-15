"""Exact ownership transformation and independent null-vector additions to original API Memory16."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pub=ld(b/'evidence/PG34302-ssc429-design-main-publication-v1/manifest.json');assert pub['actualExit']==0 and pub['ssc']=='SSC429';head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
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
 raise AssertionError('unbalanced source')
counts={};inverses={}
for name,expected in [('LoginAttemptRepository',dict(statement=5,row=2)),('LoginAuditWriter',dict(statement=1,row=0))]:
 p=r/('src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/'+name+'.java');old=p.read_text();assert old.encode()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(r))]);s=old;changes=[];counter=dict(statement=0,row=0)
 while (m:=re.search(r'try \(var (statement|row)\s*=',s)):
  start=m.start();paren=s.index('(',start);end=matching(s,paren,'(',')');brace=s.index('{',end);close=matching(s,brace,'{','}');kind=m[1];expr=s[paren+1:end].split('=',1)[1].strip();assert ';' not in expr;body=s[brace+1:close];primary='jdbcFailure'+str(len(changes)+1);method='closeStatement' if kind=='statement' else 'closeRows';new='{\nvar '+kind+' = requireValue('+expr+');\n@Nullable Throwable '+primary+' = null;\ntry {'+body+'} catch (SQLException | RuntimeException | Error failure) {\n'+primary+' = failure;\nthrow failure;\n} finally {\nJdbcResourceCleanup.'+method+'('+primary+', '+kind+');\n}\n}';prior=s[start:close+1];changes.append(dict(old=prior,new=new));s=s[:start]+new+s[close+1:];counter[kind]+=1
 assert counter==expected;back=s
 for change in reversed(changes):assert back.count(change['new'])==1;back=back.replace(change['new'],change['old'],1)
 assert back==old
 if 'import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;' not in s:s=s.replace('import com.google.gson.JsonObject;','import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;\n\nimport com.google.gson.JsonObject;')
 first=s.index('\nimport ',s.index('import static')+10);s=s[:first]+s[first:].replace('\nimport ','\nimport dev.codex.schubert.nk.api.database.JdbcResourceCleanup;\nimport ',1);s=s.replace('\n/**','\nimport org.jspecify.annotations.Nullable;\n\n/**',1);assert re.findall(r'"(?:[^"\\]|\\.)*"',old)==re.findall(r'"(?:[^"\\]|\\.)*"',s);p.write_text(s);counts[name]=counter;inverses[name]=True
p=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationServiceMemoryPortTest.java';old=p.read_text();assert old.count('@Test')==16;pool='    try (Fixture first = new Fixture();\n        Fixture second = new Fixture();\n        var executor = Executors.newFixedThreadPool(2)) {';finite='    Fixture first = new Fixture();\n    Fixture second = new Fixture();\n    var executor = Executors.newFixedThreadPool(2);\n    try {';assert old.count(pool)==1;s=old.replace(pool,finite);end=s.index('\n  private static void expectStorageFailure');prefix=s[:end];closing='    }\n  }\n';assert prefix.endswith(closing);cleanup='    } finally {\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n      try {\n        first.close();\n      } finally {\n        second.close();\n      }\n    }\n  }\n';s=prefix[:-len(closing)]+cleanup+s[end:];s=s.replace('import org.junit.jupiter.api.Test;','import org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;').replace('final class AuthenticationServiceMemoryPortTest {','@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class AuthenticationServiceMemoryPortTest {');hooks=[('    Optional<Fault> fault = Optional.empty();','    Optional<Fault> fault = Optional.empty();\n    Optional<Stage> nullStatementAt = Optional.empty();\n    Optional<Stage> nullRowsAt = Optional.empty();\n    final List<Stage> prepareAttempts = new ArrayList<>();'),('    PreparedStatement prepare(String sql) throws SQLException {','    org.jspecify.annotations.Nullable PreparedStatement prepare(String sql) throws SQLException {'),('      inject(stage, Site.PREPARE);','      inject(stage, Site.PREPARE);\n      prepareAttempts.add(stage);\n      if (nullStatementAt.filter(value -> value == stage).isPresent()) return null;'),('                      Cursor cursor = new Cursor(stage, rows());','                      if (nullRowsAt.filter(value -> value == stage).isPresent()) yield null;\n                      Cursor cursor = new Cursor(stage, rows());')]
for a,z in hooks:assert s.count(a)==1;s=s.replace(a,z)
newtests='''
  @Test
  void resource017AllLoginStatementsRejectNullAndConsumePassword() throws Exception {
    List<Stage> route = List.of(Stage.USER, Stage.CREATE_IP, Stage.IP, Stage.UPDATE_USER,
        Stage.UPDATE_IP, Stage.SESSION_USER, Stage.SESSION_INSERT, Stage.SESSION_ACTIVE, Stage.LOGIN_AUDIT);
    for (Stage stage : List.of(Stage.USER, Stage.CREATE_IP, Stage.IP, Stage.UPDATE_USER, Stage.UPDATE_IP, Stage.LOGIN_AUDIT)) {
      try (Fixture f = new Fixture()) {
        f.nullStatementAt = Optional.of(stage);
        expectStorageFailure(f::call);
        int stop = route.indexOf(stage);
        assertEquals(route.subList(0, stop + 1), f.prepareAttempts);
        assertEquals(route.subList(0, stop), f.stages());
        f.verifyReleasedAndConsumed();
      }
    }
  }

  @Test
  void resource018BothLoginNullRowsCloseTheirOwnedStatement() throws Exception {
    for (Stage stage : List.of(Stage.USER, Stage.IP)) {
      try (Fixture f = new Fixture()) {
        f.nullRowsAt = Optional.of(stage);
        expectStorageFailure(f::call);
        assertEquals(stage, f.prepareAttempts.getLast());
        assertEquals(stage == Stage.USER ? List.of(Stage.USER) : List.of(Stage.USER, Stage.CREATE_IP, Stage.IP), f.stages());
        assertTrue(f.statements.getLast().cursors.isEmpty());
        f.verifyReleasedAndConsumed();
      }
    }
  }
''';s=s.rstrip()[:-1]+newtests+'}\n';s=s.replace('    org.jspecify.annotations.Nullable PreparedStatement','    @org.jspecify.annotations.Nullable PreparedStatement');p.write_text(s);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];mains=[r/('src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/'+n+'.java') for n in counts];subprocess.run(formatter+['--replace',*map(str,mains),str(p)],check=True,timeout=30);inv=p.read_text();inv=inv[:inv.index('  @Test\n  void resource017')].rstrip()+'\n}\n';inv=inv.replace('import org.junit.jupiter.api.Timeout;\n','').replace('@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\n','').replace(finite,pool).replace(cleanup,closing,1)
for a,z in reversed(hooks):
 if z.startswith('    org.jspecify'):z=z.replace('    org.jspecify','    @org.jspecify')
 assert inv.count(z)==1,(a,z);inv=inv.replace(z,a)
formatted=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert formatted.returncode==0 and formatted.stdout==old.encode()
scope=ld(r/'evidence/01_PT/007_NK-AUT-001/input/017_authentication_memory_port_scope.json');main=[x for x in scope['mainPaths'] if '/schubert-nk-api/' in x]+['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/JdbcResourceCleanup.java'];sdk=scope['sdkDependencies'];sdk.update(ld(b/'evidence/PG34244-ssc428-source-oracle-inverse-v1/manifest.json')['sdkHashes']);out=b/'evidence/PG34304-ssc429-source-oracle-inverse-v1';out.mkdir();v=dict(actualExit=0,sourceBefore=head,designPublication=pub,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=18)],inputHashes={x:sha(r/x) for x in main+[str(p.relative_to(r))]},sdkHashes=sdk,resourceScopes=counts,mainOwnershipInverseExact=inverses,originalSixteenAssertionsInverseFormattedExact=True,oldTestSha256=hashlib.sha256(old.encode()).hexdigest(),newDefinitions=2,necessaryPriorDefinitions=16,expectedTests=18,targets=['dev/codex/schubert/nk/api/security/'+n for n in ['AuthenticationService','LoginAttemptRepository','LoginAuditWriter']],memoryProxyOnly=True,realDbFixtureNotCopied=True,defaultPasswordMatcherNotInvoked=True,ownSyntheticUnissuedCrypto=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=len(main),original16InverseExact=True,tests=18,resources=counts)))
