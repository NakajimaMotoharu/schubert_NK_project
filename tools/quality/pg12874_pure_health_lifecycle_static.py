"""Two whole API duration/policy Tests PMD/Checkstyle and same-source six-module SpotBugs; product PT0."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE='105fd644e90918945607b3ac3e4962843c7762bf'
NORMAL_SHA='bc906632f1a362e7d688ac472784c1e4438008421799f7fec927dad8c818b52a'
HOST_SHA='629cb07806640f9e8a2ec1c35306ca1fccf1b0471e0e16bf6aab5eaadf471330'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12874-pure-health-lifecycle-static-v1'
OUT=data.BASE/'PG12874-pure-health-lifecycle-static-v1'


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12870-pure-health-lifecycle-six-compile-v1/manifest.json',NORMAL_SHA)
    h=data.read_checked(data.BASE/'PG12873-pure-health-lifecycle-host-v2/manifest.json',HOST_SHA)
    p=data.read_checked(data.BASE/'PG12868-pure-health-lifecycle-plan-v1/manifest.json','e3b10e5565ac1d369b3693a5dc3c5b5c80f8022f8d29226d23c578721b64715b')
    assert n['source']==h['source']==SOURCE and n['actualExit']==n['testsExecuted']==h['actualExit']==0 and h['observedTestExecutions']==38
    sources={**p['wholeTestSourceHashes'],**{path:sha for path,sha in p['eligibilityClosureSourceHashes'].items() if path.endswith(('/AlertLifecycle.java','/TimedFilesystemMonitor.java','/FilesystemHealthObservation.java','/FilesystemHealthMonitor.java'))}};assert len(sources)==9
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
