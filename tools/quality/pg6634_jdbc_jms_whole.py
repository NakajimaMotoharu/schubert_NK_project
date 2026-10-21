"""One necessary integrated graph/cleanup regression, not selected-PASS addition."""
import inspect
import json
import subprocess
import pg6188_native_ownership_whole as base
import pg6626_jms_secondary_selected as selected

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
OLD='f39de2986cbe0dc4a552f64d55ac723002cc77f6'
LABEL='PG6634'
SLOT='pg6634-jdbc-jms-six-v1'
QSHA=None  # Freeze only after the genuine original PG6630/86 qualification exists.


def original_source():
    source=json.loads((W/selected.SLOTS['green']/'begin.safe.json').read_bytes())['source']
    selected.guard_source(source,'green')
    return source


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,
           'original_source':original_source,'prerequisites':prerequisites}
    for name in ('declared_inventory','server_source','driver_source','main'):
        raw=inspect.getsource(getattr(base,name))
        for before,after in (('4023','4158'),('605','635'),('pg6188','pg6634')):raw=raw.replace(before,after)
        exec(compile(raw,'<integrated4158 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)


def driver_source(fresh):
    raw=definitions()['driver_source'](fresh)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Required integrated graph/owned-cleanup Production change: SS312/SSC328329330; '
      'JDBC transaction, borrowed repos, auth, readiness, catalog/API domains, inspectors, Web '
      'manual/session and JMS secondary/duplicate pre-fatal. All selected originals qualified '
      'before this one fresh source4158/635/1667 whole; old4073 case identities only, never PASS '
      'addition. All old Test bodies unchanged plus85 methods in21 new suites. Allsix format '
      'and Java25 compile/null/static; ordinary isolated temporary DB/JMS/HTTP/finite children '
      'only. No actual VM/current/Root/cohort/intent/permit/key/native operation. Same-source '
      'original XML/Jar/all851/1667 and counters require independent qualification. Formal, '
      'native, CHR, F03 and full four100 remain separate; no refusal exemption inferred.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw',
                               'tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('all original selected Main/Test/gates fixed during whole and reader')
    qp=BASE/'PG6632-jms-secondary-qualification-v1/manifest.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze genuine original86 qualification first')
    q=json.loads(qp.read_bytes());private=W/'pg6632-jms-secondary-qualification-v1/manifest.safe.json'
    if not(q['source']==source and q['actualExit']==0 and (q['tests'],q['suites'],q['physicalMain'])==(86,17,1667)
           and sha(private)==q['privateManifestSha256']):raise ValueError('actual original86 XML/Jar/all Main')
    proof=json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:
        raise ValueError('all851 current Main match selected original')
    changes=subprocess.check_output(['git','diff','--name-status',OLD,source,'--',
      ':(glob)src/*/src/test/java/**/*Test.java'],cwd=ROOT,text=True).splitlines()
    if len(changes)!=21 or any(not row.startswith('A\t') for row in changes):
        raise ValueError('exact21 added suites; every historical Test byte fixed')
    owners=subprocess.check_output(['git','diff','--name-only',OLD,source,'--',
      ':(glob)src/*/src/main/java/**/*.java'],cwd=ROOT,text=True).splitlines()
    if len(owners)!=45:raise ValueError('exact reviewed45 grouped Main owners since4073')
    declared_inventory()


def main():
    scope=definitions();scope['main'].__globals__['driver_source']=driver_source
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
