"""Read-only original1038/126 qualification; preserve original inventory refusal1 and all artifacts."""
import json
import os
import re
import xml.etree.ElementTree as ET
import pg5304_permit_intent_selected as entry
import pg5311_repeated_inventory as repeats
import pg5122_root_elf_public as public
from pg5306_permit_intent_bytecode import SOURCE

RUN=entry.selected.ROOT.parent/'pgpt-runs/PG379/pg5304-permit-intent-green-v1'


def main():
    entry.configure();original=RUN/'manifest.safe.json'
    result=json.loads(original.read_bytes());begin=json.loads((RUN/'begin.safe.json').read_bytes())
    if result['actualExit']!=1 or result['phaseExits']!=[0,0] or result['reasons']!=['exact selected case inventory incomplete']:
        raise ValueError('only exact original inventory refusal, not PT/static failure')
    if result['sourceSnapshot']!=SOURCE or begin['sourceSnapshot']!=SOURCE:
        raise ValueError('fixed original source only')
    if entry.selected.sha(RUN/'source.tar')!=begin['archiveSha256']:
        raise ValueError('original immutable source archive changed')
    if any(entry.selected.sha(RUN/'source'/p)!=h for p,h in begin['inputs'].items()):
        raise ValueError('original fixed source inputs changed')
    if any(entry.selected.sha(RUN/p)!=h for p,h in result['logSha256'].items()):
        raise ValueError('original logs changed')
    expected={};base_expected={};suites={**entry.selected.SUITES,**entry.selected.PENDING_SUITES,
        'dev.codex.schubert.nk.batch.file.RootEntryRejectionTest':'batch',**entry.selected.storage_suites(),**entry.extra_suites()}
    aliases=entry.aliases.invocation_aliases();declared=entry.repetitions()
    for name,module in suites.items():
        source=(RUN/'source'/('src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java')).read_text()
        normal=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',source)
        if len(normal)!=source.count('@Test') or len(normal)!=len(set(normal)):
            raise ValueError('all exact normal source declarations')
        base=entry.selected.expected_invocations(normal,aliases.get(name,{}),source)
        base_expected[name]=base;expected[name]=repeats.expected(base,declared.get(name,{}),source)
    if base_expected!=begin['expectedMethods'] or set(declared)-set(suites):
        raise ValueError('original expected base inventory must remain unchanged')
    actual={};xml={};static={}
    for module in entry.selected.BUILT:
        target=RUN/('source/src/schubert-nk-'+module+'/target')
        for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            suite=ET.parse(path).getroot();name=suite.get('name')
            if name in actual or any(suite.get(k)!='0' for k in ('failures','errors','skipped')):
                raise ValueError('duplicate or nonzero XML FES')
            if any(suite.findall('.//'+tag) for tag in ('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')):
                raise ValueError('non-success XML invocation')
            actual[name]=sorted(c.get('name') for c in suite.findall('testcase'));xml[name]=entry.selected.sha(path)
        static[module]=len(ET.parse(target/'spotbugsXml.xml').getroot().findall('.//BugInstance'))
    if actual!=expected or actual!=result['actualMethods'] or xml!=result['xmlSha256']:
        raise ValueError('all original XML/source repetitions must match exactly')
    if len(actual)!=126 or sum(map(len,actual.values()))!=1038 or any(static.values()) or static!=result['freshStatic']:
        raise ValueError('exact1038/126 and static three0 required')
    report=RUN/'source/src/schubert-nk-storage/target/site/jacoco/jacoco.xml'
    four={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}
        for c in ET.parse(report).getroot().findall('counter') if c.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    if len(four)!=4 or any(v['missed'] for v in four.values()) or four!=result['storageFourCounters']:
        raise ValueError('all original current storage four100 required')
    if entry.selected.main_delta(RUN/'source','factory')!=result['mainDelta']:
        raise ValueError('original764 physical Main changed')
    qualified={**result,'actualExit':0,'reasons':[],'originalRunnerActualExit':1,
        'originalManifestSha256':entry.selected.sha(original),'qualifiedExpectedMethods':expected,
        'qualifiedInvocationAliases':aliases,'qualifiedInvocationRepetitions':declared,
        'qualificationKind':'READ_ONLY_ORIGINAL_1038_LITERAL_REPEAT10_NO_REPLAY',
        'logicalTestMethods':1029,'repeatedLogicalMethods':1,'repeatedInvocations':10,
        'bugs':['BUG1438'],'ykt':['YKT1202']}
    public.validate_separate_qualification(qualified,result,entry.selected.sha(original))
    os.umask(0o077)
    with(RUN/'qualification.safe.json').open('x') as f:
        json.dump(qualified,f,ensure_ascii=False,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'originalRunnerExit':1,'qualificationExit':0,'tests':1038,'suites':126,
        'logicalTestMethods':1029,'repeatedInvocations':10,'sha256':entry.selected.sha(RUN/'qualification.safe.json')}))


if __name__=='__main__':main()
