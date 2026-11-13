"""SSC341 known-SQL guards only; no transitive compile, product/DB/native operation."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,os,xml.etree.ElementTree as X
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG29778-morning-typed-sql-source-manufacture-v1';assert not e.exists();e.mkdir();p=r/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.java';old=p.read_text();prior=json.loads((b/'evidence/PG29726-morning-db-catalog-review-before-v1/manifest.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==prior['sourceSha256'];(e/'MorningDatabaseSession.before.java.txt').write_text(old)
pattern=r'catch\s*\(([^)]*)\)\s*\{\s*(?:primary = failure;\s*)?throw unavailable\(\);';matches=list(re.finditer(pattern,old,re.S));assert len(matches)==20 and len(prior['catalogConversionSites'])==20;new=old;replacements=[]
for m in reversed(matches):
 block=m.group(0);variable=re.search(r'([A-Za-z][A-Za-z0-9_]*)\s*$',m.group(1)).group(1);indent=re.search(r'\n([ \t]*)throw unavailable\(\);$',block).group(1)
 if 'primary = failure;' in block:
  insertion=('try {\n'+indent+'  preserveCatalogFatal('+variable+');\n'+indent+'} catch (Error fatal) {\n'+indent+'  primary = fatal;\n'+indent+'  throw fatal;\n'+indent+'}\n'+indent+'throw unavailable();')
 else:insertion='preserveCatalogFatal('+variable+');\n'+indent+'throw unavailable();'
 changed=block.replace('throw unavailable();',insertion);new=new[:m.start()]+changed+new[m.end():];replacements.append((block,changed))
pairs=[]
a='''        } catch (SQLException secondary) {
          if (closeReplace(primary, secondary)) throw unavailable();
''';z='''        } catch (SQLException secondary) {
          if (closeReplace(primary, secondary)) {
            preserveCatalogFatal(secondary);
            throw unavailable();
          }
''';pairs.append((a,z))
a='''    if (!known) primary.addSuppressed(new BatchRepositoryException());
    return false;
''';z='''    if (!known) primary.addSuppressed(new BatchRepositoryException());
    else if ((primary instanceof SQLException || primary instanceof BatchRepositoryException)
        && secondary instanceof SQLException) {
      preserveCatalogFatal(primary);
      preserveCatalogFatal(secondary);
    }
    return false;
''';pairs.append((a,z))
marker='  private static boolean closeReplace(@Nullable Throwable primary, Throwable secondary) {';helper='''  // SSC341: preserve typed IO/unknown policy; classify only known SQL catalog discards.
  private static void preserveCatalogFatal(Throwable failure) {
    if (failure instanceof SQLException || failure instanceof BatchRepositoryException) {
      dev.codex.schubert.nk.storage.StorageIoException.preserveFatal(failure);
    }
  }

''';pairs.append((marker,helper+marker))
for a,z in pairs:assert new.count(a)==1;(None);new=new.replace(a,z)
inverse=new
for a,z in reversed(pairs):assert inverse.count(z)==1;inverse=inverse.replace(z,a)
for a,z in reversed(replacements):assert z in inverse;inverse=inverse.replace(z,a,1)
assert inverse==old and new.count('preserveCatalogFatal(')==24
literal=lambda t:re.findall(r'"(?:[^"\\]|\\.)*"',t);assert literal(new)==literal(old);p.write_text(new)
tc=r.parent/'toolchain';java=tc/'jdk-25.0.4/bin/java';gjf=tc/'google-java-format-1.36.1-all-deps.jar';cs=tc/'static-gates-20261015/checkstyle-14.3.0-all.jar';fmt=[str(java),'-jar',str(gjf),'--skip-reflowing-long-strings'];commands=[]
for label,args in [('format',fmt+['--replace',str(p)]),('format-check',fmt+['--dry-run','--set-exit-if-changed',str(p)]),('checkstyle',[str(java),'-jar',str(cs),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(e/'checkstyle.xml'),str(p)])]:
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (e/(label+'.stdout')).open('xb') as out,(e/(label+'.stderr')).open('xb') as err:
  child=subprocess.Popen(args,cwd=r,stdin=subprocess.DEVNULL,stdout=out,stderr=err);code=child.wait(timeout=180)
 commands.append(dict(label=label,command=args,pid=child.pid,ownerPid=os.getpid(),startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actualExit=code));assert code==0
assert not X.parse(e/'checkstyle.xml').findall('.//error');normalize=lambda s:subprocess.check_output(fmt+['-'],input=s.encode());assert normalize(inverse)==normalize(old) and p.read_bytes()==normalize(new);assert literal(p.read_text())==literal(old)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();manifest=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMainBefore='5330eb303026206a87af466d0ffebb884b8e04b8',oneMainChanged=str(p.relative_to(r)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=sha(p),sourceFullNormalizedInverseEqual=True,allJavaStringLiteralsIncludingSqlUnchanged=True,knownCatalogSites=20,guardCalls=23,outerClassifiedFatalRecordedAsFinallyPrimary=True,knownSqlPairAndSuccessSqlCloseCoveredBySource=True,checkedIoAndUnknownSelectionUnchanged=True,sourceGjfCheckstyle0=True,commands=commands,toolHashes={str(x):sha(x) for x in [java,gjf,cs,r/'tools/quality/static/checkstyle.xml']},publicDesignMain='03794704417dbfbcb6e3b56fe784bec6bca31919',SS='SSC-341',BUG='BUG-2852',YKT='YKT-2359',newTestDefinitions=0,productTestsExecuted=0,coverage=None,NullAwayPmdSpotbugs='NOT_RUN_TRANSITIVE_ROOT_ACTUAL4_HOLD_NO_STUBS',wholeOriginalMorningDbTests=65,wholeTests='HOLD_NOT_RUN_NO_EXTRACTION',actualDbVmRootNativeKeyPermitActions=0,formalAcceptanceAdded=0)
(e/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('SSC341 oneMain known20/close guards created; all SQL/literals and inverse preserved; GJF-CS0; compile/PT/coverage NOT_RUN')
