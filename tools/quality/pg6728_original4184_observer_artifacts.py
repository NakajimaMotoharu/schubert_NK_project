"""Read genuine observer4184 artifacts; never re-run to replace missing or failed results."""
import inspect
import json
import subprocess
from types import SimpleNamespace
import pg6042_original3976_artifacts as reader
import pg6198_original4024_artifacts as prior
from pg6726_broker_observer_whole import original_source,OLD,ROOT,W,BASE,sha


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote)
    anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:
        raise ValueError('one original export/counter guard')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6726', (4184, 643, 1667), 2))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6726')",1)
    compile(raw,'<original observer4184 reader>','exec')
    return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one original coverage export guard')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6726')",1),'<observer4184 collect>','exec'),scope)
    return scope['collect'](*args,**kwargs)


def new_case_identities(source):
    if subprocess.check_output(['git','diff',OLD,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT):
        raise ValueError('all4184 independent Test inputs and oracles byte-fixed')
    return []


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source,'new_case_identities':new_case_identities,
           'reader':SimpleNamespace(**{**vars(reader),'collect':collect})}
    raw=inspect.getsource(prior.main)
    for before,after in (
      ('len(owners)!=13','len(owners)!=2'),('exact13','exact2'),
      ('pg6196-management-ownership-six-v1','pg6726-broker-observer-six-v1'),
      ('PG6196-six-v1','PG6726-six-v1'),('PG6196','PG6726'),
      ('PG6118-current3988-cases','PG6706-current4184-cases'),
      ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','13a7b5ae5007a63edf6bcc08dac4dcf0191cfcdf16f65f81a428e2ffc13c81d4'),
      ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','a863bd27af5f7b5d21c819f91f121cfcfb9fc5a9b7e81571103d666d14eddbba'),
      ('PG6193-management-primary-qualification-v2','PG6724-broker-observer-qualification-v1'),
      ('pg6193-management-primary-qualification-v2','pg6724-broker-observer-qualification-v1'),
      ('(60,20)','(127,33)'),('source60','source127'),('[4024,605,1667]','[4184,643,1667]'),
      ('pg6198-original4024-artifacts-v1','pg6728-original4184-observer-artifacts-v1'),
      ('PG6198-original4024-v1','PG6728-original4184-observer-v1'),
      ('PG6726-current4024-cases','PG6726-current4184-cases')):
        raw=raw.replace(before,after)
    exec(compile(raw,'<original observer4184 main>','exec'),scope)
    return scope


def main():return definitions()['main']()


def read_whole():
    qp=BASE/'PG6726-current4184-cases/qualification.json';cp=qp.with_name('cases.json')
    rp=W/'pg6728-original4184-observer-artifacts-v1/manifest.safe.json'
    op=W/'pg6726-broker-observer-six-v1/manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes()) for p in (qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']==original_source()
           and (q['tests'],q['suites'],q['mainClasses'])==(4184,643,1667)
           and q['returnedOriginalTerminalExact'] and q['currentOriginalXmlQualified']
           and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed']
           and r['originalManifestSha256']==sha(op) and r['publicQualificationSha256']==sha(qp)
           and r['publicCasesSha256']==sha(cp)):
        raise ValueError('genuine observer4184 terminal/receipt/XML required')
    if subprocess.check_output(['git','diff',q['productionSource'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('current Main/Test/gates fixed')
    current={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(current)!=851 or current!=q['allSourceHashes']:raise ValueError('all current851 exact Main bytes')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4184 or any(c['source']!=q['productionSource'] or c['result']!='PASS_ORIGINAL_XML' for c in cases):
        raise ValueError('all genuine current4184 case identities')
    return qp,q,cases


if __name__=='__main__':main()
