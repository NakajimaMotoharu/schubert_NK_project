"""One grouped ordinary whole after qualified local audit and consumer corrections."""
import inspect
import json
import subprocess
import pg6188_native_ownership_whole as base
import pg6652_consumer_graph_selected as selected

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
OLD='2d4633fb25e2c47b2adcbada8c932aba727f20fd'
LABEL='PG6668'
SLOT='pg6668-consumer-audit-six-v1'
QSHA='dc608c847f6f03f31adabdb70b1fc28366472ae77d5c18f36c9a29f518de2edd'


def original_source():
    source=json.loads((W/selected.SLOTS['green']/'begin.safe.json').read_bytes())['source']
    selected.guard_source(source,'green')
    return source


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,
           'original_source':original_source,'prerequisites':prerequisites}
    for name in ('declared_inventory','server_source','driver_source','main'):
        raw=inspect.getsource(getattr(base,name))
        for before,after in (('4023','4170'),('605','638'),('pg6188','pg6668')):raw=raw.replace(before,after)
        exec(compile(raw,'<integrated4170 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)


def driver_source(fresh):
    raw=definitions()['driver_source'](fresh)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Required grouped Production correction, SS331332 local logger/terminal graph and '
      'ordinary JMS consumer fatal/confirmed rollback proof. Original31 and77 qualifications '
      'first, all old/new Test bytes fixed. Fresh4170/638/1667 complete source, not old4158 PASS '
      'plus12. Original4158 case identities retained; allsix format/compile/null/static and '
      'finite own temporary DB/JMS/HTTP/children only. No actual VM/current/Root/cohort/intent/'
      'permit/key/native operations. Original terminal/XML/Jar/all851/1667 and current four '
      'counters require independent original qualification; F03/CHR/native/formal separate. '
      'Held or unidentified refusal scopes are not retried and not exempted by this run.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw',
                               'tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('same original77 Main/Test/gates fixed throughout whole and reader')
    qp=BASE/'PG6666-consumer-graph-qualification-v2/manifest.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze actual original77 qualification first')
    q=json.loads(qp.read_bytes());private=W/'pg6666-consumer-graph-qualification-v2/manifest.safe.json'
    if not(q['source']==source and q['actualExit']==0 and (q['tests'],q['suites'],q['physicalMain'])==(77,20,1667)
           and sha(private)==q['privateManifestSha256']):raise ValueError('actual original77 and all Main/Jars')
    proof=json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:
        raise ValueError('all851 current Main equal qualified original77')
    changes=subprocess.check_output(['git','diff','--name-status',OLD,source,'--',
      ':(glob)src/*/src/test/java/**/*Test.java'],cwd=ROOT,text=True).splitlines()
    if len(changes)!=3 or any(not row.startswith('A\t') for row in changes):
        raise ValueError('exact3 added independent suites; every historical Test byte unchanged')
    owners=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--',
      ':(glob)src/*/src/main/java/**/*.java'],cwd=ROOT,text=True).splitlines())
    local='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java'
    if owners!=selected.MAINS|{local}:raise ValueError('exact6 grouped Main owners since original4158')
    declared_inventory()


def main():
    scope=definitions();scope['main'].__globals__['driver_source']=driver_source
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
