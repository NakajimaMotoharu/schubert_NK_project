"""Current closed reason/graph tests, retaining whole original client10 and registry7."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));base='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/';main=[base+n+'.java' for n in ['ReplyCorrelationRegistry','PendingReply','JmsRequestReplyClient','JmsRequestReplyException','JmsRequestSender','package-info']];rootp=b/'evidence/PG34846-ssc436-closed24-prepare-v1/manifest.json';root=ld(rootp);unitp=b/'evidence/PG34860-ssc436-closed24-unit-v1/manifest.json';unit=ld(unitp);assert unit['productionCoreMain']=='01cc280064936775e0377371edb3cdf1fa4f1139' and unit['actualExit']==0 and unit['begin']['prepare']==ref(rootp);assert all(sha(r/n)==root['inputHashes'][n] and (r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main);oldp=b/'evidence/PG26456-jms-client-nineteen-unit-v1/manifest.json';old=ld(oldp)['begin'];tests=['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/'+n+'.java' for n in ['JmsRequestReplyClientTest','ReplyCorrelationRegistryTest']];assert all(sha(r/n)==old['inputHashes'][n] and (r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in tests);p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/JmsExceptionGraphValueTest.java';assert not p.exists();p.write_text('''package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import jakarta.jms.JMSException;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-JMS-VALUE001/GRAPH002; SS312321: public synthetic exceptions, no provider/broker/DB. */
final class JmsExceptionGraphValueTest {
  private static final String TEXT = "public bounded failure";

  @Test
  void jmsvalue001ReasonsHaveExactNamesDefensiveArraysAndConstructorNullContracts() {
    var values = List.of(JmsRequestReplyException.Reason.CAPACITY,
        JmsRequestReplyException.Reason.TIMEOUT, JmsRequestReplyException.Reason.INTERRUPTED);
    var names = List.of("CAPACITY", "TIMEOUT", "INTERRUPTED");
    assertEquals(values, List.of(JmsRequestReplyException.Reason.values()));
    for (int index = 0; index < names.size(); index++) {
      assertEquals(names.get(index), values.get(index).name());
      assertSame(values.get(index), JmsRequestReplyException.Reason.valueOf(names.get(index)));
      var plain = new JmsRequestReplyException(values.get(index), TEXT);
      var cause = new IllegalStateException(TEXT);
      var caused = new JmsRequestReplyException(values.get(index), TEXT, cause);
      var explicitNull = new JmsRequestReplyException(values.get(index), TEXT, null);
      assertSame(values.get(index), plain.reason());
      assertSame(values.get(index), caused.reason());
      assertSame(values.get(index), explicitNull.reason());
      assertEquals(TEXT, plain.getMessage());
      assertEquals(TEXT, caused.getMessage());
      assertEquals(TEXT, explicitNull.getMessage());
      assertNull(plain.getCause());
      assertNull(explicitNull.getCause());
      assertSame(cause, caused.getCause());
      assertEquals(0, plain.getSuppressed().length);
      assertEquals(0, caused.getSuppressed().length);
    }
    var copy = JmsRequestReplyException.Reason.values();
    copy[0] = JmsRequestReplyException.Reason.TIMEOUT;
    assertSame(JmsRequestReplyException.Reason.CAPACITY, JmsRequestReplyException.Reason.values()[0]);
    for (String unknown : List.of("", "UNKNOWN", "capacity", "CAPACITY "))
      assertThrows(IllegalArgumentException.class, () -> JmsRequestReplyException.Reason.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> JmsRequestReplyException.Reason.valueOf(null));
    assertThrows(NullPointerException.class, () -> new JmsRequestReplyException(null, TEXT));
    assertThrows(NullPointerException.class, () -> new JmsRequestReplyException(null, TEXT, null));
  }

  @Test
  void jmsgraph002FatalIdentityPrecedenceAndNonfatalCyclesAreFiniteAndUnmodified() {
    for (int kind = 0; kind < 7; kind++) {
      var fatal = new AssertionError(TEXT);
      Throwable root;
      switch (kind) {
        case 0 -> root = fatal;
        case 1 -> root = new IllegalStateException(TEXT, fatal);
        case 2 -> {
          root = new IllegalStateException(TEXT);
          root.addSuppressed(fatal);
        }
        case 3 -> {
          var sql = new SQLException(TEXT);
          sql.setNextException(new SQLException(TEXT, fatal));
          root = sql;
        }
        case 4 -> {
          var jms = new JMSException(TEXT);
          jms.setLinkedException(new IllegalStateException(TEXT, fatal));
          root = jms;
        }
        case 5 -> {
          var sql = new SQLException(TEXT);
          sql.setNextException(new SQLException(TEXT, fatal));
          var jms = new JMSException(TEXT);
          jms.setLinkedException(sql);
          root = jms;
        }
        case 6 -> {
          root = new IllegalStateException(TEXT, fatal);
          root.addSuppressed(new AssertionError("public second fatal"));
        }
        default -> throw new AssertionError(TEXT);
      }
      assertSame(fatal, assertThrows(AssertionError.class, () -> JmsRequestReplyException.preserveFatal(root)));
      assertEquals(0, fatal.getSuppressed().length);
    }
    var first = new IllegalStateException(TEXT);
    var second = new IllegalArgumentException(TEXT, first);
    first.initCause(second);
    var sqlFirst = new SQLException(TEXT);
    var sqlSecond = new SQLException(TEXT);
    sqlFirst.setNextException(sqlSecond);
    sqlSecond.setNextException(sqlFirst);
    var jmsFirst = new JMSException(TEXT);
    var jmsSecond = new JMSException(TEXT);
    jmsFirst.setLinkedException(jmsSecond);
    jmsSecond.setLinkedException(jmsFirst);
    first.addSuppressed(sqlFirst);
    first.addSuppressed(jmsFirst);
    second.addSuppressed(jmsSecond);
    assertDoesNotThrow(() -> JmsRequestReplyException.preserveFatal(first));
    assertSame(second, first.getCause());
    assertSame(first, second.getCause());
    assertSame(sqlSecond, sqlFirst.getNextException());
    assertSame(sqlFirst, sqlSecond.getNextException());
    assertSame(jmsSecond, jmsFirst.getLinkedException());
    assertSame(jmsFirst, jmsSecond.getLinkedException());
    assertDoesNotThrow(() -> JmsRequestReplyException.preserveFatal(new SQLException(TEXT)));
    assertDoesNotThrow(() -> JmsRequestReplyException.preserveFatal(new JMSException(TEXT)));
    assertThrows(NullPointerException.class, () -> JmsRequestReplyException.preserveFatal(null));
  }
}
''');subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);assert all(sha(r/n)==old['inputHashes'][n] for n in tests);sdk={n:h for n,h in root['dependencies'].items() if '/jakarta/jms/jakarta.jms-api/3.1.0/' in n};assert len(sdk)==1 and all(sha(Path(n))==h for n,h in sdk.items());out=b/'evidence/PG34900-jms-scope19-source-v1';out.mkdir();v=dict(actualExit=0,mainSources=main,testSources=[dict(path=tests[0],tests=10),dict(path=tests[1],tests=7),dict(path=str(p.relative_to(r)),tests=2)],inputHashes={n:sha(r/n) for n in main+tests+[str(p.relative_to(r))]},sdkHashes=sdk,mainSourcesUnchanged=True,originalClient10Registry7ByteExact=True,newDefinitions=2,necessaryPriorDefinitions=17,expectedTests=19,targets=['dev/codex/schubert/nk/web/messaging/'+n for n in ['ReplyCorrelationRegistry','PendingReply','JmsRequestReplyClient','JmsRequestReplyException','JmsRequestReplyException$Reason','JmsRequestSender']],currentMainRootCompileReference=ref(rootp),currentCoreQualificationReference=ref(unitp),currentMainStaticReference=ref(b/'evidence/PG34848-ssc436-closed24-static-v1/manifest.json'),mainRootReusableOnlyForExactSourceAndBinary=True,noOld19CurrentSourceTransfer=True,noWholeWebOrApiJarPayloadAccess=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,mainSources=len(main),tests=v['expectedTests'],newDefinitions=v['newDefinitions'],oldWhole17Unchanged=True,sdk=len(sdk))))
