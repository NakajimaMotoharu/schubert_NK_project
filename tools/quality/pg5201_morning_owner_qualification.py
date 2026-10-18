"""Read original688 once; explicit @TempDir aliases, original exit1 kept, no Maven replay."""
import json
import os
import re
import xml.etree.ElementTree as ET
import pg5200_morning_owner_selected as entry
import pg5202_morning_owner_bytecode as byteproof

RUN=byteproof.RUN


def normalized(methods,aliases):
    if len(set(aliases.values()))!=len(aliases):raise ValueError('one-to-one invocation map')
    if not set(aliases)<=set(methods):raise ValueError('missing original aliased invocation')
    names=[aliases.get(name,name) for name in methods]
    if len(set(names))!=len(names):raise ValueError('alias collision with original case')
    return sorted(names)


def main():
    entry.configure();original=RUN/'manifest.safe.json'
    result=json.loads(original.read_bytes());begin=json.loads((RUN/'begin.safe.json').read_bytes())
    if result['actualExit']!=1 or result['phaseExits']!=[0,0] or result['reasons']!=['exact selected case inventory incomplete']:
        raise ValueError('only exact known invocation-name refusal, not failed PT/static')
    if result['sourceSnapshot']!=begin['sourceSnapshot'] or result['sourceSnapshot']!='d659d23bf669d092e2e99f0bac8411aac2e1389f':
        raise ValueError('immutable original source d659 only')
    if any(entry.selected.sha(RUN/'source'/p)!=h for p,h in begin['inputs'].items()):
        raise ValueError('original inputs changed')
    if any(entry.selected.sha(RUN/p)!=h for p,h in result['logSha256'].items()):
        raise ValueError('original logs changed')
    aliases=entry.invocation_aliases();actual={};xml={};static={}
    suites={**entry.selected.SUITES,**entry.selected.PENDING_SUITES,**entry.selected.storage_suites(),
        'dev.codex.schubert.nk.batch.file.RootEntryRejectionTest':'batch',**entry.extra_suites()}
    for suite,mapping in aliases.items():
        source=(RUN/'source'/('src/schubert-nk-'+suites[suite]+'/src/test/java/'+suite.replace('.','/')+'.java')).read_text()
        for observed,canonical in mapping.items():
            if observed!=canonical+'(Path)' or not re.search(r'void\s+'+re.escape(canonical)+r'\(\s*@TempDir\s+Path\s+temporary\s*\)',source):
                raise ValueError('exact declared @TempDir Path parameter only')
    for module in entry.selected.BUILT:
        target=RUN/('source/src/schubert-nk-'+module+'/target')
        for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            suite=ET.parse(path).getroot();name=suite.get('name')
            if name in actual or any(suite.get(k)!='0' for k in ('failures','errors','skipped')):
                raise ValueError('duplicate or nonzero XML FES')
            if any(suite.findall('.//'+tag) for tag in ('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')):
                raise ValueError('non-success XML case')
            actual[name]=sorted(c.get('name') for c in suite.findall('testcase'));xml[name]=entry.selected.sha(path)
        static[module]=len(ET.parse(target/'spotbugsXml.xml').getroot().findall('.//BugInstance'))
    names={name:normalized(methods,aliases.get(name,{})) for name,methods in actual.items()}
    if names!=begin['expectedMethods'] or actual!=result['actualMethods'] or xml!=result['xmlSha256']:
        raise ValueError('actual source/XML invocation inventory/hash changed')
    if len(actual)!=85 or sum(map(len,actual.values()))!=688 or any(static.values()) or static!=result['freshStatic']:
        raise ValueError('exact688/85 and three fresh static0')
    report=RUN/'source/src/schubert-nk-storage/target/site/jacoco/jacoco.xml'
    four={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}
        for c in ET.parse(report).getroot().findall('counter') if c.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    if set(four)!={'LINE','METHOD','CLASS','BRANCH'} or any(v['missed'] for v in four.values()) or four!=result['storageFourCounters']:
        raise ValueError('original storage four100')
    delta=entry.selected.main_delta(RUN/'source','factory')
    if delta!=result['mainDelta']:raise ValueError('original764 Main changed')
    qualified={**result,'actualExit':0,'reasons':[],'qualifiedInvocationAliases':aliases,
        'originalRunnerActualExit':1,'originalManifestSha256':entry.selected.sha(original),
        'qualificationKind':'READ_ONLY_ORIGINAL_688_EXPLICIT_PATH_SIGNATURES','bugs':['BUG1431'],'ykt':['YKT1195']}
    byteproof.main(result=qualified)
    proof=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5202-morning-owner-bytecode-v1/manifest.json'
    qualified['bytecodeProofSha256']=entry.selected.sha(proof)
    os.umask(0o077)
    with(RUN/'qualification.safe.json').open('x') as f:
        json.dump(qualified,f,ensure_ascii=False,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'originalActualExit':1,'qualificationActualExit':0,'tests':688,'suites':85,
        'sha256':entry.selected.sha(RUN/'qualification.safe.json'),'noTestReplays':True}))


if __name__=='__main__':main()
