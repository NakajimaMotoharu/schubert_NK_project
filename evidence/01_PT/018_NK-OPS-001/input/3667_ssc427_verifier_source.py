"""Exact verifier ownership wrappers, invariant private carrier and original6 oracle inverse."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pub=ld(b/'evidence/PG34142-ssc427-design-main-publication-v1/manifest.json');assert pub['actualExit']==0 and pub['ssc']=='SSC427';p=r/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticationContextVerifier.java';old=p.read_text();assert old.encode()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(r))]);head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();changes=[]
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
s=old;counts={'statement':0,'row':0}
while (m:=re.search(r'try \((?:var|ResultSet) (statement|row)\s*=',s)):
 start=m.start();paren=s.index('(',start);end=matching(s,paren,'(',')');brace=s.index('{',end);close=matching(s,brace,'{','}');header=s[paren+1:end];name=m[1];expr=header.split('=',1)[1].strip();body=s[brace+1:close];primary='jdbcFailure'+str(len(changes)+1);method='closeStatement' if name=='statement' else 'closeRows';new='{\nvar '+name+' = requireValue('+expr+');\n@Nullable Throwable '+primary+' = null;\ntry {'+body+'} catch (SQLException | RuntimeException | Error failure) {\n'+primary+' = failure;\nthrow failure;\n} finally {\nJdbcResourceCleanup.'+method+'('+primary+', '+name+');\n}\n}';original=s[start:close+1];changes.append(dict(old=original,new=new));counts[name]+=1;s=s[:start]+new+s[close+1:]
assert counts==dict(statement=3,row=2);back=s
for change in reversed(changes):assert back.count(change['new'])==1;back=back.replace(change['new'],change['old'],1)
assert back==old
oldcarrier='  private record VerifiedSession(UUID id, AuthenticatedActor actor) {}';assert s.count(oldcarrier)==1;carrier='''  private static final class VerifiedSession {
    private final UUID id;
    private final AuthenticatedActor actor;

    private VerifiedSession(UUID id, AuthenticatedActor actor) {
      this.id = Objects.requireNonNull(id, "id");
      this.actor = Objects.requireNonNull(actor, "actor");
    }

    private UUID id() {
      return id;
    }

    private AuthenticatedActor actor() {
      return actor;
    }
  }''';s=s.replace(oldcarrier,carrier).replace('import dev.codex.schubert.nk.api.domain.Role;','import dev.codex.schubert.nk.api.database.JdbcResourceCleanup;\nimport dev.codex.schubert.nk.api.domain.Role;').replace('import java.sql.ResultSet;\n','').replace('import java.util.UUID;','import java.util.UUID;\nimport org.jspecify.annotations.Nullable;');p.write_text(s)
test=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationVerifierJdbcPortTest.java';prior=test.read_text();assert prior.count('@Test')==6;poolOld='    try (var executor = Executors.newFixedThreadPool(2)) {';poolNew='    var executor = Executors.newFixedThreadPool(2);\n    try {';assert prior.count(poolOld)==1;t=prior.replace(poolOld,poolNew);end=t.rindex('    }\n  }\n}');t=t[:end]+'    } finally {\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n'+t[end:];t=t.replace('import org.junit.jupiter.api.Test;','import org.jspecify.annotations.Nullable;\nimport org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;').replace('final class AuthenticationVerifierJdbcPortTest {','@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class AuthenticationVerifierJdbcPortTest {');nameLine='      String name = actual.equals(USER_LOCK) ? "user" : actual.equals(TOUCH) ? "touch" : "session";';assert t.count(nameLine)==1
hooks=[('    final Map<String, Object> fields = new HashMap<>();','    final Map<String, @Nullable Object> fields = new HashMap<>();'),('    final List<String> closes = new ArrayList<>();','    final List<String> closes = new ArrayList<>();\n    final List<String> acquired = new ArrayList<>();'),('    String failMethod = "";','    String failMethod = "";\n    String nullStatementAt = "";\n    String nullRowAt = "";'),('    RuntimeException runtimeFailure;','    @Nullable RuntimeException runtimeFailure;'),('    PreparedStatement statement(String actual) {','    @Nullable PreparedStatement statement(String actual) {'),(nameLine,nameLine+'\n      if (actual.equals(nullStatementAt)) return null;\n      acquired.add(name + ".statement");'),('    ResultSet row(String name) {','    @Nullable ResultSet row(String name) {\n      if (name.equals(nullRowAt)) return null;\n      acquired.add(name + ".row");')]
for a,z in hooks:assert t.count(a)==1;t=t.replace(a,z)
owned='''
    void owned() {
      assertEquals(0, forbiddenOwnerCalls);
      assertEquals(acquired.size(), closes.size());
      for (String name : acquired) assertEquals(1, closes.stream().filter(name::equals).count());
    }
''';marker='  }\n\n  private static void fixedInfrastructure';assert t.count(marker)==1;t=t.replace(marker,owned+marker);newtests='''
  @Test
  void resource001NullStatementsFailClosedBeforeAnyLaterStatement() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      for (String sql : inspect ? List.of(READ) : List.of(USER_LOCK, SESSION_LOCK, TOUCH)) {
        var f = new Fixture();
        f.readOnly = inspect;
        f.nullStatementAt = sql;
        fixedInfrastructure(() -> { if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW); else verifier.verify(f.connection(), INPUT, NOW); });
        assertEquals(sql, f.sql.getLast());
        f.owned();
      }
    }
  }

  @Test
  void resource002NullRowsCloseOnlyThePreviouslyAcquiredResourcesExactlyOnce() throws Exception {
    var verifier = new AuthenticationContextVerifier(new ContextHash());
    for (boolean inspect : List.of(false, true)) {
      for (String label : inspect ? List.of("session") : List.of("user", "session")) {
        var f = new Fixture();
        f.readOnly = inspect;
        f.nullRowAt = label;
        fixedInfrastructure(() -> { if (inspect) verifier.inspectReadOnly(f.connection(), INPUT, NOW); else verifier.verify(f.connection(), INPUT, NOW); });
        assertEquals(inspect ? READ : label.equals("user") ? USER_LOCK : SESSION_LOCK, f.sql.getLast());
        f.owned();
      }
    }
  }
''';t=t.rstrip()[:-1]+newtests+'}\n';test.write_text(t);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p),str(test)],check=True,timeout=30)
current=test.read_text();inv=current[:current.index('  @Test\n  void resource001')].rstrip()+'\n}\n';inv=inv.replace('import org.jspecify.annotations.Nullable;\n','').replace('import org.junit.jupiter.api.Timeout;\n','').replace('@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\n','').replace(poolNew,poolOld).replace('    } finally {\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n','    }\n',1).replace('    }\n    }\n  }\n}', '    }\n  }\n}');inv=inv.replace(owned,'')
for a,z in reversed(hooks):assert inv.count(z)==1;inv=inv.replace(z,a)
formatted=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert formatted.returncode==0 and formatted.stdout==prior.encode();mainText=p.read_text();a=mainText.index('  private static final class VerifiedSession');brace=mainText.index('{',a);end=matching(mainText,brace,'{','}');withoutCarrier=mainText[:a]+oldcarrier+mainText[end+1:];assert re.findall(r'"(?:[^"\\]|\\.)*"',old)==re.findall(r'"(?:[^"\\]|\\.)*"',withoutCarrier)
security=['AuthenticationContextVerifier','AuthenticatedActor','ContextHash','AuthenticationInfrastructureException','AuthenticationContextException','package-info'];main=['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/'+n+'.java' for n in security]+['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/'+n+'.java' for n in ['RequiredColumn','JdbcResourceCleanup','package-info']]+['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/domain/'+n+'.java' for n in ['Role','package-info']];assert len(main)==11;sdk=r.parent/'toolchain/m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar';out=b/'evidence/PG34144-ssc427-source-oracle-inverse-v1';out.mkdir();v=dict(actualExit=0,sourceBefore=head,designPublication=pub,mainSources=main,testSources=[dict(path=str(test.relative_to(r)),tests=8)],inputHashes={n:sha(r/n) for n in main+[str(test.relative_to(r))]},sdkHashes={str(sdk):sha(sdk)},mainOwnershipWrapperInverseBeforeFormattingExact=True,resourceScopes=counts,privateCarrierInvariantOnlyThreeMethods=True,privateCarrierReflectedOrExposed=False,originalSixAssertionsInverseFormattedExact=True,oldTestSha256=hashlib.sha256(prior.encode()).hexdigest(),mainOriginalLiteralSequenceExactOutsideDeclaredCarrier=True,newDefinitions=2,necessaryPriorDefinitions=6,expectedTests=8,targets=['dev/codex/schubert/nk/api/security/AuthenticationContextVerifier','dev/codex/schubert/nk/api/security/AuthenticationContextVerifier$VerifiedSession'],memoryProxyOnly=True,actualDbFixtureNotCopiedOrExtracted=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=11,resourceScopes=counts,old6InverseExact=True,tests=8)))
