"""Allowlist original71 cases, whole selected reports and physical proofs; no native credit."""
import hashlib
import json
import os
import xml.etree.ElementTree as ET
import pg3280_wbs_current_source as redactor
from pg5058_whole_case_projection import project_xml
import pg5568_monitor_bytecode as audit

ROOT,W=audit.ROOT,audit.W
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5570-private-monitor-v1'
SOURCE='2fc563a5f2fba4cfaf6f7a5bd56fe8909c1910ad'
IDS={'monitor001CallerLockCannotBlockOwnedStartStatus':'OPS-MONITOR001',
    'monitor002CallerLockCannotBlockOwnedStopStatus':'OPS-MONITOR002',
    'monitor003CallerLockCannotBlockReadyInformationOrRelease':'OPS-MONITOR003',
    'monitor004CallerLockCannotBlockConfirmedLifetimeClose':'OPS-MONITOR004'}


def load(slot,digest):
    path=W/slot/'manifest.safe.json';raw=path.read_bytes()
    if audit.sha(raw)!=digest:raise ValueError('fixed original record hash')
    return json.loads(raw)


def main():
    green=load('pg5566-private-monitor-green-v2','27d1b35269b9a4e8848100565e7d6b901f425cd599805c6afe1031dc874ced50')
    red=load('pg5566-private-monitor-red-v1','ea6699978f6b9267fa9a379b50a6a9d32e10f30a80888b481c8ce9b08220fee1')
    post=load(audit.SLOT,'fb7917b4b9d9944f0cf3a6fb286d173569e31193ab1e8fbc31cf3f2f91d554ec')
    if not(green['sourceSnapshot']==post['sourceSnapshot']==SOURCE and green['greenSelectedQualified']and green['actualCases']==71
        and green['suites']==8 and red['actualExit']==1 and red['purposefulRedEstablished']and post['actualExit']==0
        and sum(map(len,post['privateMonitorMethods'].values()))==14):raise ValueError('same-source actual green and independent post, purposeful red retained')
    snapshot=W/'pg5566-private-monitor-green-v2/source';cases=[];environments=[];reports={};prepared={};newtrace={}
    for module in('protocol','storage','bootstrap','api','web','batch'):
        target=snapshot/('src/schubert-nk-'+module+'/target')
        for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            raw=path.read_bytes();tree=ET.fromstring(raw);suite=tree.get('name')
            if audit.sha(raw)!=green['xmlHashes'][suite]:raise ValueError('original selected XML immutable')
            projected=project_xml(module,path.name,raw,audit.sha(raw));cases.extend(projected)
            props={p.get('name'):p.get('value')for p in tree.findall('properties/property')}
            environments.append({key:props[key]for key in('os.name','os.arch','os.version','java.version','java.vendor')})
            for item,row in zip(tree.findall('testcase'),projected,strict=True):
                name=item.get('name','').removesuffix('()')
                if name in IDS:
                    if IDS[name]in newtrace:raise ValueError('new criterion only once in original XML')
                    newtrace[IDS[name]]=row
        raw=(target/'site/jacoco/jacoco.xml').read_bytes();counts=redactor.report_counters(ET.fromstring(raw))
        public,proof=redactor.redact_report(raw,{k:counts[k]for k in redactor.COUNTERS}|{'classByteMismatch':0,'formal':False})
        prepared[module+'-selected-jacoco.xml']=public
        reports[module]={'path':module+'-selected-jacoco.xml',**proof,'scope':'complete selected module report, no native/global100 claim'}
    if len(cases)!=71 or len(environments)!=8 or len({r['testId']for r in cases})!=71 or set(newtrace)!=set(IDS.values())or any(x!=environments[0]for x in environments):raise ValueError('all71/eight original XML/newfour/source environment exact')
    history=[]
    for slot in('pg5566-private-monitor-red-v1','pg5566-private-monitor-green-v1','pg5566-private-monitor-green-v2'):
        path=W/slot/'manifest.safe.json';value=json.loads(path.read_bytes())
        history.append({'run':slot,'originalManifestSha256':audit.sha(path.read_bytes()),**{k:value[k]for k in('sourceSnapshot','actualExit','actualCases','suites','exactSelectedInventory','purposefulRedEstablished','greenSelectedQualified','phaseExits')}})
    value={'actualExit':0,'productionInputSnapshot':SOURCE,'deployedSourceUnchanged':'29612b2a484a5ab7418e02a491c4360af7444626',
        'branch':green['branch'],'startedUTC':green['startedUTC'],'completedUTC':green['completedUTC'],'originalEnvironment':environments[0],
        'commands':green['commands'],'phaseExits':[0,0],'actualCases':71,'suites':8,'failures':0,'errors':0,'skipped':0,
        'allSixFormatBeforePt':True,'staticSixModules':green['staticBuiltModules'],'archiveSha256':green['archiveSha256'],'caseTrace':newtrace,
        'allCaseRefs':cases,'history':history,'redIsNotPass':True,'originalSelectedSha256':'27d1b35269b9a4e8848100565e7d6b901f425cd599805c6afe1031dc874ced50',
        'independentBytecodeProofSha256':'fb7917b4b9d9944f0cf3a6fb286d173569e31193ab1e8fbc31cf3f2f91d554ec',
        'physicalMain':green['physicalMain'],'targetCounters':green['targetCounters'],'completeCoverageReports':reports,
        'privateMonitorMethods':post['privateMonitorMethods'],'lockBeforeNativeAcquisition':post['lockBeforeNativeAcquisition'],
        'physicalDifferences':post['allPhysicalDifferenceClassifications'],'existingStatementRows':post['existingStatementRows'],'existingPrivateLockFields':post['existingPrivateLockFields'],
        'privateLockContractQualified':True,'pmdPerformanceDispositionPending':True,'F03Accepted':False,'wholeQualified':False,'nativeQualified':False,
        'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'oldNativeImported':False,'vmActions':0,'rawSecretsOrSessionIdsExported':False}
    os.umask(0o077);BASE.mkdir()
    for name,raw in prepared.items():
        with(BASE/name).open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    with(BASE/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sourceSnapshot':SOURCE,'actualCases':71,'newCriterionTraces':4,'privateMonitors':14,'physicalChanges':11,'debugOnly':5,
        'sha256':hashlib.sha256((BASE/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
