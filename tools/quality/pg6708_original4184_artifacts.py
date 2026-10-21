"""Read the original4184 XML/Jar/physical artifacts, never re-execute missing tests."""
import inspect
import json
import subprocess
from types import SimpleNamespace
import pg6042_original3976_artifacts as reader
import pg6198_original4024_artifacts as prior
from pg6706_broker_cleanup_whole import original_source,OLD,ROOT,W,BASE,sha


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote)
    anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:
        raise ValueError('one original export/counter guard')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6706', (4184, 643, 1667), 8))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6706')",1)
    compile(raw,'<original4184 reader>','exec')
    return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one original coverage export guard')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6706')",1),'<original4184 collect>','exec'),scope)
    return scope['collect'](*args,**kwargs)


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source,
           'reader':SimpleNamespace(**{**vars(reader),'collect':collect})}
    for name in ('new_case_identities','main'):
        raw=inspect.getsource(getattr(prior,name))
        for before,after in (
          ('!=36','!=14'),('exact36','exact14'),('len(owners)!=13','len(owners)!=8'),('exact13','exact8'),
          ('pg6196-management-ownership-six-v1','pg6706-broker-cleanup-six-v1'),
          ('PG6196-six-v1','PG6706-six-v1'),('PG6196','PG6706'),
          ('PG6118-current3988-cases','PG6668-current4170-cases'),
          ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','75a039af0e96adace67974c93354cfc175bfe1063b3ddb30908f3a3ad7894c45'),
          ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','fc752a7e746bfccf0d56494e57e678a4725731d58155acccf1945b488a0639ec'),
          ('PG6193-management-primary-qualification-v2','PG6712-broker-parent-qualification-v3'),
          ('pg6193-management-primary-qualification-v2','pg6712-broker-parent-qualification-v3'),
          ('(60,20)','(127,33)'),('source60','source127'),('[4024,605,1667]','[4184,643,1667]'),
          ('pg6198-original4024-artifacts-v1','pg6708-original4184-artifacts-v1'),
          ('PG6198-original4024-v1','PG6708-original4184-v1'),
          ('PG6706-current4024-cases','PG6706-current4184-cases')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<original4184 '+name+'>','exec'),scope)
    return scope


def new_case_identities(source):return definitions()['new_case_identities'](source)
def main():return definitions()['main']()


def read_whole():
    qp=BASE/'PG6706-current4184-cases/qualification.json';cp=qp.with_name('cases.json')
    rp=W/'pg6708-original4184-artifacts-v1/manifest.safe.json'
    op=W/'pg6706-broker-cleanup-six-v1/manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes()) for p in (qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']==original_source()
           and (q['tests'],q['suites'],q['mainClasses'])==(4184,643,1667)
           and q['returnedOriginalTerminalExact'] and q['currentOriginalXmlQualified']
           and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed']
           and r['originalManifestSha256']==sha(op) and r['publicQualificationSha256']==sha(qp)
           and r['publicCasesSha256']==sha(cp)):
        raise ValueError('genuine original4184 terminal/receipt/XML required')
    if subprocess.check_output(['git','diff',q['productionSource'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('current Main/Test/gates fixed')
    current={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(current)!=851 or current!=q['allSourceHashes']:raise ValueError('all current851 exact Main bytes')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4184 or any(c['source']!=q['productionSource'] or c['result']!='PASS_ORIGINAL_XML' for c in cases):
        raise ValueError('all genuine current4184 case identities')
    return qp,q,cases


if __name__=='__main__':main()
