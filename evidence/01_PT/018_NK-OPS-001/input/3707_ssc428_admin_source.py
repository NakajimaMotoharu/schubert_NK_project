"""Preserve Admin8 oracles and exact multi-resource TWR ordering while establishing nonnull ownership."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pub=ld(b/'evidence/PG34242-ssc428-design-main-publication-v1/manifest.json');assert pub['actualExit']==0 and pub['ssc']=='SSC428';p=r/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AdminCommandAuthenticator.java';old=p.read_text();assert old.encode()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(r))]);head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
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
s=old;multi=[]
for m in list(re.finditer(r'try \(var statement\s*=',s))[::-1]:
 start=m.start();paren=s.index('(',start);end=matching(s,paren,'(',')');header=s[paren+1:end]
 if ';' not in header:continue
 first,second=header.split(';');assert first.strip().startswith('var statement =') and second.strip().startswith('var row =');brace=s.index('{',end);close=matching(s,brace,'{','}');body=s[brace+1:close];original=s[start:close+1];nested='try ('+first.strip()+') {\ntry ('+second.strip()+') {'+body+'}\n}';multi.append(dict(old=original,new=nested));s=s[:start]+nested+s[close+1:]
assert len(multi)==1;normalized=s;changes=[];counts={'statement':0,'row':0,'rows':0}
while (m:=re.search(r'try \(var (statement|rows|row)\s*=',s)):
 start=m.start();paren=s.index('(',start);end=matching(s,paren,'(',')');brace=s.index('{',end);close=matching(s,brace,'{','}');header=s[paren+1:end];name=m[1];expr=header.split('=',1)[1].strip();assert ';' not in expr;body=s[brace+1:close];primary='jdbcFailure'+str(len(changes)+1);method='closeStatement' if name=='statement' else 'closeRows';new='{\nvar '+name+' = requireValue('+expr+');\n@Nullable Throwable '+primary+' = null;\ntry {'+body+'} catch (SQLException | RuntimeException | Error failure) {\n'+primary+' = failure;\nthrow failure;\n} finally {\nJdbcResourceCleanup.'+method+'('+primary+', '+name+');\n}\n}';original=s[start:close+1];changes.append(dict(old=original,new=new));counts[name]+=1;s=s[:start]+new+s[close+1:]
assert counts==dict(statement=3,row=2,rows=1);back=s
for change in reversed(changes):assert back.count(change['new'])==1;back=back.replace(change['new'],change['old'],1)
assert back==normalized
for change in reversed(multi):assert back.count(change['new'])==1;back=back.replace(change['new'],change['old'],1)
assert back==old;s=s.replace('import dev.codex.schubert.nk.protocol.header.AuthenticationContext;','import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;\n\nimport dev.codex.schubert.nk.api.database.JdbcResourceCleanup;\nimport dev.codex.schubert.nk.protocol.header.AuthenticationContext;').replace('import java.util.OptionalLong;','import java.util.OptionalLong;\nimport org.jspecify.annotations.Nullable;');p.write_text(s)
test=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AdminPreludeJdbcPortTest.java';prior=test.read_text();assert prior.count('@Test')==8;poolOld='    try (var pool = Executors.newFixedThreadPool(2)) {';poolNew='    var pool = Executors.newFixedThreadPool(2);\n    try {';assert prior.count(poolOld)==1;t=prior.replace(poolOld,poolNew);end=t.rindex('    }\n  }\n}');t=t[:end]+'    } finally {\n      pool.shutdownNow();\n      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));\n'+t[end:];t=t.replace('import org.junit.jupiter.api.Test;','import org.jspecify.annotations.Nullable;\nimport org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;').replace('final class AdminPreludeJdbcPortTest {','@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class AdminPreludeJdbcPortTest {');hooks=[('    String faultAt = "";','    String faultAt = "";\n    String nullStatementAt = "";\n    String nullRowAt = "";'),('    RuntimeException runtimeFailure;','    @Nullable RuntimeException runtimeFailure;'),('    PreparedStatement statement(String sql) throws SQLException {','    @Nullable PreparedStatement statement(String sql) throws SQLException {'),('      fault(name + ".prepare");','      fault(name + ".prepare");\n      if (name.equals(nullStatementAt)) return null;'),('    ResultSet row(String name) {','    @Nullable ResultSet row(String name) {\n      if (name.equals(nullRowAt)) return null;')]
for a,z in hooks:assert t.count(a)==1;t=t.replace(a,z)
newtests='''
  @Test
  void resource001AllPreludeAndAuthenticationStatementsFailClosedOnNull() {
    for (String label : List.of(CANDIDATE, ADVISORY, USERS, LOCKED, AUTH_USER, AUTH_SESSION, TOUCH)) {
      Fixture f = new Fixture();
      f.nullStatementAt = label;
      infrastructure(f, Mutation.DISABLE, OptionalLong.of(20));
      assertEquals(label, f.order.getLast());
    }
  }

  @Test
  void resource002AllPreludeAndAuthenticationNullRowsCloseTheirOwnedStatements() {
    for (String label : List.of(CANDIDATE, ADVISORY, USERS, LOCKED, AUTH_USER, AUTH_SESSION)) {
      Fixture f = new Fixture();
      f.nullRowAt = label;
      infrastructure(f, Mutation.DISABLE, OptionalLong.of(20));
      assertEquals(label, f.order.getLast());
    }
  }

  @Test
  void mutation001ClosedVocabularyLookupDefensiveValuesAndMembershipReduction() {
    assertEquals(List.of("CREATE", "ENABLE", "DISABLE", "PROMOTE", "DEMOTE", "RESET_PASSWORD", "UNLOCK"), java.util.Arrays.stream(Mutation.values()).map(Enum::name).toList());
    assertSame(Mutation.CREATE, Mutation.valueOf("CREATE"));
    assertSame(Mutation.ENABLE, Mutation.valueOf("ENABLE"));
    assertSame(Mutation.DISABLE, Mutation.valueOf("DISABLE"));
    assertSame(Mutation.PROMOTE, Mutation.valueOf("PROMOTE"));
    assertSame(Mutation.DEMOTE, Mutation.valueOf("DEMOTE"));
    assertSame(Mutation.RESET_PASSWORD, Mutation.valueOf("RESET_PASSWORD"));
    assertSame(Mutation.UNLOCK, Mutation.valueOf("UNLOCK"));
    var exposed = Mutation.values();
    exposed[0] = Mutation.UNLOCK;
    assertSame(Mutation.CREATE, Mutation.values()[0]);
    for (Mutation mutation : Mutation.values())
      assertEquals(List.of(Mutation.DISABLE, Mutation.DEMOTE).contains(mutation), mutation.reducesMembership());
    for (String unknown : List.of("UNKNOWN", "", "create", " CREATE "))
      assertThrows(IllegalArgumentException.class, () -> Mutation.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> Mutation.valueOf(null));
  }
''';t=t.rstrip()[:-1]+newtests+'}\n';test.write_text(t);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(p),str(test)],check=True,timeout=30);current=test.read_text();inv=current[:current.index('  @Test\n  void resource001')].rstrip()+'\n}\n';inv=inv.replace('import org.jspecify.annotations.Nullable;\n','').replace('import org.junit.jupiter.api.Timeout;\n','').replace('@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\n','').replace(poolNew,poolOld).replace('    } finally {\n      pool.shutdownNow();\n      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));\n','    }\n',1).replace('    }\n    }\n  }\n}', '    }\n  }\n}')
for a,z in reversed(hooks):assert inv.count(z)==1;inv=inv.replace(z,a)
formatted=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert formatted.returncode==0 and formatted.stdout==prior.encode()
def literal_values(source):
 values=[]
 for token in re.findall(r'"""[\s\S]*?"""|"(?:[^"\\]|\\.)*"',source):
  if not token.startswith('"""'):values.append(('STRING',token));continue
  text=token[3:-3];assert text.startswith('\n') and '\\' not in text
  lines=text[1:].split('\n');indent=min(len(line)-len(line.lstrip(' \t')) for index,line in enumerate(lines) if line.strip() or index==len(lines)-1);values.append(('TEXTBLOCK','\n'.join(line[indent:].rstrip(' \t') for line in lines)))
 return values
assert literal_values(old)==literal_values(p.read_text());base=ld(b/'evidence/PG34156-ssc427-source-oracle-inverse-v2/manifest.json');main=base['mainSources']+['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/'+n+'.java' for n in ['AdminCommandAuthenticator','AuthorizationService','AuthorizationException']];assert len(main)==14;out=b/'evidence/PG34244-ssc428-source-oracle-inverse-v1';out.mkdir();v=dict(actualExit=0,sourceBefore=head,designPublication=pub,mainSources=main,testSources=[dict(path=str(test.relative_to(r)),tests=11)],inputHashes={n:sha(r/n) for n in main+[str(test.relative_to(r))]},sdkHashes=base['sdkHashes'],mainOwnershipWrapperInverseBeforeFormattingExact=True,oneMultiHeaderNormalizedAndInverseExact=True,resourceScopes=counts,originalEightAssertionsInverseFormattedExact=True,oldTestSha256=hashlib.sha256(prior.encode()).hexdigest(),mainRegularLiteralSequenceExact=True,textBlockSqlValueExactAfterIncidentalIndent=True,newDefinitions=3,necessaryPriorDefinitions=8,expectedTests=11,targets=['dev/codex/schubert/nk/api/security/AdminCommandAuthenticator','dev/codex/schubert/nk/api/security/AdminCommandAuthenticator$Mutation'],memoryProxyOnly=True,actualDbFixtureNotCopiedOrExtracted=True,actualAdvisoryLockOrAdminMutation=False,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=14,resourceScopes=counts,multiTwrInverseExact=True,old8InverseExact=True,tests=11)))
