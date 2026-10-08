"""Seal the completed selected source; no build rerun, no source/main/native acceptance."""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

os.umask(0o077)
T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
RUN='PG541-timeout-cardinality-selected-v1'
stem=W/RUN.lower();source=pathlib.Path(str(stem)+'.source').read_text().strip()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=T).decode().strip()==source
assert pathlib.Path(str(stem)+'.exit').read_text()=='0\n'
assert subprocess.run(['sha256sum','--check','--status',str(stem)+'.source-files.sha256'],cwd=T).returncode==0
root=W/(RUN.lower()+'-artifacts-v1');assert not root.exists();root.mkdir(mode=0o700)
inventory=json.loads((T/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
owners=['WBS-P017-12'];targets={}
for item in inventory['artifacts']:
 if item['kind']=='JAVA' and item['owner'] in owners and item.get('counterApplicability') != 'NO_EXECUTABLE_INTERFACE':
  targets.setdefault(item['owner'],[]).append((item['module'],item['class']))
modules=[];families={};tests=suites=0
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['storage','bootstrap','batch']:
 p=T/('src/schubert-nk-'+name+'/target');d=root/name;d.mkdir(mode=0o700)
 for rel in ['site/jacoco/jacoco.xml','jacoco.exec','spotbugsXml.xml','schubert-nk-'+name+'-0.1.0-SNAPSHOT.jar']:
  target=d/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/rel,target)
 reports=d/'surefire-reports';reports.mkdir(mode=0o700)
 for q in(p/'surefire-reports').glob('TEST-*.xml'):shutil.copyfile(q,reports/q.name)
 xs=[ET.parse(q).getroot()for q in reports.glob('TEST-*.xml')]
 pt={k:sum(int(q.attrib.get(k,0))for q in xs)for k in ['tests','failures','errors','skipped']}
 assert pt['tests']>0 and pt['failures']==pt['errors']==pt['skipped']==0
 assert not ET.parse(d/'spotbugsXml.xml').getroot().findall('.//BugInstance')
 xml=d/'site/jacoco/jacoco.xml';doc=ET.parse(xml).getroot();groups={}
 for c in doc.findall('./package/class'):
  family=c.attrib['name'].split('$')[0];values=groups.setdefault(family,{k:[0,0]for k in ['LINE','METHOD','CLASS','BRANCH']})
  for counter in c.findall('counter'):
   key=counter.attrib['type']
   if key in values:values[key][0]+=int(counter.attrib['missed']);values[key][1]+=int(counter.attrib['covered'])
 families[name]=groups
 jar=d/('schubert-nk-'+name+'-0.1.0-SNAPSHOT.jar');prior=W/'pg540-six-host-v1'/name/jar.name
 with zipfile.ZipFile(jar)as a,zipfile.ZipFile(prior)as b:
  current=[n for n in a.namelist()if n.endswith('.class')];original=[n for n in b.namelist()if n.endswith('.class')]
  assert len(current)==len(set(current)) and len(original)==len(set(original)) and set(current)==set(original)
  assert all(a.read(n)==b.read(n)for n in current)
 modules.append({'module':name,'pt':pt,'suites':len(xs),'coverageXmlSha256':digest(xml),'jarSha256':digest(jar),
                 'priorJar':str(prior),'priorJarSha256':digest(prior),'spotbugsXmlSha256':digest(d/'spotbugsXml.xml'),
                 'productionClassInventoryEqual':True,'comparedClasses':len(current),'classByteMismatch':0,
                 'missed':{c.attrib['type']:int(c.attrib['missed'])for c in doc.findall('counter')if c.attrib['type']in ['LINE','METHOD','CLASS','BRANCH']}})
 tests+=pt['tests'];suites+=len(xs)
measured={}
for owner,items in targets.items():
 sums={k:{'missed':0,'covered':0}for k in ['LINE','METHOD','CLASS','BRANCH']}
 for module,family in items:
  assert family in families[module],(module,family)
  for key,(miss,cover)in families[module][family].items():sums[key]['missed']+=miss;sums[key]['covered']+=cover
 measured[owner]={'families':len(items),'counters':sums}
guard = families['batch']['dev/codex/schubert/nk/batch/cleanup/MaintenanceMutationGuard']
assert all(v[0] == 0 for v in guard.values())
for item in inventory['artifacts']:
 if item['kind']=='JAVA' and item['owner'] in owners and item.get('counterApplicability') == 'NO_EXECUTABLE_INTERFACE':
  assert all(sum(v) == 0 for v in families[item['module']][item['class']].values())
measured['WBS-P017-12']['nonExecutableFamilies']=1
summary={'programId':'NK-BAT-001/NK-OPS-001','run':RUN,'runRecordStem':str(stem),'wbsIds':owners,
         'source':source,'productionSource':'969d8ded10c0bf5841d9e3a5c531e922caf4a24a','deployedVmSource':'a2e98ce9e96c42425921e3686e8ae7a94bff9e6c','branch':'dev-foundation',
         'actualExit':0,'sourceUnchanged':True,'FES':0,'staticIssues':0,
         'startedJST':pathlib.Path(str(stem)+'.started').read_text().strip(),'completedJST':pathlib.Path(str(stem)+'.completed').read_text().strip(),
         'command':'bash tools/quality/vm/050_s1/pg541_timeout_pt_v1.sh <fixed HEAD40>',
         'environment':{'os':'Linux 7.0.0-38-generic','jdk':'25.0.4','maven':'3.9.12','jacoco':'0.8.15','spotbugsPlugin':'4.10.4.0','hostUid':1000},
         'coverageRoot':str(root),'logSha256':digest(pathlib.Path(str(stem)+'.log')),'tests':tests,'suites':suites,
         'modules':modules,'wbsMeasurements':measured,'newProductionTests':1,'all715ProductionClassBytesSameAsPG540':True,
         'formalUpdated':False,'acceptedWbsDelta':0,'nativeAccepted':False,'ITSTAccepted':False,
         'testIds':['PT-MG541001'],
         'maintenanceMutationGuardCounters':guard,'remainingMorningCompletionEvidenceBranches':0,'rawExportedToGit':False,
         'collectorSourceSha256':digest(pathlib.Path(__file__)),'collectorMode':'post-run uncommitted helper SHA; Maven run source fixed separately'}
out=W/'pg541-timeout-cardinality-selected-v1.safe.json'
with out.open('x')as f:json.dump(summary,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'run':RUN,'source':source,'tests':tests,'suites':suites,'measured':measured,'safeSha256':digest(out),'formalUpdated':False}))
