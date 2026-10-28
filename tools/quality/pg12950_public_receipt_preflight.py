"""Before source freeze: explicit pure policy four-file PMD/Checkstyle diagnostic only, PT0."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg12950-public-receipt-preflight-v1'
OUT = data.BASE/'PG12950-public-receipt-preflight-v1'

def main():
    invocation = capture(__file__); assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG12938-login-policy-six-compile-v1/manifest.json','f65a05a93b6a857e21602222b5a9f5287a92b185cf6b540792c5bf8d7a10cac2')
    h = data.read_checked(data.BASE/'PG12940-login-policy-host-v1/manifest.json','3cf0b7bab17d85a075c1ad007cf12ee7b2536706b062b3dac3dd32b17766dfca')
    assert normal['source'] == h['source'] == 'e49eb0cc84c62ace468cf389938b23f3e56ba520'
    assert normal['actualExit'] == h['actualExit'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in normal['begin']['inputHashes'].items())
    paths = ['src/schubert-nk-api/src/'+kind+'/java/dev/codex/schubert/nk/api/application/question/'+name+'.java' for kind,name in [('main','QuestionReceiptId'),('main','QuestionReceiptIdGenerator'),('test','QuestionReceiptIdTest'),('test','QuestionReceiptRecoveryTest')]]
    hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    static = runner.TC/'static-gates-20261015'; rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    deps = h['begin']['dependencyHashes']
    assert all(data.sha(Path(p).read_bytes()) == digest for p,digest in deps.items())
    SLOT.mkdir(); runner.SLOT = SLOT; listing = SLOT/'source-list.txt'
    with listing.open('x') as f: f.write(''.join(str(data.ROOT/p)+'\n' for p in paths))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {}
    stages['pmd'] = runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT)
    stages['checkstyle'] = runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT)
    reports = {}
    for name,tag in [('pmd','violation'),('checkstyle','error')]:
        p = SLOT/(name+'.xml'); root = ET.parse(p).getroot()
        findings = [x for x in root.iter() if x.tag.rpartition('}')[2] == tag]
        errors = [x for x in root.iter() if x.tag.rpartition('}')[2] in ['error','configerror']] if name == 'pmd' else []
        reports[name] = dict(findings=len(findings),processingErrors=len(errors),sha256=data.sha(p.read_bytes()))
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == digest for p,digest in {**tools,**deps}.items())
    passed = not any(v['timedOut'] for v in stages.values()) and stages['pmd']['actualExit'] in [0,4] and stages['checkstyle']['actualExit'] == 0 and all(v['processingErrors'] == 0 for v in reports.values())
    raw_gate = all(v['findings'] == v['processingErrors'] == 0 for v in reports.values())
    verify(invocation); OUT.mkdir()
    for name in reports:
        with (OUT/(name+'.xml')).open('xb') as f: f.write((SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,source=None,baseSource=normal['source'],candidateSourceHashes=hashes,
        invocation=invocation,reports=reports,stages=stages,toolAndRuleHashes=tools,productTestsExecuted=0,
        candidatePreflightOnly=True,diagnosticOnlyRawFindingsRetained=True,rawGatePassed=raw_gate,normalCompilationOrRuntimeQualificationInferred=False,newAccepted=0,externalActions=0))
    print(json.dumps(dict(actualExit=0 if passed else 1,reports=reports,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__': main()
