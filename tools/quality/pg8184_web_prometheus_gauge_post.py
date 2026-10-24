"""Independent original 50/7, exact 15-Main single-exec coverage, current-source static applicability."""
import copy
import datetime
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import xml.etree.ElementTree as ET

import pg8178_web_prometheus_gauge_host as contract
import pg6966_chr_adapter_host as host
import pg7032_monitoring_six_artifact_post as steps
from host_tool_invocation import capture, verify

RUN=host.W/'pg8182-web-prometheus-gauge-host-v1'
RAW_SHA='8b3954cbcab6572f96ea8e6d0c0cba605417f80de9f49d907825f24ca945ba0c'
SLOT=host.W/'pg8184-web-prometheus-gauge-post-v1'
OUT=host.BASE/'PG8184-web-prometheus-gauge-post-v1'
PREFIX='dev/codex/schubert/nk/web/monitoring/'
NAMES={PREFIX+'HttpMetricContract'+s for s in ('','$Metric','$Route','$Method','$Status','$Labels')}
NAMES|={PREFIX+'WebDbPoolMetricRecorder'+s for s in ('','$State','$Counts')}
NAMES|={PREFIX+'WebOutboxMetricRecorder'+s for s in ('','$Status','$Observation')}
NAMES|={PREFIX+'MediaStreamsMetricRecorder',PREFIX+'MediaBytesMetricRecorder',PREFIX+'MediaBytesMetricRecorder$Mode'}
OLD_REVIEW=host.BASE/'PG8132-web-pool-review-v1/manifest.json'
OLD_SHA='f6d7ac40ef2cddb898c9c29fbd2ccd77991ea161f245389f00b1ef075bd4b548'
OLD_POST=host.BASE/'PG8126-web-pool-post-v1/manifest.json'
OLD_POST_SHA='655e3f064bc57fc9266414fd290ac2f034ce3dbe20a0acae09d408c70bc25201'


def require(value,message):
    if not value:
        raise ValueError(message)


def assess(raw):
    require(raw['source']==contract.SOURCE and raw['actualExit']==0,'exact source and genuine terminal')
    require(raw['begin']['expectedTests']==50 and raw['begin']['selectedSuites']==contract.COUNTS,'closed exact tests')
    require(len(raw['cases'])==50 and len({(c['classname'],c['name']) for c in raw['cases']})==50
            and all(c['result']=='PASS' and not c['nonPass'] for c in raw['cases']),'actual unique PASS only')
    require(len(raw['suites'])==7 and all(v==dict(tests=contract.COUNTS[n.rpartition('.')[2]],failures=0,errors=0,skipped=0)
            for n,v in raw['suites'].items()),'no FES/unknown suite inflation')
    require(raw['begin']['fixtureSource']==contract.SOURCE and len(raw['begin']['fixtureHashes'])==2
            and set(raw['begin']['fixtureHashes'].values())=={contract.FIXTURE_SHA},'fixture present and independent bytes')
    require(raw['begin']['priorCoverageTransferred'] is False and raw['whole451Accepted'] is False
            and raw['formalUpdated'] is False and raw['effortPercent'] is None,'limited actual scope only')
    require(len(raw['stages'])==2 and all(s['actualExit']==0 and s['timedOut'] is False for s in raw['stages']),
            'both actual own compile and original JVM terminated zero')


def main():
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only independent audit')
    require(host.sha(RUN/'manifest.safe.json')==RAW_SHA,'full original terminal witness')
    raw=json.loads((RUN/'manifest.safe.json').read_bytes())
    assess(raw)
    require(host.sha(contract.COMPILE/'manifest.safe.json')==contract.COMPILE_SHA
            and raw['begin']['compileManifestSha256']==contract.COMPILE_SHA,'normal original source proof')
    snapshot=contract.COMPILE/'snapshot'
    for p,h in raw['begin']['sourceHashes'].items():
        require(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h,'all normal input/current byte equality')
    for key in ('dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes'):
        require(all(host.sha(Path(p))==h for p,h in raw['begin'][key].items()),'all actual '+key+' unchanged')
    require(host.sha(RUN/'jacoco.exec')==raw['execSha256'],'original single-exec bytes')
    parsed={}
    for path in sorted((RUN/'xml').glob('TEST-*.xml')):
        require(raw['xmlHashes'].get(path.name)==host.sha(path),'returned original XML bytes')
        doc=ET.parse(path).getroot()
        parsed[doc.get('name')]={k:int(doc.get(k,'0')) for k in ('tests','failures','errors','skipped')}
    require(parsed==raw['suites'] and len(parsed)==7,'independent XML matrix matches exact original terminal')
    command=raw['stages'][1]['command']
    require('-Dprometheus.config='+str(RUN/'empty-prometheus.properties') in command
            and '-javaagent:'+str(contract.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid=PG8182-WEB-PROMETHEUS-GAUGE' in command
            and raw['begin']['environment']==contract.ENV,'clean child JVM/one-session and own empty SDK config')
    cp=command[command.index('-cp')+1].split(os.pathsep)
    require(cp[0]==str(RUN/'fresh-test-classes') and all('test-classes' not in p for p in cp[1:]),
            'fresh tests and own empty first resource, no old compiled tests')
    rejected=[]
    for name,change in (
        ('source-tail',lambda x:x.update(source=x['source'][:-1]+'0')),
        ('failed-case',lambda x:x['cases'][0].update(result='NOT_PASS')),
        ('missing-fixture',lambda x:x['begin'].update(fixtureHashes={})),
        ('altered-fixture',lambda x:x['begin']['fixtureHashes'].update({next(iter(x['begin']['fixtureHashes'])):'0'*64})),
        ('prior-counter-union',lambda x:x['begin'].update(priorCoverageTransferred=True)),
        ('formal-inflation',lambda x:x.update(formalUpdated=True)),
        ('unknown-timeout',lambda x:x['stages'][1].update(timedOut=True))):
        candidate=copy.deepcopy(raw)
        change(candidate)
        try:
            assess(candidate)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('independent metadata mutation must be rejected')
    os.umask(0o077)
    SLOT.mkdir()
    steps.SLOT=SLOT
    component=SLOT/'component'
    component.mkdir()
    target=snapshot/'src/schubert-nk-web/target/classes'
    physical={}
    for name in sorted(NAMES|{PREFIX+'package-info'}):
        p=target/(name+'.class')
        require(p.is_file(),'all declared current executable and package metadata bytes exist')
        destination=component/(name+'.class')
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,destination)
        require(host.sha(destination)==host.sha(p),'copied exact normal class bytes')
        physical[name+'.class']=host.sha(p)
    jdk=host.TC/'jdk-25.0.4/bin'
    libraries=[host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[host.TC/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    helper=host.ROOT/'tools/quality/architecture/ComponentCoverageAudit.java'
    audit=SLOT/'audit-classes'
    audit.mkdir()
    reader_cp=os.pathsep.join(str(p) for p in libraries)
    stages=[]
    for name,cmd in (
        ('coverage-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',reader_cp,'-d',str(audit),str(helper)]),
        ('coverage-run',[str(jdk/'java'),'-cp',str(audit)+os.pathsep+reader_cp,'ComponentCoverageAudit',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES)])):
        row,output=steps.step(name,cmd)
        stages.append(row)
        require(row['actualExit']==0,'all declared 15 actual classes, CRC/session and all four counters')
    executable={}
    for line in output.splitlines():
        parts=line.split('\t')
        if parts[0]=='CLASS':
            executable[parts[1]]=dict(crc64=parts[2],counters={p.split(':')[0]:dict(missed=int(p.split(':')[1]),covered=int(p.split(':')[2])) for p in parts[3:]})
    require(set(executable)==NAMES,'all exactly15, no executable exclusions')
    totals={k:dict(missed=sum(v['counters'][k]['missed'] for v in executable.values()),
                         covered=sum(v['counters'][k]['covered'] for v in executable.values())) for k in ('LINE','METHOD','CLASS','BRANCH')}
    require(all(v['missed']==0 and v['covered']>0 for v in totals.values()),'nonvacuous all four100')
    require(host.sha(OLD_REVIEW)==OLD_SHA and host.sha(OLD_POST)==OLD_POST_SHA,'same-source existing static and generated witnesses')
    prior=json.loads(OLD_REVIEW.read_bytes())
    old=json.loads(OLD_POST.read_bytes())
    require(prior['source']==old['source']==contract.SOURCE and prior['unclassified']==0
            and prior['actualViolationsOutstanding']==0,'same exact production source previously classified static, not a different-source result')
    owners={'src/schubert-nk-web/src/main/java/'+name.split('$',1)[0]+'.java' for name in NAMES}
    sources={p:host.sha(host.ROOT/p) for p in sorted(owners)}
    require(len(sources)==5 and all(sources[p]==old['sourceFiles'][p] for p in sources),'all five identical current production source files')
    reasons=[r for r in prior['individualRationaleRows'] if r['sourcePath'] in owners]
    require(all(r['source']==contract.SOURCE and r['sourceSha256']==sources[r['sourcePath']]
                and r['disposition'] in ('CONTEXT_NOT_APPLICABLE','FALSE_POSITIVE','REQUIRED_CONTRACT')
                for r in reasons),'every applicable original raw reason and unchanged source')
    require(all(old['staticRaw'][k]['processingErrors']==0 for k in ('pmd','checkstyle','spotbugs'))
            and not old['staticRaw']['checkstyle']['findings'] and not old['staticRaw']['spotbugs']['findings'],
            'original actual source static no missing class, CS/SB0; not newly executed analysis')
    generated=[r for r in prior['generatedTypes'] if r['className'] in NAMES]
    require(len(generated)==10 and sum(len(r['methods']) for r in generated)==36
            and all(physical[r['className']+'.class']==r['sha256'] and r['sourceSha256']==sources[r['sourcePath']]
                    and r['directOrdinaryContractsVerified'] is True and r['customExclusionAdded'] is False for r in generated),
            'all10 generated types/36 methods same exact bytes and direct necessary 42 ordinary typed witnesses')
    # Every same-source original static finding remains visible; only applicable source rows are rebound.
    static_proof=dict(kind='EXISTING_SAME_PRODUCTION_SOURCE_AND_BYTES_NOT_NEW_ANALYSIS_RUN',
        originalPostSha256=OLD_POST_SHA,originalReviewSha256=OLD_SHA,
        applicableRationaleRows=reasons,allOriginalRawFindings=prior['rawPmdFindings'],
        currentAnalysisJobs=0,sourceScope=sorted(owners),suppressionsAdded=0,unclassified=0)
    verify(invocation)
    value=dict(actualExit=0,source=contract.SOURCE,qualificationHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip(),
        originalManifestSha256=RAW_SHA,originalCompileSha256=contract.COMPILE_SHA,invocation=invocation,
        timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),os=platform.platform(),
        tests=50,suites=7,physicalClasses=physical,executableClasses=executable,counters=totals,
        actualCrcMismatch=0,actualSessions=1,coverageUnion=False,customExclusionsAdded=False,
        scope='FOUR_RECORDERS_AND_DIRECT_CONTRACT_15_EXECUTABLES_ONLY_NOT_ALL_WEB_OR_WHOLE451',
        metadataClasses=[PREFIX+'package-info.class'],sourceFiles=sources,
        generatedTypes=generated,generatedMethodCount=36,generatedOrdinaryWitness='PG8182 exact necessary42 Test cases, same source bodies',
        staticApplicability=static_proof,negativeReceiptGuards=rejected,
        fixtureHashes=raw['begin']['fixtureHashes'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],
        auditStages=stages,auditHelperSha256=host.sha(helper),actualVmActions=0,actualDatabaseActions=0,
        actualNetworkActions=0,actualServiceActions=0,whole451Accepted=False,newAccepted=0,
        formalUpdated=False,effortPercent=None,productTestsExecutedByPost=0)
    host.write(SLOT/'manifest.safe.json',value)
    OUT.mkdir()
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=50,suites=7,counters=totals,negativeGuards=len(rejected),
       staticApplicableReasons=len(reasons),generatedTypes=len(generated),manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
