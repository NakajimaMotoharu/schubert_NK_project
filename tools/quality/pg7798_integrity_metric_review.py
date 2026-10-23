"""Current253, monitoring62 plus original dependency1, generated124 and all28 unchanged raw reasons."""
from collections import Counter
import copy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7802_integrity_metric_host_v2 as execution
import pg7804_integrity_metric_six_compile_v2 as compilation
import pg7032_monitoring_six_artifact_post as steps
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7798-integrity-metric-review-v1'
PREFIX='dev/codex/schubert/nk/batch/monitoring/'
DEPENDENCY='dev/codex/schubert/nk/batch/repository/BatchStep'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=117,introduced=2))
    paths={r['path']:r for r in trace['sourceRows']}
    require(len(paths)==119 and len(trace['physicalRows'])==103
      and len({r['className'] for r in trace['physicalRows']})==103,'all source and additional physical owners')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no transferred counters')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==253 and row['componentCounterScope']=='ALL_CURRENT_BATCH_EXECUTABLES_ONLY','current exact Batch witness')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'POM not PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','historical source not current execution')
    roles={'batch':('CURRENT_BATCH_QUALIFIED',physical['currentBatch']),
      'api':('HISTORICAL_API_BYTE_ONLY',physical['historicalApi']),'web':('HISTORICAL_WEB_BYTE_ONLY',physical['historicalWeb'])}
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);label,proof=roles[role];executable=not entry.endswith('package-info.class')
        path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['qualificationDomain']==label and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='batch' and executable) and row['sourcePath']==path
          and row['owner']==paths[path]['owner'] and row['sha256']==proof['physicalClasses'][row['className']],'all true role/source/byte owners')
    dep=trace['originalDependencyTrace'];expected=physical['originalCurrentDependency']
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==62 and len(current['executableClasses'])==63
      and all(dep[k]==v for k,v in expected.items()) and dep['owner']=='WBS-P017-02' and dep['additionalPhysicalCount']==0
      and dep['alreadyInOriginal1669'] is True and dep['currentSourceExecutionAccepted'] is True
      and dep['sourceSha256']==current['sourceFiles'][dep['sourcePath']] and dep['executionWitness']['source']==current['source']
      and 'batch:'+DEPENDENCY+'.class' not in {r['className'] for r in trace['physicalRows']},'original dependency1 explicitly qualified, no double-count or source alias')
    return counts

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only same-source review');proofs={};pins={}
    for key,path,digest in (
      ('current','PG7790-integrity-metric-post-v1/manifest.json','37cbd4239538d378a060c475fadd7a0151fe99f73046985376161f6d8e36a448'),
      ('physical','PG7794-integrity-metric-six-post-v1/manifest.json',None),
      ('trace','PG7796-integrity-metric-trace-v1/manifest.json',None),
      ('previousTrace','PG7778-media-bytes-trace-v1/manifest.json','08afec5b1cd6ac4f7fa9c9dc9017f51e33de2d7cdc17e59e8306d1bd83ff096a'),
      ('old','PG7712-observed-retention-post-v1/manifest.json','4da07632be45c13495dc4929e0b197fc9ed2e6b6b917226e41362a6204774931'),
      ('oldReview','PG7720-observed-retention-review-v1/manifest.json','8dcdce75a2afc017326bbbc4cf88bebfa77e5feb1a31d91b36fe53ba94226f7a'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['current'];old=proofs['old'];prior=proofs['oldReview'];trace=proofs['trace'];physical=proofs['physical']
    require(c['actualExit']==physical['actualExit']==trace['actualExit']==0 and c['source']==physical['source']==trace['source']==compilation.SOURCE
      and c['tests']==253 and c['suites']==33 and len(c['sourceFiles'])==67 and len(c['executableClasses'])==63
      and len(c['physicalClasses'])==64 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'genuine current253/63/CRC0/single session/four100')
    require(all(c['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items())
      and all(c['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items()),'all old64 source/61 physical incl debug unchanged before reason reuse')
    canonical=lambda row:json.dumps(row,sort_keys=True);raw=c['staticRaw']['pmd']
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==28
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0
      and prior['unchangedIndividualRationaleCount']==25 and len(prior['movedModePropertyRationales'])==3,'all28 exact rows with previous individual reason chain, no suppression')
    dispositions=[]
    for row in raw['findings']:
        full=row['class'].split('.',1)[0];path='src/schubert-nk-batch/src/main/java/'+PREFIX+full+'.java'
        require(path in c['sourceFiles'] and c['sourceFiles'][path]==old['sourceFiles'][path],'each issue-bearing source unchanged')
        matched=[r for r in prior['movedModePropertyRationales'] if r['raw']==row]
        dispositions.append(dict(raw=row,sourcePath=path,sourceSha256=c['sourceFiles'][path],classification='EXISTING_INDIVIDUAL_REASON_UNCHANGED_SOURCE_BYTE_AND_POSITION',
          reason=matched[0]['reason'] if matched else 'Exact unchanged25 per-row rationale chain of pinned7720.previousReview; this row, issue-bearing source and compiled debug byte are unchanged, current ordinary253 requalifies the complete component.',
          rationaleWitness=pins['oldReview'],earlierRationaleWitness=prior['witnesses']['previousReview'],sourceOrRulesChanged=False,suppressionAdded=False))
    require(len(dispositions)==28 and c['spotbugs']['actualExit']==0 and c['spotbugs']['findings']==0
      and c['staticRaw']['checkstyle']['actualExit']==0 and not c['staticRaw']['checkstyle']['findings'],'all reasoned rows and actual SB/CS0')
    raw_run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    require(raw_run['actualExit']==0 and len(raw_run['cases'])==253 and all(r['result']=='PASS' for r in raw_run['cases']),'actual corrected original verify, not first failed source transfer')
    for name,count in (('GeneratedBatchValueContractTest',7),('MonitoringRetentionConfigurationTest',8),('IntegrityFailureMetricRecorderTest',8)):
        cases=[r for r in raw_run['cases'] if r['classname'].endswith('.'+name)]
        require(len(cases)==count and all(r['result']=='PASS' for r in cases),'old120/new4 generated contracts actually exercised on this source')
    require(prior['currentBatchGeneratedTypes']==30 and prior['currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==120,'exact original generated120 qualification, never numeric coverage addition')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same official platform and filters')
    work=host.W/'pg7798-integrity-metric-review-v1';require(not work.exists(),'new-only metadata stages');work.mkdir();steps.SLOT=work
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes';generated=[]
    for name,testid in ((PREFIX+'IntegrityFailureMetricRecorder$Area','INTEGRITYMET003'),(DEPENDENCY,'INTEGRITYMET001')):
        file=classes/(name+'.class');require(host.sha(file)==c['physicalClasses'][name+'.class'],'exact executed generated enum class')
        receipt,stdout=steps.step('javap-'+name.rsplit('/',1)[1].replace('$','-'),[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s',str(file)])
        require(receipt['actualExit']==0 and 'values();' in stdout and 'valueOf(java.lang.String);' in stdout
          and 'clone:' in stdout and 'java/lang/Enum.valueOf:' in stdout,'two exact enum factories plus independent typed current ordinary oracle')
        generated.append(dict(className=name,sha256=host.sha(file),methods=['values()','valueOf(java.lang.String)'],testId=testid,receipt=receipt,
          originallyIn1669=name==DEPENDENCY,customExclusionAdded=False))
    dep=trace['originalDependencyTrace'];require(dep['counters']['LINE']==dict(missed=0,covered=15)
      and dep['counters']['METHOD']==dict(missed=0,covered=3) and dep['counters']['CLASS']==dict(missed=0,covered=1)
      and dep['counters']['BRANCH']==dict(missed=0,covered=0),'complete measured dependency getter/ctor/init, genuinely no branches not removed conditions')
    core=(host.ROOT/'tools/quality/pg7008_monitoring_mode_post.py').read_text()
    expected=core.replace('Independent original-result/CRC/session/static post for the pure mode component.',
      'Fixed additional original Repository BatchStep included explicitly; all-class CRC/static, no exclusions.')
    expected=expected.replace("SOURCE_ROOT_PREFIX = 'src/schubert-nk-batch/'", "SOURCE_ROOT_PREFIX = 'src/schubert-nk-batch/'\nEXPLICIT_ORIGINAL_DEPENDENCY = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchStep.java'")
    expected=expected.replace("if p.startswith(SOURCE_ROOT_PREFIX) and '/monitoring/' in p and p.endswith('.java')", "if (p.startswith(SOURCE_ROOT_PREFIX) and '/monitoring/' in p and p.endswith('.java')) or p==EXPLICIT_ORIGINAL_DEPENDENCY")
    expected=expected.replace('harnessPomSha256=host.sha(snapshot/POM),sourceFiles=source_files,',
      'harnessPomSha256=host.sha(snapshot/POM),sourceFiles=source_files,\n      explicitOriginalDependencySource=EXPLICIT_ORIGINAL_DEPENDENCY,additionalOriginalDependencyCount=1,\n      monitoringSourceFileCount=SOURCE_FILE_COUNT-1,measuredOriginalDependencyNotNewPhysical=True,')
    require(expected.strip()==(host.ROOT/'tools/quality/pg7806_integrity_dependency_component_post.py').read_text().strip(),
      'entire core verifier differs only explicit additional source inclusion/provenance, all actual physical/CRC/static/coverage rules retained')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(trace,c,physical,previous);negative=[]
    for label,mutate in (
      ('historicalExecution',lambda t:next(r for r in t['physicalRows'] if r['className'].startswith('web:')).update(currentSourceExecutionAccepted=True)),
      ('wrongOriginalOwner',lambda t:t['originalDependencyTrace'].update(owner='WBS-C07')),
      ('doubleCountOriginal',lambda t:t['originalDependencyTrace'].update(additionalPhysicalCount=1)),
      ('dependencySourceAlias',lambda t:t['originalDependencyTrace'].update(source='historical')),
      ('counterTransfer',lambda t:t['sourceRows'][0].update(currentSourceCoverageTransferred=True))):
        mutant=copy.deepcopy(trace);mutate(mutant)
        try:domains(mutant,c,physical,previous)
        except ValueError:negative.append(dict(name=label,rejected=True))
        else:raise ValueError('metadata mutation accepted')
    require(len(negative)==5,'all five guards reject metadata only')
    initial=subprocess.check_output(['git','show','f9d91150a9d82cd3edecbc02043c946926389967:'+dep['sourcePath']],cwd=host.ROOT)
    require(hashlib.sha256(initial).hexdigest()==dep['sourceSha256'],'original dependency production source unchanged')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      tests=253,suites=33,rawPmdFindings=28,rawPmdExit=4,staticDispositions=dispositions,newMainRawFindings=0,unclassified=0,actualViolationsOutstanding=0,
      currentBatchGeneratedTypes=32,currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=124,newGeneratedContracts=generated,
      originalDependencyTrace=dep,allSourceCount=119,additionalPhysicalCount=103,original1669DependencyAdditionalPhysicalCount=0,
      currentMonitoringExecutableCount=62,currentOriginalDependencyExecutableCount=1,counters=c['counters'],editAnchorCounts=counts,negativeGuards=negative,
      explicitAdditionalSourceVerifierOnly=True,customExclusionsAdded=False,suppressionsAdded=0,ptExecutedByReview=0,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=253,generatedMethods=124,rawFindings=28,unclassified=0,negativeGuards=5,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
