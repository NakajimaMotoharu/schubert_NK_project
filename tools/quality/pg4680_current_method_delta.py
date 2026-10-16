"""Saved-only method delta with identical actual Main bytes; never arithmetic global acceptance."""
import hashlib
import json
import os
from pathlib import Path
import xml.etree.ElementTree as E
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4662-current-native-measurement-v1'
SOURCE='964e96e45bb588e7e75798b5adf425cbd9985427'
SLOT='pg4680-current-method-delta-v1'
TARGETS=[('RootStartupPending','verifySelf','pg4674-root-self-identity-selected-v1'),('RootServiceLauncher','proof','pg4678-root-proof-environment-selected-v1'),('RootServiceLauncher','environment','pg4678-root-proof-environment-selected-v1')]


def counters(xml,name,method):
    root=E.fromstring(xml);classes=[c for c in root.findall('package/class')if c.get('name')==name]
    if len(classes)!=1:raise ValueError('one exact class')
    methods=[m for m in classes[0].findall('method')if m.get('name')==method]
    if len(methods)!=1:raise ValueError('one exact method; overload descriptor required otherwise')
    return methods[0].get('desc'),{c.get('type'):{k:int(c.get(k))for k in ['missed','covered']}for c in methods[0].findall('counter')}


def delta(old,new):
    if set(old)!=set(new):raise ValueError('identical method counter scope required')
    for key in old:
        for value in [old[key],new[key]]:
            if set(value)!={'missed','covered'}or any(type(n)is not int or n<0 for n in value.values()):raise ValueError('strict nonnegative counters')
        if sum(old[key].values())!=sum(new[key].values())or new[key]['missed']!=0:raise ValueError('equal denominators and complete new target conditions first')
    return {key:old.get(key,{'missed':0})['missed']for key in ['LINE','METHOD','BRANCH']}


def main():
    raw=(BASE/'manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!='5efbdb58521fbebd6f2c70de3f38bcd96963133191d7f948f25a659bf1f24cf5':raise ValueError('actual saved baseline authority')
    baseline=json.loads(raw);full=json.loads((W/'pg4428-shared-manager-whole-qualified-v1/manifest.safe.json').read_bytes())
    if baseline['productionSource']!=SOURCE or full['actualExit']!=0 or full['result']['productionSource']!=SOURCE:raise ValueError('same qualified source')
    original=(BASE/'coverage/batch/site/jacoco/jacoco.xml').read_bytes()
    record=next(m for m in baseline['modules']if m['module']=='batch')
    if hashlib.sha256(original).hexdigest()!=record['coverageXmlSha256']:raise ValueError('actual redacted same-source XML')
    result=[]
    for name,method,slot in TARGETS:
        manifest=json.loads((W/slot/'manifest.safe.json').read_bytes())
        if manifest['actualExit']!=0 or manifest['actualMavenExit']!=0 or manifest['reasons']:raise ValueError('actual qualified selection first')
        snapshot=W/slot/'source';relative='dev/codex/schubert/nk/batch/file/'+name
        blob=(snapshot/('src/schubert-nk-batch/target/classes/'+relative+'.class')).read_bytes()
        digest=hashlib.sha256(blob).hexdigest()
        if digest!=full['result']['allPhysicalMainSha256']['batch:'+relative+'.class']:raise ValueError('actual identical Main byte before any counter delta')
        xml=(snapshot/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml').read_bytes()
        old_desc,old=counters(original,relative,method);new_desc,new=counters(xml,relative,method)
        if old_desc!=new_desc:raise ValueError('same descriptor')
        difference=delta(old,new)
        result.append({'class':relative,'method':method,'descriptor':old_desc,'sameMainSha256':digest,'baselineCounters':old,'selectedCounters':new,'newlyCoveredTarget':difference,'kind':'NEW_COUNTER_CONDITIONS'if any(difference.values())else'CONTRACT_STRENGTHENING_COUNTER_DELTA_ZERO','selectedRun':slot,'selectedSnapshot':manifest['sourceSnapshot'],'selectedManifestSha256':hashlib.sha256((W/slot/'manifest.safe.json').read_bytes()).hexdigest(),'selectedXmlSha256':hashlib.sha256(xml).hexdigest()})
    value={'actualExit':0,'productionSource':SOURCE,'targets':result,'targetOnlyDelta':{k:sum(r['newlyCoveredTarget'][k]for r in result)for k in ['LINE','METHOD','BRANCH']},'globalCounterRecomputed':False,'oldGlobalCounterNotArithmeticallyReduced':True,'formalAccepted':False,'acceptedLeafDelta':0,'MainModified':False,'testsReissued':False,'vmActions':0,'BUG':'BUG1379','YKT':'YKT1145'}
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return 0


if __name__=='__main__':raise SystemExit(main())
