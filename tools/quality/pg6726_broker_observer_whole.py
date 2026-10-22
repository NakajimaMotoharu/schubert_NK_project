"""Necessary same-oracle4184 whole after two ordinary callback definitions are shared."""
import inspect
import json
import subprocess
import pg6706_broker_cleanup_whole as prior
from pg6722_broker_noop_equivalence import PATHS

ROOT,W,BASE,sha=prior.ROOT,prior.W,prior.BASE,prior.sha
OLD='d48f8ebf8ed4047763c77fe487c44f7caa03e8f8'
LABEL='PG6726'
SLOT='pg6726-broker-observer-six-v1'
QSHA='70670e2540807bf2c8357d285d50c9aa0a19434b04406cfab8b344ef4dae2fd6'
original_source=prior.original_source


def definitions():
    scope={**vars(prior),'OLD':OLD,'LABEL':LABEL,'SLOT':SLOT,
           'original_source':original_source,'prerequisites':prerequisites}
    raw=inspect.getsource(prior.definitions).replace("'pg6706'","'pg6726'")
    exec(compile(raw,'<same-oracle4184 definitions>','exec'),scope)
    return scope['definitions']()


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)


def driver_source(fresh):
    raw=definitions()['driver_source'](fresh)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Necessary PG-D500/BUG1610 ordinary callback deduplication regression, not a '
      'confirmation replay of original4184. Two Main and six old ordinary callsites expand '
      'exactly to prior tokens; same all old independent Test bytes. Original127 qualification '
      'and source equivalence first. Full4184/643/851source1667physical, allsix format-beforePT, '
      'compile/null/static and same finite own fixtures. No actual VM/current/Root/failed cohort/'
      'intent/permit/key/native qualification operation, no retry of refused operations. '
      'Original terminal/XML/Jar/current counters/static/trace require independent qualification; '
      'prior native/formal acceptance not imported.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):
        raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('all Main/Test/gates fixed from original127')
    qp=BASE/'PG6724-broker-observer-qualification-v1/manifest.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze actual observer127 qualification first')
    q=json.loads(qp.read_bytes());pp=W/'pg6724-broker-observer-qualification-v1/manifest.safe.json'
    if not(q['source']==source and q['actualExit']==0 and (q['tests'],q['suites'],q['physicalMain'])==(127,33,1667)
           and sha(pp)==q['privateManifestSha256']):raise ValueError('genuine current127/all Main/Jars')
    proof=json.loads(pp.read_bytes())
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:
        raise ValueError('all851 current Main fixed')
    if set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())!=set(PATHS):
        raise ValueError('two necessary Main only; every historical Test byte fixed')
    e=json.loads((W/'pg6722-observer-expansion-proof-v1/manifest.safe.json').read_bytes())
    if e['actualExit']!=0 or e['source']!=source or e['priorSource']!=OLD:
        raise ValueError('same-source exact ordinary observer expansion proof')
    declared_inventory()


def main():
    scope=definitions();scope['main'].__globals__['driver_source']=driver_source
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
