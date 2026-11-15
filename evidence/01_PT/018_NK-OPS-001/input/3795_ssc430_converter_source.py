"""Keep original form13 oracles, add existing finite fatal graph guard and independent two tests."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pub=ld(b/'evidence/PG34482-ssc430-design-main-publication-v1/manifest.json');assert pub['actualExit']==0 and pub['ssc']=='SSC430';mainp=r/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/LoginFormAuthenticationConverter.java';before=mainp.read_text();assert before.encode()==subprocess.check_output(['git','show','HEAD:'+str(mainp.relative_to(r))]);s=before;importBefore='import jakarta.servlet.http.HttpServletRequest;';importAfter='import dev.codex.schubert.nk.web.session.SessionStoreException;\n'+importBefore;guardBefore='    } catch (IllegalArgumentException | IllegalStateException | NoSuchElementException failure) {\n      throw new LoginFormRejectedException();';guardAfter='    } catch (IllegalArgumentException | IllegalStateException | NoSuchElementException failure) {\n      SessionStoreException.preserveFatal(failure);\n      throw new LoginFormRejectedException();';assert s.count(guardBefore)==s.count(importBefore)==1;s=s.replace(importBefore,importAfter,1).replace(guardBefore,guardAfter,1);mainp.write_text(s);p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/LoginFormConverterPortTest.java';old=p.read_text();assert old.count('@Test')==13;s=old;changes=[('import org.junit.jupiter.api.Test;','import org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;'),('final class LoginFormConverterPortTest {','@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class LoginFormConverterPortTest {'),('    try (var workers = Executors.newFixedThreadPool(2)) {','    var workers = Executors.newFixedThreadPool(2);\n    try {'),('        untrusted(pending.get(i).get(10, TimeUnit.SECONDS), READER + i, PUBLIC_PASSWORD);\n    }','        untrusted(pending.get(i).get(10, TimeUnit.SECONDS), READER + i, PUBLIC_PASSWORD);\n    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n    }')]
for a,z in changes:assert s.count(a)==1,a;s=s.replace(a,z,1)
pairs=[('"getMethod"','FORM_GET_METHOD'),('"getParameterValues"','FORM_GET_PARAMETER_VALUES')];declarations=''
for literal,name in pairs:assert s.count(literal)==2;s=s.replace(literal,name);declarations+='  private static final String '+name+' = '+literal+';\n'
s=s.replace('  private static final String FIXTURE_FAULT = "synthetic fixture fault";\n','  private static final String FIXTURE_FAULT = "synthetic fixture fault";\n'+declarations,1)
new='''
  @Test
  void formfatal014EveryDeclaredClassificationPreservesCauseAndSuppressedFatalIdentity() {
    for (int kind = 0; kind < 3; kind++) {
      for (String site : List.of(FORM_GET_METHOD, FORM_GET_PARAMETER_VALUES)) {
        for (boolean cause : new boolean[] {true, false}) {
          AssertionError fatal = new AssertionError(FIXTURE_FAULT);
          RuntimeException wrapper = classifiedFormFailure(kind, cause ? fatal : null);
          if (!cause) wrapper.addSuppressed(fatal);
          Fixture f = new Fixture();
          f.faultAt = site;
          f.fault = wrapper;
          assertSame(fatal, assertThrows(AssertionError.class, () -> CONVERTER.convert(f.asRequest())));
          assertEquals(0, fatal.getSuppressed().length);
        }
      }
    }
  }

  @Test
  void formfatal015NonfatalCyclesAreFiniteRedactedAndUnknownRuntimeKeepsIdentity() {
    for (int kind = 0; kind < 3; kind++) {
      RuntimeException first = new RuntimeException(FIXTURE_FAULT);
      RuntimeException second = new RuntimeException(FIXTURE_FAULT);
      first.initCause(second);
      second.initCause(first);
      RuntimeException shared = new RuntimeException(FIXTURE_FAULT);
      first.addSuppressed(shared);
      RuntimeException wrapper = classifiedFormFailure(kind, first);
      wrapper.addSuppressed(shared);
      Fixture f = new Fixture();
      f.faultAt = FORM_GET_PARAMETER_VALUES;
      f.fault = wrapper;
      rejected(f);
      assertSame(second, first.getCause());
      assertSame(first, second.getCause());
    }
    Fixture f = new Fixture();
    UnsupportedOperationException unknown = new UnsupportedOperationException(FIXTURE_FAULT);
    f.faultAt = FORM_GET_METHOD;
    f.fault = unknown;
    assertSame(unknown, assertThrows(UnsupportedOperationException.class, () -> CONVERTER.convert(f.asRequest())));
  }

  private static RuntimeException classifiedFormFailure(int kind, Throwable cause) {
    return switch (kind) {
      case 0 -> new IllegalArgumentException(FIXTURE_FAULT, cause);
      case 1 -> new IllegalStateException(FIXTURE_FAULT, cause);
      case 2 -> new NoSuchElementException(FIXTURE_FAULT, cause);
      default -> throw new AssertionError("unknown form exception fixture");
    };
  }
''';s=s.rstrip()[:-1]+new+'}\n';p.write_text(s);formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(formatter+['--replace',str(mainp),str(p)],check=True,timeout=30);inv=p.read_text();inv=inv[:inv.index('  @Test\n  void formfatal014')].rstrip()+'\n}\n';assert inv.count(declarations)==1;inv=inv.replace(declarations,'',1)
for literal,name in pairs:inv=re.sub(r'\b'+name+r'\b',literal,inv)
for a,z in reversed(changes):
 pattern=''.join(r'\s+' if part.isspace() else re.escape(part) for part in re.split(r'(\s+)',z.strip()));matches=list(re.finditer(pattern,inv));assert len(matches)==1,(a,z);m=matches[0];inv=inv[:m.start()]+a.strip()+inv[m.end():]
result=subprocess.run(formatter+['-'],input=inv.encode(),capture_output=True,timeout=30);assert result.returncode==0 and result.stdout==old.encode();assert mainp.read_text().replace(importAfter,importBefore,1).replace(guardAfter,guardBefore,1)==before
main=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/'+n+'.java' for n in ['LoginFormAuthenticationConverter','CaddyClientAddressResolver','LoginClientAddress','LoginFormRejectedException','CaddyRequestRejectedException']]+['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/'+n+'.java' for n in ['SessionStoreException','InvalidSessionRowException']];assert len(main)==7;priorp=b/'evidence/PG27632-caddy-context24-independent-v1/manifest.json';prior=ld(priorp);sdkrefp=b/'evidence/PG25856-closed-mock-auth-current-console-preflight-v1/manifest.json';sdkref=ld(sdkrefp);allowed=['/jakarta/servlet/jakarta.servlet-api/6.1.0/','/commons-logging/commons-logging/1.4.0/','/org/springframework/spring-core/7.0.9/','/org/springframework/spring-web/7.0.9/','/org/springframework/security/spring-security-core/7.1.1/','/org/springframework/security/spring-security-web/7.1.1/'];sdk={}
for marker in allowed:
 source=prior if 'jakarta/servlet' in marker else sdkref;values={path:h for path,h in source['dependencies'].items() if marker in path};assert len(values)==1 and all(path.startswith(str(r.parent/'toolchain/m2/repository')+'/') and sha(Path(path))==h for path,h in values.items());sdk.update(values)
assert len(sdk)==6;out=b/'evidence/PG34484-ssc430-converter-source-inverse-v1';out.mkdir();v=dict(actualExit=0,designPublication=pub,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=15)],inputHashes={path:sha(r/path) for path in main+[str(p.relative_to(r))]},sdkHashes=sdk,sdkProvenance=[ref(priorp),ref(sdkrefp)],originalThirteenAssertionsInverseFormattedExact=True,onlyMainGuardAndImportInverseExact=True,oldTestSha256=hashlib.sha256(old.encode()).hexdigest(),newDefinitions=2,necessaryPriorDefinitions=13,expectedTests=15,syntheticGraphCases=16,targets=['dev/codex/schubert/nk/web/security/LoginFormAuthenticationConverter'],noWholeWebOrApiJarPayloadAccess=True,original2Workers8TasksGet10Preserved=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=7,tests=15,original13InverseExact=True,sdk=6,syntheticGraphCases=16)))
