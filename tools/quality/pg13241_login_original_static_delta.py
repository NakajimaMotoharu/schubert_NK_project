"""One necessary source-only comparison of original Login Test under saved current static conditions."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import original_value, out
from f03_literal_batch_diagnostic_v3 import signature
import pg13237_business_delivery_literal_config as cfg
import pg9666_pagination_static as runner

OUT = data.BASE/'PG13241-login-original-static-delta-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13241-login-original-static-delta-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    failed = data.ROOT.parent/'pgpt-runs/PG379'/out(cfg,cfg.PREFLIGHT_NUMBER).name.lower()
    begin = json.loads((failed/'begin.safe.json').read_bytes());observed = json.loads((failed/'observed.safe.json').read_bytes())
    assert begin['candidateSourceHashes'] == observed['candidateSourceHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in begin['candidateSourceHashes'].items())
    original = next(r for r in original_value(cfg)['sources'] if r['path'].endswith('/LoginInboxServiceTest.java'))
    assert data.sha(original['text'].encode()) == cfg.PATHS[original['path']][0]
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**begin['toolAndRuleHashes'],**begin['dependencyHashes']}.items())
    SLOT.mkdir();runner.SLOT = SLOT;target = SLOT/'original'/Path(original['path']).name
    target.parent.mkdir()
    with target.open('x') as stream:stream.write(original['text'])
    listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:stream.write(str(target)+'\n')
    command = json.loads((failed/'pmd-begin.safe.json').read_bytes())['command']
    assert command.count('--file-list') == command.count('--report-file') == 1
    command[command.index('--file-list')+1] = str(listing);command[command.index('--report-file')+1] = str(SLOT/'pmd.xml')
    data.write(SLOT/'begin.safe.json',dict(invocation=invocation,baseSource=cfg.BASE_SOURCE,originalPath=original['path'],originalSha256=original['sha256'],
        candidateSourceHashes=begin['candidateSourceHashes'],toolAndRuleHashes=begin['toolAndRuleHashes'],dependencyHashes=begin['dependencyHashes'],command=command,productTestsExecuted=0,targetRuntimeInvoked=False))
    stage = runner.step('original-pmd',command,SLOT);assert stage['actualExit'] in [0,4] and not stage['timedOut']
    root = ET.parse(SLOT/'pmd.xml').getroot();assert not [x for x in root.iter() if x.tag.rpartition('}')[2] in ['error','configerror']]
    rows = [dict(attributes=dict(x.attrib),message=x.text.strip()) for x in root.iter() if x.tag.rpartition('}')[2] == 'violation']
    methods = {'jdbcOwnerCommitsOnlyCompleteBusinessResults','permanentProtocolNeedsConfirmedRollbackAndClose'}
    before = [r for r in rows if r['attributes']['rule'] == 'CloseResource' and r['attributes'].get('method') in methods and r['attributes'].get('variable') == 'connection']
    after = [r for r in observed['retainedRawFindings'] if r['path'] == original['path'] and r['attributes']['rule'] == 'CloseResource' and r['attributes'].get('method') in methods and r['attributes'].get('variable') == 'connection']
    assert len(after) == 2
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in begin['candidateSourceHashes'].items()) and data.sha(target.read_bytes()) == original['sha256']
    verify(invocation);OUT.mkdir()
    with (OUT/'original-pmd.xml').open('xb') as stream:stream.write((SLOT/'pmd.xml').read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=cfg.BASE_SOURCE,invocation=invocation,stages=[stage],originalSourceSha256=original['sha256'],originalReportSha256=data.sha((OUT/'original-pmd.xml').read_bytes()),
        originalUnderCurrentConditions=before,currentCandidateFindings=after,originalHasSameTwo=(len(before) == 2 and {signature(r['attributes'],r['message']) for r in before} == {signature(r['attributes'],r['message']) for r in after}),
        originalGlobalFindingsRewritten=False,newProductSourceRunClaim=False,productTestsExecuted=0,targetRuntimeInvoked=False,externalActions=0,newAccepted=0,whole451Accepted=False))
    print(json.dumps(dict(manifestSha256=data.sha((OUT/'manifest.json').read_bytes()),originalRelevant=len(before),candidateRelevant=len(after))))

if __name__ == '__main__':main()
