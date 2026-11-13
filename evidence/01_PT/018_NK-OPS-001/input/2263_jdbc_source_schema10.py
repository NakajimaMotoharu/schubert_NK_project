from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';c=json.loads((B/'input/2262_schema10_pgpt_start.json').read_text());changes=[]
for name in c['implementationArtifactPaths']:
 p=R/name;old=p.read_text();assert old==subprocess.check_output(['git','show',c['source']+':'+name],text=True);new=old;rs=[]
 if p.stem=='JdbcAdmissionFailures':
  rs.append(('import java.sql.SQLException;\n','import dev.codex.schubert.nk.storage.StorageIoException;\nimport java.sql.SQLException;\n',1))
  a='  static boolean replace(@Nullable Throwable primary, Throwable secondary) {\n';rs.append((a,a+'    beforeDiscard(primary, secondary);\n',1))
  a='''    return false;
  }
}''';b='''    return false;
  }

  /** Classify only known SQL failures before discarding them; unknown primary identity stays. */
  static void beforeDiscard(@Nullable Throwable primary, Throwable secondary) {
    if (primary instanceof SQLException) StorageIoException.preserveFatal(primary);
    if ((primary == null || primary instanceof SQLException) && secondary instanceof SQLException)
      StorageIoException.preserveFatal(secondary);
  }
}''';rs.append((a,b,1))
 else:
  a='import java.';assert a in old;i=old.index(a);imp='import dev.codex.schubert.nk.storage.StorageIoException;\n';new=old[:i]+imp+old[i:];rs.append(('',imp,1))
  if p.stem=='SchemaHistoryAdmission':
   a='    } catch (SQLException known) {\n';rs.append((a,a+'      StorageIoException.preserveFatal(known);\n',1))
  elif p.stem=='ServiceDatabaseAdmission':
   a='    } catch (SQLException failure) {\n';rs.append((a,a+'      StorageIoException.preserveFatal(failure);\n',1))
  else:
   assert p.stem=='ServiceDatabaseSource'
   a='''        } catch (SQLException failure) {
          discard(connection, failure);
          throw unavailable();''';b='''        } catch (SQLException failure) {
          discard(connection, failure);
          StorageIoException.preserveFatal(failure);
          throw unavailable();''';rs.append((a,b,1))
   a='\n      } catch (SQLException failure) {\n';rs.append((a,a+'        StorageIoException.preserveFatal(failure);\n',1))
   for a in ['    } catch (SQLException cleanup) {\n','    } catch (RuntimeException | Error cleanup) {\n']:rs.append((a,a+'      JdbcAdmissionFailures.beforeDiscard(primary, cleanup);\n',1))
 for a,b,n in rs:
  if a:assert new.count(a)==n;new=new.replace(a,b)
 changes.append((p,old,new,rs))
root=R/'src/schubert-nk-bootstrap/src';t=root/'test/java/dev/codex/schubert/nk/api/maintenance/SchemaHistoryAdmissionTest.java';ot=t.read_text();assert len(re.findall(r'@Test\b',ot))==9
oldhead='    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {\n';head='    var executor = Executors.newVirtualThreadPerTaskExecutor();\n    try {\n';assert ot.count(oldhead)==1
oldtail='''      for (var task : tasks)
        assertArrayEquals(new int[] {1, 1, 0}, task.get(5, java.util.concurrent.TimeUnit.SECONDS));
    }
  }
''';tail='''      for (var task : tasks)
        assertArrayEquals(new int[] {1, 1, 0}, task.get(5, java.util.concurrent.TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
  }
''';assert ot.count(oldtail)==1
new='''
  @Test
  void opsSchema010KnownSqlFatalGraphsCloseOwnersAndPreserveOriginalIdentity() {
    for (String site : List.of(FIXTURE_PREPARESTATEMENT_CB987D1F, "setQueryTimeout",
        "executeQuery", FIXTURE_NEXT_CA1733B5, FIXTURE_ROWCLOSE_4440E762,
        FIXTURE_STATEMENTCLOSE_D5A13A63)) {
      for (int graph = 0; graph < 4; graph++) {
        var marker = new LinkageError("synthetic SQL fatal");
        var failure = new SQLException("synthetic SQL provider", "P0001");
        if (graph == 0) failure.initCause(marker);
        else if (graph == 1) failure.addSuppressed(marker);
        else if (graph == 2) {
          var cycle = new SQLException("synthetic SQL cycle", failure);
          failure.initCause(cycle);
          cycle.addSuppressed(marker);
        } else failure.setNextException(new SQLException("synthetic SQL next", marker));
        var probe = new Probe();
        probe.faults.put(site, failure);
        assertSame(marker, assertThrows(LinkageError.class,
            () -> new SchemaHistoryAdmission(RELEASE).inspect(probe.connection())));
        int rows = List.of(FIXTURE_PREPARESTATEMENT_CB987D1F, "setQueryTimeout", "executeQuery")
            .contains(site) ? 0 : 1;
        int statements = site.equals(FIXTURE_PREPARESTATEMENT_CB987D1F) ? 0 : 1;
        assertArrayEquals(new int[] {rows, statements, 0}, probe.closed);
        assertNull(marker.getCause());
        assertEquals(0, marker.getSuppressed().length);
      }
    }
    var primaryMarker = new LinkageError("synthetic SQL primary fatal");
    var primary = new Probe();
    primary.faults.put(FIXTURE_NEXT_CA1733B5, new SQLException("synthetic SQL", primaryMarker));
    primary.faults.put(FIXTURE_ROWCLOSE_4440E762, new IllegalStateException("synthetic row close"));
    assertSame(primaryMarker, assertThrows(LinkageError.class,
        () -> new SchemaHistoryAdmission(RELEASE).verify(primary.connection())));
    assertArrayEquals(new int[] {1, 1, 0}, primary.closed);
    assertEquals(0, primaryMarker.getSuppressed().length);
    var secondaryMarker = new LinkageError("synthetic SQL secondary fatal");
    var secondary = new Probe();
    secondary.faults.put(FIXTURE_NEXT_CA1733B5, new SQLException("synthetic ordinary SQL"));
    secondary.faults.put(FIXTURE_ROWCLOSE_4440E762, new SQLException("synthetic SQL", secondaryMarker));
    secondary.faults.put(FIXTURE_STATEMENTCLOSE_D5A13A63,
        new IllegalStateException("synthetic statement close"));
    assertSame(secondaryMarker, assertThrows(LinkageError.class,
        () -> new SchemaHistoryAdmission(RELEASE).verify(secondary.connection())));
    assertArrayEquals(new int[] {1, 1, 0}, secondary.closed);
    assertNull(secondaryMarker.getCause());
    assertEquals(1, secondaryMarker.getSuppressed().length);
    assertEquals("database admission resource failure", secondaryMarker.getSuppressed()[0].getMessage());
    assertNull(secondaryMarker.getSuppressed()[0].getCause());
  }
'''
nt=ot.replace(oldhead,head).replace(oldtail,tail);assert nt.endswith('}\n');nt=nt[:-2]+new+'}\n'
O=B/'evidence/PG29148-jdbc-four-main-schema10-source-closure-v1';assert not O.exists();O.mkdir();proof=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,old,now,rs in changes:
 (O/(p.stem+'-before.txt')).write_text(old);p.write_text(now);subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','-i',str(p)],check=True);inv=p.read_text()
 for a,b,n in reversed(rs):
  assert inv.count(b)==n
  inv=inv.replace(b,a)
 assert inv==old;proof.append(dict(path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=sha(p),originalByteInverseExact=True))
(O/'SchemaHistoryAdmissionTest-before.txt').write_text(ot);t.write_text(nt);subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','-i',str(t)],check=True);nt=t.read_text();i=nt.index('  @Test\n  void opsSchema010');inv=nt[:i].rstrip()+'\n}\n';inv=inv.replace(head,oldhead).replace(tail,oldtail);assert inv==ot
paths=[str(root/'main/java/dev/codex/schubert/nk/api/bootstrap'/n) for n in ['SchemaHistoryAdmission.java','JdbcAdmissionFailures.java']]+[str(R/'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java')]
(O/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceBefore=c['source'],changedMainProof=proof,changedMainHashes={p['path']:p['afterSha256'] for p in proof},mainInputHashes={str(Path(p).relative_to(R)):sha(Path(p)) for p in paths},testInputHashes={str(t.relative_to(R)):sha(t)},originalFourSourceInverseExact=True,originalWhole9InverseExactExceptFiniteWorkerClose=True,ordinaryIndependent64MatrixUnchanged=True,oldWhole9Sha256=hashlib.sha256(ot.encode()).hexdigest(),wholeTestCount=10,newDefinitions=1,knownSqlFatalGraphScopesOnly=True,unknownNonSqlPrimaryAndResourceClosePriorityUnchanged=True,independentOracle='Six fixed fault sites x4 cause/suppressed/cycle/SQLnext graphs all same Erroridentity, literal rows-statement-connection closecounts; twoexplicit knownSQLprimary/secondarygraph peerclose cases. Original64 ordinarytype matrix unchanged; originalworker8/barrier5/get5 unchanged, finallyshutdown-await10 only.',wholeMain3AndWholeTest10Reviewed=True,relatedTwoMainRuntimeNotAccepted=True,productTestsExecuted=0,newAcceptance=0,actualDbDdlMigrationRootCredentialNativeVmActions=0),ensure_ascii=False,indent=2)+'\n');print('FourMain PG, oldwhole9 inverse exceptfinitefinally exact; newSchema010 24+2 independentvectors, Main3/physical5 closure, ProductPT0')
