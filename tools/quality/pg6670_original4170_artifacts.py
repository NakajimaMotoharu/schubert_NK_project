"""Original4170 XML/Jar/physical qualification, never a replay to fill missing results."""
import inspect
import json
import subprocess
from types import SimpleNamespace
import pg6042_original3976_artifacts as reader
import pg6198_original4024_artifacts as prior
from pg6668_consumer_audit_whole import original_source,OLD,ROOT,W,BASE,sha


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote)
    anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:raise ValueError('one original export/counter guard')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6668', (4170, 638, 1667), 6))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6668')",1)
    compile(raw,'<original4170 reader>','exec')
    return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one original coverage export guard')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6668')",1),'<original4170 collect>','exec'),scope)
    return scope['collect'](*args,**kwargs)


def definitions():
    scope={**vars(prior),'OLD':OLD,'original_source':original_source,
           'reader':SimpleNamespace(**{**vars(reader),'collect':collect})}
    for name in ('new_case_identities','main'):
        raw=inspect.getsource(getattr(prior,name))
        for before,after in (
          ('!=36','!=12'),('exact36','exact12'),('len(owners)!=13','len(owners)!=6'),('exact13','exact6'),
          ('pg6196-management-ownership-six-v1','pg6668-consumer-audit-six-v1'),
          ('PG6196-six-v1','PG6668-six-v1'),('PG6196','PG6668'),
          ('PG6118-current3988-cases','PG6634-current4158-cases'),
          ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23','658804678cc942c70ee498bc030d9833d8043994b43d8cffaf7fdf58accc5cb8'),
          ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47','7c698189b247c9ae75182f781a61a2b161aaf3709d0768367615cf97f06a0cb3'),
          ('PG6193-management-primary-qualification-v2','PG6666-consumer-graph-qualification-v2'),
          ('pg6193-management-primary-qualification-v2','pg6666-consumer-graph-qualification-v2'),
          ('(60,20)','(77,20)'),('source60','source77'),('[4024,605,1667]','[4170,638,1667]'),
          ('pg6198-original4024-artifacts-v1','pg6670-original4170-artifacts-v1'),
          ('PG6198-original4024-v1','PG6670-original4170-v1'),
          ('PG6668-current4024-cases','PG6668-current4170-cases')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<original4170 '+name+'>','exec'),scope)
    return scope


def new_case_identities(source):return definitions()['new_case_identities'](source)
def main():return definitions()['main']()


def read_whole():
    qp=BASE/'PG6668-current4170-cases/qualification.json';cp=qp.with_name('cases.json')
    rp=W/'pg6670-original4170-artifacts-v1/manifest.safe.json'
    op=W/'pg6668-consumer-audit-six-v1/manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes()) for p in (qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']==original_source()
           and (q['tests'],q['suites'],q['mainClasses'])==(4170,638,1667)
           and q['returnedOriginalTerminalExact'] and q['currentOriginalXmlQualified']
           and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed']
           and r['originalManifestSha256']==sha(op) and r['publicQualificationSha256']==sha(qp)
           and r['publicCasesSha256']==sha(cp)):
        raise ValueError('genuine original4170 terminal/receipt/XML required')
    if subprocess.check_output(['git','diff',q['productionSource'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('current Main/Test/gates fixed')
    current={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(current)!=851 or current!=q['allSourceHashes']:raise ValueError('all current851 exact Main bytes')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4170 or any(c['source']!=q['productionSource'] or c['result']!='PASS_ORIGINAL_XML' for c in cases):
        raise ValueError('all genuine current4170 case identities')
    return qp,q,cases


if __name__=='__main__':main()
