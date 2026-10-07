"""One private XML extraction over the already verified immutable full+8native.
Only code coordinates/counters reach stdout; no exec/session/raw/source content.
"""
import hashlib,json,os,pathlib,subprocess,xml.etree.ElementTree as ET
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
manifest=json.loads((W/'pg531-native-diagnostic-v1.safe.json').read_text())
assert manifest['eligibleCurrentStreams']==8 and all(v['classByteMismatch']==v['unknownProductionClasses']==0 and v['singleSession'] and v['currentWindowAndRole'] for v in manifest['streams'])
assert subprocess.check_output(['git','diff',manifest['productionSource'],'--','src','pom.xml'],cwd=T)==b''
root=W/'pg532-native-gap-v1';assert not root.exists();root.mkdir(mode=0o700);classes=root/'classes';classes.mkdir(mode=0o700)
repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
    files=list(repo.glob(pattern));assert len(files)==1;cp.append(str(files[0]))
r=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(classes),str(T/'tools/quality/vm/050_s1/NativeCoverageXml471.java')],capture_output=True)
assert r.returncode==0 and not r.stdout and not r.stderr
modules=['protocol','storage','bootstrap','api','web','batch'];host=[W/'pg495-host'/m/'jacoco.exec' for m in modules]
native=[W/('pg531-'+m['role']+'-native-v1.exec') for m in manifest['streams'] if m['eligibleForCurrentUnion']]
summary={};hashes={}
for module in modules:
    xml=root/(module+'.xml');jar=W/'pg495-host'/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
    r=subprocess.run([str(J/'java'),'-cp',str(classes)+':'+':'.join(cp),'NativeCoverageXml471',str(jar),str(xml)]+[str(p) for p in host+native],capture_output=True,timeout=45)
    assert r.returncode==0 and not r.stderr and b'classMismatch0=true' in r.stdout
    doc=ET.parse(xml).getroot();counters={c.attrib['type']:int(c.attrib['missed']) for c in doc.findall('counter')}
    assert all(counters[c]==manifest['counters'][module][c]['missed'] for c in ['LINE','METHOD','CLASS','BRANCH'])
    gap=[]
    for package in doc.findall('package'):
        for c in package.findall('class'):
            misses={k.attrib['type']:int(k.attrib['missed']) for k in c.findall('counter')}
            if any(misses.get(k,0) for k in ['LINE','METHOD','CLASS','BRANCH']):
                methods=[{**m.attrib,'missed':{k.attrib['type']:int(k.attrib['missed']) for k in m.findall('counter')}} for m in c.findall('method') if any(int(k.attrib['missed']) for k in m.findall('counter') if k.attrib['type'] in ['LINE','METHOD','BRANCH'])]
                gap.append({'class':c.attrib['name'],'source':c.attrib.get('sourcefilename'),'missed':misses,'methods':methods})
    summary[module]=gap;hashes[module]=hashlib.sha256(xml.read_bytes()).hexdigest()
with (root/'gap.safe.json').open('x') as stream:json.dump({'productionSource':manifest['productionSource'],'formal':False,'xmlPrivateHashes':hashes,'gaps':summary},stream,indent=2);stream.write('\n')
print(json.dumps({'run':'PG532-native-gap-v1','source':manifest['productionSource'],'gapClasses':{m:len(v)for m,v in summary.items()},'missedTotals':{c:sum(manifest['counters'][m][c]['missed']for m in modules)for c in ['LINE','METHOD','CLASS','BRANCH']},'safeGapSha256':hashlib.sha256((root/'gap.safe.json').read_bytes()).hexdigest(),'formal':False}))
