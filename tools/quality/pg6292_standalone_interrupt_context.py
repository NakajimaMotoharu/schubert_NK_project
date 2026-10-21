"""Sixteen explicit current-thread observations are outside the pinned J2EE rule premise."""
import inspect
import json
import os
import hashlib
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
import pg6284_web_owned_static_reviews as engine
from static_disposition_overlay import load,apply_decisions

T='DoNotUseThreads'
SITES={
 'BackupArtifactVerifier':{725:'current caller interrupt before bounded artifact IO',728:'same caller interrupt after the clock read'},
 'MaintenanceRunFiles':{369:'same caller interrupt before returning the verified result',378:'current caller interrupt before admission and euid checks',1103:'same caller interrupt after owned action before result return'},
 'ArtemisManagementReadinessClient':{108:'restore the interrupted caller before fixed failure mapping',286:'restore caller interrupt after caught wait interruption'},
 'SystemctlStateSource':{90:'restore caller interrupt after buffer wipe and fixed failure mapping'},
 'LinuxSystemdSession':{56:'record current owner thread identity before acquiring a native bus',83:'reject calls from a different thread; no thread is started'},
 'MaintenanceOwnerFrame':{137:'check current caller interrupt before monotonic owner guard',143:'recheck current caller interrupt and deadline after observation'},
 'SystemManagerObservation':{107:'capture current owner thread identity',118:'reject access from another thread',120:'reject interrupted caller before reading properties',173:'reject interrupted caller before finite observation wait'}
}
SPEC={name:{(line,T):(1,'SS311/342/343 standalone batch/bootstrap JavaSE, not J2EE managed-thread context: '+reason+'. This is only the pinned rule applicability premise. It neither proves actual owner/lock/Unit/native completion nor grants process/service access.')for line,reason in sites.items()}for name,sites in SITES.items()}
TESTS={name:[]for name in SPEC}
PLAN=engine.BASE/'PG6290-application-static-review-v1/manifest.json'
PLAN_SHA='952e8b7755eb35165a26d1c67a1e9a0ceaffc834c8918a22fbc0e5fe1da662d9'
RULE_SHA='a584188485d8da3ca58abf4d80cfd443775a2f9fecdc97ebd6aa4dec33049da3'


def rule_premise():
    jar=engine.ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    with zipfile.ZipFile(jar)as z:raw=z.read('category/java/multithreading.xml')
    if hashlib.sha256(raw).hexdigest()!=RULE_SHA:raise ValueError('exact pinned7.28 multithreading rules')
    rows=[r for r in ET.fromstring(raw)if r.attrib.get('name')==T]
    if len(rows)!=1 or rows[0].attrib['message']!='To be compliant to J2EE, a webapp should not use any thread.':raise ValueError('explicit J2EE premise, not all Java thread observation forbidden')
    for module in ('batch','bootstrap'):
        text=(engine.ROOT/('src/schubert-nk-'+module+'/pom.xml')).read_text()
        if any(x in text for x in ('<packaging>war','<packaging>ear','jakarta.ejb')):raise ValueError('standalone context must be rereviewed if deployment premise changes')
    return dict(version='7.28.0',resource='category/java/multithreading.xml',sha256=RULE_SHA)


def calculate():
    rule=rule_premise();scope={**vars(engine),'PLAN':PLAN,'PLAN_SHA':PLAN_SHA,'SPEC':SPEC,'TESTS':TESTS}
    raw=inspect.getsource(engine.calculate)
    for a,b in (("prefix='web:'","prefix=row['sourcePath'].split('/')[1].removeprefix('schubert-nk-')+':'"),
        ('len(decisions)!=33','len(decisions)!=16'),('all33 explicit','all16 explicit'),('reviewed=33','reviewed=16'),
        ('1338 individual ordinary Web','1339 individual standalone thread-context')):
        if a not in raw:raise ValueError('exact current source engine '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<16 caller observations>','exec'),scope)
    rows,value=scope['calculate']()
    for row in rows:
        row.update(status='CONTEXT_NOT_APPLICABLE',staticContextPremiseOnly=True,pinnedRule=rule,
            plannedCurrentWholeCaseClasses=[],reviewScope='PINNED_RULE_STANDALONE_CONTEXT_ONLY_NOT_RUNTIME_AUTHORITY')
    updated=apply_decisions(load(PLAN,PLAN_SHA,value['source']),rows)
    value.update(statusCounts=dict(Counter(r['status']for r in updated)),pinnedRule=rule,
        unresolved=['No process/service/native/thread action executed; actual resource conditions remain unverified','All other findings/full-source quality remain separate'])
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6292-standalone-thread-context-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=16,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
