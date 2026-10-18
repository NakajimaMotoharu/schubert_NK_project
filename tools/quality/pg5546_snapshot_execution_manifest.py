"""Canonical program execution context from original XML, never current-OS backfill."""
import datetime
import json
import os
import xml.etree.ElementTree as ET
import pg5544_snapshot_scratch_public as public


def main():
    output=public.BASE/'manifest.json'
    if public.audit.sha(output)!='e8f6006e3c0bfef23d730b9337551f73fa4ae67934dcc1af3999800078ab5f96':raise ValueError('original sanitized data manifest')
    green,_=public.load(public.audit.RUN,'fb49c8579faff830f2df86f80286f9073392d436b0b986a537b3a0bbbf8e6a78')
    contexts=[]
    for module in('protocol','storage','bootstrap','api'):
        for path in(public.audit.W/public.audit.RUN/'source'/('src/schubert-nk-'+module+'/target/surefire-reports')).glob('TEST-*.xml'):
            root=ET.parse(path).getroot()
            if public.audit.sha(path)!=green['xmlHashes'][root.get('name')]:raise ValueError('original selected XML, not a later run')
            props={p.get('name'):p.get('value')for p in root.findall('properties/property')}
            context={k:props.get(k)for k in('os.name','os.version','os.arch','java.version','java.vendor','java.vm.version','java.specification.version')}
            if any(value is None for value in context.values()):raise ValueError('original OS/JDK witness missing; no current-value substitute')
            contexts.append(context)
    if len(contexts)!=5 or any(value!=contexts[0]for value in contexts):raise ValueError('same coherent selected runtime environment')
    value={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'programId':'NK-MSG-002','specification':'../001_SnapshotScratch_単体テスト仕様書.md',
        'sourceSnapshot':green['sourceSnapshot'],'branchAtSourceCommit':'dev-foundation',
        'branchEvidence':'Recorded [dev-foundation a19a9f7d9] commit/push immediately before original Green. Original runner did not separately capture branch; no current branch substituted as a past measurement.',
        'originalStartedUTC':green['startedUTC'],'originalCompletedUTC':green['completedUTC'],'commands':green['commands'],'actualExit':green['actualExit'],
        'originalEnvironmentFromFiveXml':contexts[0],'maven':'3.9.12 fixed executable path in original commands and documented toolchain; no later version used as a past observation',
        'input':'Four synthetic byte-array scratch-fault vectors, seven independent codec vectors, eighteen explicitly inventoried dependency contracts',
        'expected':'001/002 native acquired0; negative003/004 acquired1; end at synthetic fault0; identical fixed Error; original independent wire/JCE values unchanged',
        'actual':'29 exact cases PASS/FES0; every count/Error identity assertion passed; target L154 M14 C1 B70, all missed0',
        'bugIds':['BUG-1453','BUG-1456','BUG-1457'],'yktIds':['YKT-1217','YKT-1220','YKT-1221'],'sscIds':[],
        'dataManifest':{'path':'output/PG5544-scratch-v1/manifest.json','sha256':public.audit.sha(output)},
        'originalReceiptSha256':public.audit.sha(public.audit.W/public.audit.RUN/'manifest.safe.json'),
        'coverageScope':'Named codec target100 only; complete selected API XML retained with session hashes; new-source whole/native/451 pending',
        'formalAccepted':False,'wholeAccepted':False,'oldNativeImported':False,'rawSecretsOrPropertiesPublished':False}
    target=public.BASE.parent.parent/'manifest.json'
    with target.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sourceSnapshot':green['sourceSnapshot'],'sha256':public.audit.sha(target),'fiveXmlRuntimeCoherent':True,'formalAccepted':False},sort_keys=True))


if __name__=='__main__':main()
