"""One required ordinary whole after SSC333334; no held deployed operation is admitted."""
import inspect
import json
import subprocess
import pg6188_native_ownership_whole as base
import pg6690_broker_parent_selected as selected
import pg6680_consumer_cleanup_selected as cleanup

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
OLD='f16f717d4e5338e7f5b44faef179ada0cf19aae0'
LABEL='PG6706'
SLOT='pg6706-broker-cleanup-six-v1'
QSHA=None  # Freeze only the genuinely returned original127 qualification.


def original_source():
    source=json.loads((W/selected.SLOTS['green']/'begin.safe.json').read_bytes())['source']
    selected.guard_source(source,'green')
    return source


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,
           'original_source':original_source,'prerequisites':prerequisites}
    for name in ('declared_inventory','server_source','driver_source','main'):
        raw=inspect.getsource(getattr(base,name))
        for before,after in (('4023','4184'),('605','643'),('pg6188','pg6706')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<integrated4184 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)


def driver_source(fresh):
    raw=definitions()['driver_source'](fresh)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Required grouped SSC333334 ordinary consumer/broker/parent cleanup graph correction. '
      'Original83 and127 qualifications, same all new/old Test bytes. Independent declarations '
      '4184/643/1667; historical4170 identities plus14 declarations are not imported PASS. '
      'Allsix format/compile/null/static; existing own finite temporary DB/JMS/HTTP/child fixtures. '
      'No actual VM/current/Root/failed cohort/intent/permit/key/native qualification operation. '
      'Original terminal/XML/Jar/all851/1667 and current four counters require independent '
      'original qualification; F03/CHR/native/formal and held refusal scopes remain separate.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):
        raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw',
                               'tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('same original127 Main/Test/gates fixed throughout whole and reader')
    qp=BASE/'PG6712-broker-parent-qualification-v3/manifest.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze actual original127 qualification first')
    q=json.loads(qp.read_bytes());private=W/'pg6712-broker-parent-qualification-v3/manifest.safe.json'
    if not(q['source']==source and q['actualExit']==0 and (q['tests'],q['suites'],q['physicalMain'])==(127,33,1667)
           and sha(private)==q['privateManifestSha256']):
        raise ValueError('actual original127 and all Main/Jars')
    proof=json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:
        raise ValueError('all851 current Main equal qualified original127')
    changes=subprocess.check_output(['git','diff','--name-status',OLD,source,'--',
      ':(glob)src/*/src/test/java/**/*Test.java'],cwd=ROOT,text=True).splitlines()
    if len(changes)!=5 or any(not row.startswith('A\t') for row in changes):
        raise ValueError('exact5 added independent suites; every historical Test byte unchanged')
    owners=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--',
      ':(glob)src/*/src/main/java/**/*.java'],cwd=ROOT,text=True).splitlines())
    if owners!=selected.MAINS|cleanup.MAINS:
        raise ValueError('exact8 grouped Main owners since original4170')
    declared_inventory()


def main():
    scope=definitions();scope['main'].__globals__['driver_source']=driver_source
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
