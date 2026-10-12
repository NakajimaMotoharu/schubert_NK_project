"""Public current3618 whole source result; no raw logs/DB/credentials/native bytes."""
import hashlib
import json
import os
from pg1446_current_cold_stage import W
from pg1625_unsupported_ports_selected import ROOT

def main():
    source=W/'pg1756-boundary-full-qualified-v1/manifest.safe.json';raw=source.read_bytes();v=json.loads(raw);r=v.get('result',{})
    if v.get('actualExit')!=0 or (r.get('tests'),r.get('suites'),r.get('mainClasses'))!=(3618,536,1643)or r.get('changedClasses')!=[]or r.get('addedClasses')!=[]or r.get('FESFlakyNotRun')!=0 or r.get('staticSixModules')!=0:raise ValueError('actual fresh whole qualification required')
    allmiss={k:sum(c[k]['missed']for c in r['coverage'].values())for k in ('LINE','METHOD','CLASS','BRANCH')}
    value={'program':'NK-OPS-001','testId':'PT-K01-1755-FULL6','branch':'dev-foundation','sourceSnapshot':r['sourceSnapshot'],'productionSource':r['productionSource'],'actualExit':0,'mavenExit':0,'tests':r['tests'],'suites':r['suites'],'physicalMainClasses':r['mainClasses'],'FESFlakyNotRun':0,'staticSixModules':0,'allMainClassDelta0':True,'modules':r['modules'],'coverage':r['coverage'],'hostModuleLocalMissed':allmiss,'jarHashes':r['jarHashes'],'qualificationInputs':r['qualificationInputs'],'serverManifestSha256':r['serverManifestSha256'],'sourceArchiveSha256':r['sourceArchiveSha256'],'qualificationHostSha256':hashlib.sha256(raw).hexdigest(),'startUTC':r['startUTC'],'endUTC':r['endUTC'],'elapsedSeconds':r['elapsedSeconds'],'command':'pg1755_main_test_separate_full_six.py: offline clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report jar:jar; separate pg1756_boundary_full_qualification.py','environment':{'execution':'dedicated LAN Ubuntu26.04/x86_64','jdk':'25.0.4','maven':'3.9.12','postgresql':'18.6','node':'24.19.0','jacoco':'0.8.15','worker':1},'bug':['BUG-1161'],'ykt':['YKT-929'],'old1754NotRunNotPassed':True,'coverage100':False,'newNextDayNativeNotYetQualified':True,'vmOperationsInThisGroup':0,'privateRawExported':False,'formalRun':'PT-WEB-20260925-24','formalTests':1964,'formalScopes':53,'formalAccepted':False,'wholeLeafAcceptedDelta':0,'N':None,'T':None,'actualAllocatedPp':None}
    p=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/output/689_manifest.json';os.umask(0o077)
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tests':3618,'formalAccepted':False}))

if __name__=='__main__':main()
