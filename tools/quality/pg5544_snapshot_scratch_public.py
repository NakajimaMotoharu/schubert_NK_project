"""Publish allowlisted scratch red/green/bytecode evidence, never raw properties or sessions."""
import json
import os
import xml.etree.ElementTree as ET
import pg5542_snapshot_scratch_bytecode as audit
import pg3280_wbs_current_source as redactor

BASE=audit.ROOT/'evidence/01_PT/006_NK-MSG-002/007_SnapshotScratch/evidence/output/PG5544-scratch-v1'
SOURCE='a19a9f7d940b4f9fba47e51bd9be675f4420401b'


def load(slot,expected=None):
    path=audit.W/slot/'manifest.safe.json'
    digest=audit.sha(path)
    if expected is not None and digest!=expected:raise ValueError('fixed original evidence bytes')
    return json.loads(path.read_bytes()),digest


def main():
    green,gsha=load(audit.RUN,'fb49c8579faff830f2df86f80286f9073392d436b0b986a537b3a0bbbf8e6a78')
    bytecode,bsha=load(audit.SLOT,'cc4b8e5ccd0b1f359b9acd1bb44e1d0cefad390cc5a48bc99b7c5219965fcbb1')
    red,rsha=load('pg5540-snapshot-scratch-red-v3','5631973e95503d23953d42dbfdc26b1f2e0196d7b736d9adc44ead94ab6e6c0a')
    if not(green['sourceSnapshot']==bytecode['sourceSnapshot']==SOURCE and green['greenSelectedQualified']and green['actualCases']==29 and green['targetFour100']and bytecode['actualExit']==0 and len(bytecode['fixtureFactories'])==8 and red['purposefulRedEstablished']and red['actualExit']==1):raise ValueError('actual coherent green and exact independent red/bytecode evidence')
    history=[]
    for suffix in('red-v1','red-v2','red-v3','green-v1'):
        value,digest=load('pg5540-snapshot-scratch-'+suffix)
        history.append({k:value[k]for k in('sourceSnapshot','phase','actualExit','actualCases','suites','purposefulRedEstablished','greenSelectedQualified','exactSelectedInventory','phaseExits')}|{'run':'PG5540-'+suffix,'originalManifestSha256':digest})
    raw=(audit.W/audit.RUN/'source/src/schubert-nk-api/target/site/jacoco/jacoco.xml').read_bytes()
    counters=redactor.report_counters(ET.fromstring(raw))
    public,proof=redactor.redact_report(raw,{k:counters[k]for k in redactor.COUNTERS}|{'classByteMismatch':0,'formal':False})
    value={'actualExit':0,'productionInputSnapshot':SOURCE,'deployedSourceUnchanged':audit.prior.SOURCE,
        'selectedCases':29,'suites':5,'failed':0,'errors':0,'skipped':0,'wholeRegressionAccepted':False,
        'sourceFixed':True,'allSixFormatBeforePT':True,'builtStaticIssues':green['staticBuiltModules'],
        'targetProgram':'NK-MSG-002/ResponseSnapshotCodec','targetCounters':green['targetCounters'],'targetFour100':True,
        'caseScope':green['caseScope'],'physicalMainDelta':{k:green['physicalMain'][k]for k in('count','changed','added','removed','declaredDeltaQualified')},
        'caseIds':{f'PT-IDEM-SCRATCH00{i}':{'result':'PASS','expectedNativeAcquired':0 if i<3 else 1,'expectedEndAtFault':0,'realHeapExhaustion':False}for i in range(1,5)},
        'redIsNotPass':True,'history':history,'selectedOriginalManifestSha256':gsha,'redOriginalManifestSha256':rsha,
        'independentBytecodeReceiptSha256':bsha,'mainBytecode':bytecode['mainMethods'],'fixtures':bytecode['fixtureFactories'],
        'coverageReport':{'path':'api-selected-jacoco.xml',**proof,'scope':'entire selected API report; only named target qualified100; global source quality remains pending'},
        'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'oldNativeImported':False,'vmActions':0}
    os.umask(0o077);BASE.mkdir(parents=True)
    with(BASE/'api-selected-jacoco.xml').open('xb')as target:target.write(public);target.flush();os.fsync(target.fileno())
    with(BASE/'manifest.json').open('x')as target:json.dump(value,target,sort_keys=True,ensure_ascii=False,indent=2);target.write('\n');target.flush();os.fsync(target.fileno())
    print(json.dumps({'actualExit':0,'sourceSnapshot':SOURCE,'sha256':audit.sha(BASE/'manifest.json'),'targetFour100':True,'selectedCases':29,'fixtures':8,'formalAccepted':False},sort_keys=True))


if __name__=='__main__':main()
