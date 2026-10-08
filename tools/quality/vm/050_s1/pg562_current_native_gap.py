"""PG561 same-source sealed diagnostic XML and method gaps. Private XML, safe coordinates only."""
import hashlib,json,os,pathlib,subprocess,xml.etree.ElementTree as ET
T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
def main():
 os.umask(0o077);prior=W/'pg561-current-native-v2';record=json.loads((prior/'manifest.safe.json').read_bytes());assert record['actualExit']==0 and record['formalAccepted']is False
 target=W/'pg562-current-native-gap-v1';assert not target.exists();target.mkdir(mode=0o700);classes=target/'classes';classes.mkdir(mode=0o700)
 repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
 for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
  matches=list(repo.glob(pattern));assert len(matches)==1;cp.append(str(matches[0]))
 r=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(classes),str(T/'tools/quality/vm/050_s1/NativeCoverageXml471.java')],capture_output=True);assert r.returncode==0 and not r.stdout and not r.stderr
 modules=['protocol','storage','bootstrap','api','web','batch'];host=W/'pg540-six-host-v1';data=[host/m/'jacoco.exec'for m in modules]+[prior/(str(n)+'.exec')for n in range(9)]
 for m,p in zip(modules,data):assert hashlib.sha256(p.read_bytes()).hexdigest()==record['hostExecHashes'][m]
 for n,p in enumerate(data[6:]):assert hashlib.sha256(p.read_bytes()).hexdigest()==record['currentNativeFiles'][n]['sha256']
 summary={};delta={};jar_hashes={};xml_hashes={}
 for module in modules:
  jar=host/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');xml=target/(module+'.xml');jar_hashes[module]=hashlib.sha256(jar.read_bytes()).hexdigest()
  r=subprocess.run([str(J/'java'),'-cp',str(classes)+':'+':'.join(cp),'NativeCoverageXml471',str(jar),str(xml),*[str(p)for p in data]],capture_output=True,timeout=45);assert r.returncode==0 and not r.stderr
  root=ET.parse(xml).getroot();counts={c.attrib['type']:int(c.attrib['missed'])for c in root.findall('counter')};before={c.attrib['type']:int(c.attrib['missed'])for c in ET.parse(host/module/'site/jacoco/jacoco.xml').getroot().findall('counter')}
  assert all(counts[k]==record['moduleCounters'][module][k]['missed']and counts[k]<=before[k]for k in ('LINE','METHOD','CLASS','BRANCH'))
  delta[module]={k:{'hostMissed':before[k],'hostPlusCurrentNineMissed':counts[k],'newlyCovered':before[k]-counts[k]}for k in ('LINE','METHOD','CLASS','BRANCH')}
  gaps=[]
  for package in root.findall('package'):
   for c in package.findall('class'):
    missed={x.attrib['type']:int(x.attrib['missed'])for x in c.findall('counter')}
    if any(missed.get(k,0)for k in ('LINE','METHOD','CLASS','BRANCH')):
     methods=[{**m.attrib,'missed':{x.attrib['type']:int(x.attrib['missed'])for x in m.findall('counter')}}for m in c.findall('method')if any(int(x.attrib['missed'])for x in m.findall('counter')if x.attrib['type']in('LINE','METHOD','BRANCH'))]
     gaps.append({'class':c.attrib['name'],'source':c.attrib.get('sourcefilename'),'missed':missed,'methods':methods})
  summary[module]=gaps;xml_hashes[module]=hashlib.sha256(xml.read_bytes()).hexdigest()
 safe={'productionSource':record['productionSource'],'priorNativeManifestSha256':hashlib.sha256((prior/'manifest.safe.json').read_bytes()).hexdigest(),'frozenClassJarHashes':jar_hashes,'privateXmlHashes':xml_hashes,'counterDelta':delta,'gaps':summary,'formalAccepted':False}
 with (target/'gap.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'newlyCovered':{k:sum(v[k]['newlyCovered']for v in delta.values())for k in ('LINE','METHOD','CLASS','BRANCH')},'gapOuterFamilies':{m:len(v)for m,v in summary.items()},'formalAccepted':False,'safeSha256':hashlib.sha256((target/'gap.safe.json').read_bytes()).hexdigest()}))
if __name__=='__main__':main()
