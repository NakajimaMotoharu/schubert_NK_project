"""686 safe exact4 source/count/hash evidence, not private JDBC/native bytes."""
import hashlib
import json
import os
from pg1625_unsupported_ports_selected import ROOT,W
from pg1719_current_bootstrap_sources import SOURCE

def main():
    os.umask(0o077)
    records={}; values={}
    for key,name in [('selected','pg1750-expiry-count-selected-v1'),('qualified','pg1751-expiry-exact-qualified-v1')]:
        p=W/name/'manifest.safe.json';raw=p.read_bytes();v=json.loads(raw)
        if v.get('actualExit')!=0:raise ValueError('actual success required')
        values[key]=v; records[key]={'path':name+'/manifest.safe.json','sha256':hashlib.sha256(raw).hexdigest(),'serverManifestSha256':v['manifestSha256'],'actualExit':0}
    s=values['selected'];q=values['qualified']
    if s['tests']!=4 or q['testsByRun']!={'1750':4}or s['productionSource']!=SOURCE or q['remaining']!=s['remaining']or s['FESAbortedNotRun']!=0 or s['classByteMismatch']!=0:raise ValueError('source count CRC qualification required')
    v={'program':'NK-BAT-001','testIds':['EXP-1749-'+f'{i:03}'for i in range(1,5)],'branch':'dev-foundation','productionSource':SOURCE,'testSource':s['testSource'],'records':records,'actualExit':0,'tests':4,'FESAbortedNotRun':0,'classByteMismatch':0,'javacWarnings':0,'coverageRemaining':s['remaining'],'coverage100':False,'failed1749NotPassed':True,'bugs':['BUG-1160'],'ykt':['YKT-928'],'vmOrDbOperations':0,'privateRawExported':False,'formalRun':'PT-WEB-20260925-24','formalTests':1964,'formalScopes':53,'formalAccepted':False,'wholeLeafAcceptedDelta':0,'command':'python3 -B tools/quality/pg1750_expiry_count_selected.py; separate pg1751_expiry_exact_qualification.py','environment':{'execution':'LAN Ubuntu26.04/x86_64','jdk':'25.0.4','junit':'5.13.4','jacoco':'0.8.15'},'independentOracle':'literal expected record fields and four unique XML IDs, no Production expected generation','N':None,'T':None,'actualAllocatedPp':None}
    p=ROOT/'evidence/01_PT/017_NK-BAT-001/evidence/output/686_manifest.json'
    with p.open('x')as f:json.dump(v,f,sort_keys=True,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'formalAccepted':False}))

if __name__=='__main__':main()
