"""Read-only requalification of original684, never repeat Maven or rewrite original exit1."""
import json
import os
import xml.etree.ElementTree as ET
import pg5192_durable_worker_selected as entry
import pg5194_durable_worker_bytecode as byteproof

RUN=byteproof.RUN


def main():
    entry.configure()
    original=RUN/'manifest.safe.json'
    result=json.loads(original.read_bytes());begin=json.loads((RUN/'begin.safe.json').read_bytes())
    if result['actualExit']!=1 or result['phaseExits']!=[0,0] or result['reasons']!=[
        'declared semantic changes plus explicitly bounded nested debug candidates only']:
        raise ValueError('only known post-inventory refusal, never conceal PT or static failure')
    if result['sourceSnapshot']!=begin['sourceSnapshot'] or result['sourceSnapshot']!='805c166c2868e2cc5997aa73cd33ef125cb873a2':
        raise ValueError('immutable original source805c only')
    if any(entry.selected.sha(RUN/'source'/p)!=h for p,h in begin['inputs'].items()):
        raise ValueError('original inputs changed')
    if any(entry.selected.sha(RUN/p)!=h for p,h in result['logSha256'].items()):
        raise ValueError('original logs changed')
    actual={};xml={};static={}
    for module in entry.selected.BUILT:
        target=RUN/('source/src/schubert-nk-'+module+'/target')
        for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            suite=ET.parse(path).getroot();name=suite.get('name')
            if name in actual or any(suite.get(k)!='0' for k in ('failures','errors','skipped')):
                raise ValueError('duplicate or nonzero XML FES')
            if any(suite.findall('.//'+tag) for tag in ('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')):
                raise ValueError('non-success XML case')
            actual[name]=sorted(c.get('name') for c in suite.findall('testcase'))
            xml[name]=entry.selected.sha(path)
        static[module]=len(ET.parse(target/'spotbugsXml.xml').getroot().findall('.//BugInstance'))
    if actual!=begin['expectedMethods'] or actual!=result['actualMethods'] or xml!=result['xmlSha256']:
        raise ValueError('actual original XML inventory/hash changed')
    if len(actual)!=85 or sum(map(len,actual.values()))!=684 or any(static.values()) or static!=result['freshStatic']:
        raise ValueError('exact684/85 and three fresh static0')
    report=RUN/'source/src/schubert-nk-storage/target/site/jacoco/jacoco.xml'
    four={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}
          for c in ET.parse(report).getroot().findall('counter') if c.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    if set(four)!={'LINE','METHOD','CLASS','BRANCH'} or any(v['missed'] for v in four.values()) or four!=result['storageFourCounters']:
        raise ValueError('original storage four100')
    qualified={**result,'actualExit':0,'reasons':[],'mainDelta':entry.selected.main_delta(RUN/'source','factory'),
        'originalRunnerActualExit':1,'originalManifestSha256':entry.selected.sha(original),
        'qualificationKind':'READ_ONLY_ORIGINAL_JOB_684_NO_REPLAY','bugs':['BUG1430'],'ykt':['YKT1194']}
    byteproof.main(result=qualified)
    proof=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5194-durable-worker-bytecode-v1/manifest.json'
    qualified['bytecodeProofSha256']=entry.selected.sha(proof)
    os.umask(0o077)
    with(RUN/'qualification.safe.json').open('x') as f:
        json.dump(qualified,f,ensure_ascii=False,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'originalActualExit':1,'qualificationActualExit':0,'tests':684,'suites':85,
        'sha256':entry.selected.sha(RUN/'qualification.safe.json'),'noTestReplays':True}))


if __name__=='__main__':main()
