"""Changed Main/Test PMD/Checkstyle; four Thread raw findings remain and same-source six-module SpotBugs; product PT0."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE='af3f0f86d295ed721f5c1b41670ef224eb1d49e3'
NORMAL_SHA='5433fb79732be52686b99e8ec665a0ebb02752a90004cc777eedb3b4d31ba1c7'
HOST_SHA='ccb4a097f17f8e40779ca3f01f3ab79a876f0c33eccb94d27c31f54661562513'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12722-alert-threshold-static-v1'
OUT=data.BASE/'PG12722-alert-threshold-static-v1'


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12718-alert-threshold-six-compile-v1/manifest.json',NORMAL_SHA)
    h=data.read_checked(data.BASE/'PG12720-alert-threshold-host-v1/manifest.json',HOST_SHA)
    p=data.read_checked(data.BASE/'PG12716-alert-threshold-plan-v1/manifest.json','9f59c8646f08f5df99f88b599219640d5b4aa531b3e4c8dabeb733f5ae414500')
    assert n['source']==h['source']==SOURCE and n['actualExit']==n['testsExecuted']==h['actualExit']==0 and h['observedTestExecutions']==14
    sources={r['path']:r['sha256'] for r in p['sourceChanges']};assert len(sources)==2
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    static=runner.TC/'static-gates-20261015';rules=data.ROOT/'tools/quality/static'
    pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    toolhashes={str(f):data.sha(f.read_bytes()) for f in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    deps=h['begin']['dependencyHashes'];assert all(data.sha(Path(f).read_bytes())==digest for f,digest in {**deps,**toolhashes}.items())
    SLOT.mkdir();runner.SLOT=SLOT;listing=SLOT/'source-list.txt'
    with listing.open('x') as f:f.write(''.join(str(data.ROOT/path)+'\n' for path in sorted(sources)))
    java=str(runner.TC/'jdk-25.0.4/bin/java');stages={}
    stages['pmd']=runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT)
    stages['checkstyle']=runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT)
    mvn=runner.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
    stages['spotbugs-six']=runner.step('spotbugs-six',[str(mvn),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(runner.TC/'m2/repository'),'-pl',','.join('src/schubert-nk-'+r for r in ['protocol','storage','bootstrap','api','web','batch']),'-am','-DskipTests=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],Path(h['begin']['normalSnapshot']),timeout=600)
    OUT.mkdir();reports={}
    for name,tag in [('pmd','violation'),('checkstyle','error')]:
        b=(SLOT/(name+'.xml')).read_bytes();root=ET.fromstring(b)
        findings=[x for x in root.iter() if x.tag.rpartition('}')[2]==tag]
        errors=[x for x in root.iter() if x.tag.rpartition('}')[2] in ('error','configerror')] if name=='pmd' else []
        reports[name]=dict(findings=len(findings),processingErrors=len(errors),sha256=data.sha(b))
        with (OUT/(name+'.xml')).open('xb') as f:f.write(b)
    passed=all(v['actualExit']==0 and not v['timedOut'] for v in stages.values()) and all(v['findings']==v['processingErrors']==0 for v in reports.values())
    verify(invocation)
    value=dict(actualExit=0 if passed else 1,source=SOURCE,invocation=invocation,sourceHashes=sources,normalManifestSha256=NORMAL_SHA,hostManifestSha256=HOST_SHA,dependencyHashes=deps,toolAndRuleHashes=toolhashes,stages=stages,reports=reports,spotbugsSixExit=stages['spotbugs-six']['actualExit'],productTestsExecuted=0,suppressionsAdded=False,newAccepted=0,coverage=None,wholeF03Accepted=False)
    data.write(OUT/'manifest.json',value);print(json.dumps(dict(actualExit=value['actualExit'],reports=reports,spotbugsSixExit=value['spotbugsSixExit'],manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))));raise SystemExit(value['actualExit'])


if __name__=='__main__':main()
