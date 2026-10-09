"""SSC241 exact completed-original + failed PID1 recovery, zero intent operations."""
import ast
from pathlib import Path
import pg813_sources as prior
R=Path(__file__).resolve().parent
SOURCE='2a0d5aa392c85a1dc12a1cdb423978e8500895b8'
DIGEST='8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'
SNAPSHOT='31835fbf4052046f393059d4fe797b7cb82852e99f540d1370e61829ad994b71'
EPOCH='8b153538-1523-4987-a456-6cbea0d345ee'
PAIRS=((prior.SOURCE,SOURCE),(prior.DIGEST,DIGEST),('Pg813','Pg856'),('PG813','PG856'),('pg813','pg856'),
 ('failed949-tools-v2','failed-done-tools-v1'),('failed949-recovery-v2','failed-done-recovery-v1'),
 ('PG796','PG832'),('pg796','pg832'),('7ea672e8a76c4a4a8a7994652366a4cc','9c08566fff9945a492eaae25559c3084'),
 ('3123795','3417355'),('155954641282','171417627031'),('15595464','17141762'),
 ('3342473','3506798'),('6220dab5a87945d2bb144cb9e14f5f14','eeb1b35ca3214176adae5d45bb6432ab'),('15742135','17241379'),
 ('3344741','3507964'),('02ae69dca0514d8c917831eee3ca82b6','8c46100f289f47b9a24d2c12bd443ba2'),('15743589','17242685'),
 ('3350579','3509997'),('42e945fbd2894199b7dfca297c989627','87dd86b0f2c243198a05ae36903fdefa'),('15746848','17244888'),
 ('3158873','3427249'),('cb2f7a6c4beb4420a0e96adb65fb6f11','9a576ea327854479a3196fe41b2c0a61'),('15613132','17151412'),
 ('pg812-current-timeout-v4','pg855-doneafter-current-v1'),(prior.SNAPSHOT,SNAPSHOT))
def bind(raw):
    for a,b in PAIRS: raw=raw.replace(a,b)
    return raw
def java():
    raw=bind(prior.java())
    raw=raw.replace('static final String EPOCH="'+prior.EPOCH+'"','static final String EPOCH="'+EPOCH+'"')
    begin=raw.index('  static Set<String> names()');end=raw.index('  static final class References',begin)
    names=bind(prior.NAMES).replace('n.add(EPOCH+".API.start.intent");','')
    names=names.replace('"e9f11f1c-f087-458a-aad0-8c1e4e140571",EPOCH','"e9f11f1c-f087-458a-aad0-8c1e4e140571","'+prior.EPOCH+'",EPOCH')
    names=names.replace('n.remove(EPOCH+".API.start.intent");','')
    raw=raw[:begin]+names+raw[end:]
    begin=raw.index('  static RootFailedStartRecovery.PairEvidence pair(');end=raw.index('  static boolean parentValue(',begin)
    cohort=raw[begin:end]
    cohort=cohort.replace('static RootFailedStartRecovery.PairEvidence pair(', 'static void validateCohort(')
    cohort=cohort[:cohort.index('    return new RootFailedStartRecovery.PairEvidence')]+ '  }\n'
    raw=raw[:begin]+cohort+raw[end:]
    raw=raw.replace('names().size()==44','names().size()==47').replace('retiredNames().size()==43','retiredNames().size()==47').replace('rows()==554','rows()==564')
    marker='require(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().isEmpty()'
    assert raw.count(marker)==1
    raw=raw.replace(marker,'require(completedValue(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())),epoch.activation())')
    raw=raw.replace('&& new RunReferenceRepository(db).read(epoch.activation().run()).identityConsistent());',
      '&& new RunReferenceRepository(db).read(epoch.activation().run()).identityConsistent());\n    require(Pg410KnownAuthRecovery.hash(Files.readAllBytes(Path.of("/var/lib/schubert-nk/maintenance/attempts/021111b4-6de5-4733-917d-5ac176240ffc.done"))).equals("37356ff23d0393924c22079bd4c87fce7c3070155d84704fb1cb143e7b1c60a5"));')
    marker='  static void pending('
    raw=raw.replace(marker,r'''  static boolean completedValue(MaintenanceRunFiles.StartupOriginal original,MaintenanceActivation expected){
    return original!=null && expected!=null && original.activation().equals(expected)
      && original.completed().isPresent() && original.completed().orElseThrow().activation().equals(expected);
  }
'''+marker)
    raw=raw.replace('phase="PENDING_ORIGINAL"','phase="COMPLETED_ORIGINAL"')
    raw=raw.replace('var pair=pair(invalid,permit,startup);','')
    raw=raw.replace('phase="HELPER_LIVE_VERIFY";helper("verify");', 'validateCohort(epoch,permit,startup);phase="HELPER_LIVE_VERIFY";helper("verify");')
    begin=raw.index('    phase="PUBLICATION_QUARANTINE";');end=raw.index('    save("observations.private"',begin)
    raw=raw[:begin]+'''    require(actualNames().equals(names())&&names().size()==47&&invalid.equals(files.current()));
    helper("retired");pulse();parent();pulse();signed();pulse();pending(invalid,db);
'''+raw[end:]
    raw=raw.replace('existingPairRetired=true','intentRetirement0=true')
    assert 'quarantinePair' not in raw and 'retirePair' not in raw and 'pair(' not in raw
    return raw
def helper():
    raw=bind(prior.helper()).replace(prior.EPOCH,EPOCH).replace('==554','==564').replace('== 554','== 564')
    # No intent exists. The canonical revoke changes only epoch.current; no pseudo-retirement.
    assert "elif action=='retired':require(newnames==oldnames-intents)" in raw
    raw=raw.replace("elif action=='retired':require(newnames==oldnames-intents)","elif action=='retired':require(newnames==oldnames)")
    raw=raw.replace("intents={startup+'/"+EPOCH+".API.start.intent',startup+'/"+EPOCH+".WEB.start.intent'}","intents=set()")
    ast.parse(raw); return raw
def java_test():
    return (R/'Pg856FailedRecoveryTest.java').read_text()
