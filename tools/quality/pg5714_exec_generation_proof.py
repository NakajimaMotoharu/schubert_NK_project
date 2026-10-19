"""Original red/green XML and actual changed bytes; publish only allowlisted diagnostics."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pg5708_exec_generation_selected import ROOT,TC,BASE,RED,sha

W=ROOT.parent/'pgpt-runs/PG379'
SOURCE='6db56feeea6df0e355c018e6b80ad4e40c2d90f5'
SLOT='pg5714-exec-generation-independent-v1'


def main():
    rpath=W/'pg5708-exec-generation-red-v2/manifest.safe.json';gpath=W/'pg5708-exec-generation-green-v1/manifest.safe.json'
    red=json.loads(rpath.read_bytes());green=json.loads(gpath.read_bytes())
    if not(red['purposefulRedEstablished']and red['actualExit']==1 and red['tests']==62 and red['suites']==8 and not red['errors']and not red['skipped']and set(map(tuple,red['failed']))==RED
      and green['sourceSnapshot']==SOURCE and green['greenSelectedQualified']and green['actualExit']==0 and green['tests']==62 and green['suites']==8 and not green['failed']and not green['errors']and not green['skipped']and not any(green['staticBuiltModules'].values())):raise ValueError('original exact red/green first, not arithmetic success')
    reference=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5588-current3905-cases/qualification.json'
    if sha(reference)!='b34549edfd627c6b4606abbbb9a50eadf47153b37e7b3ad7e3f2aa2a30732878':raise ValueError('actual old physical Main reference')
    before=json.loads(reference.read_bytes())['allPhysicalMainSha256'];after=green['allPhysicalMainSha256']
    changed=sorted(k for k in before if before[k]!=after.get(k));prefix='batch:dev/codex/schubert/nk/batch/platform/RootStartupContext'
    if set(before)!=set(after)or len(after)!=1664 or changed!=[prefix+'$NativeIo.class',prefix+'.class']:raise ValueError('exact two physical differences only')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);classes=out/'classes';classes.mkdir()
    helper=ROOT/'tools/quality/MonitorDebugCanonical.java';jdk=TC/'jdk-25.0.4/bin'
    subprocess.run([str(jdk/'javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),str(helper)],check=True)
    differences=[]
    for key in changed:
        module,relative=key.split(':',1)
        old=W/'pg5566-private-monitor-green-v3/source'/('src/schubert-nk-'+module+'/target/classes')/relative
        new=gpath.parent/'source'/('src/schubert-nk-'+module+'/target/classes')/relative
        if sha(old)!=before[key]or sha(new)!=after[key]:raise ValueError('each actual class byte matches its own qualified input')
        parts=subprocess.check_output([str(jdk/'java'),'-cp',str(classes),'MonitorDebugCanonical',str(old),str(new)],text=True).strip().split('\t')
        debug=key.endswith('$NativeIo.class')
        if len(parts)!=3 or parts[2]!=str(debug).lower():raise ValueError('only NativeIo is genuinely debug-only, not an exclusion')
        differences.append({'physicalClass':key,'oldSha256':before[key],'newSha256':after[key],'debugOnly':debug})
    cases=[]
    for module in ('protocol','storage','bootstrap','api','web','batch'):
        for path in(gpath.parent/'source'/('src/schubert-nk-'+module+'/target/surefire-reports')).glob('TEST-*.xml'):
            tree=ET.parse(path).getroot();name=tree.get('name')
            if green['xmlHashes'].get(name)!=sha(path):raise ValueError('exact original selected XML')
            cases.extend({'class':name,'method':c.get('name'),'result':'PASS'}for c in tree.findall('testcase'))
    if len(cases)!=62:raise ValueError('one TestID per actual selected case')
    value={'actualExit':0,'source':SOURCE,'priorSource':BASE,'redManifestSha256':sha(rpath),'greenManifestSha256':sha(gpath),'tests':62,'suites':8,'allPhysicalMain':1664,'physicalDifferences':differences,'cases':cases,'staticBuiltModules':green['staticBuiltModules'],'targetCounters':green['targetCounters'],'formalAccepted':False,'wholeCoverageAccepted':False,'normalNativeQualified':False,'wholeMorningAccepted':False,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5714-exec-generation-selected';public.mkdir()
    with(public/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'tests':62,'suites':8,'allPhysicalMain':1664,'codeChanged':1,'debugOnly':1,'publicManifestSha256':sha(public/'manifest.json'),'formalAccepted':False}))


if __name__=='__main__':main()
