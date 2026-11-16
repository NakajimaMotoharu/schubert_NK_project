"""Verify four real original javac map shapes and malformed variants, no product execution."""
from pathlib import Path
import copy,hashlib,json,subprocess,zipfile
import pgpt_closed_host_profile as p
from pgpt_closed_host_post_v3 import validate_switch_map_shape
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();c=ld(b/'input/4284_ssc444_protocol_profile_v3.json');old=ld(b/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json');jar=Path(old['jar']['path']);assert sha(jar)==old['jar']['sha256'];w=r.parent/'pgpt-runs/PG379/pg36114-compiler-map-shape-v1';o=b/'evidence/PG36114-compiler-map-shape-selftest-v1';w.mkdir();o.mkdir();checks=[];texts={}
with zipfile.ZipFile(jar) as z:
 for item in c['standardCompilerSwitchMaps']:
  name=item['className']+'.class';p.relative_name(name);data=z.read(name);assert hashlib.sha256(data).hexdigest()==old['physicalClassHashes'][name];path=w/name;path.parent.mkdir(parents=True,exist_ok=True);path.open('xb').write(data);cmd=[str(r.parent/'toolchain/jdk-25.0.4/bin/javap'),'-p','-v',str(path)];v=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert v.returncode==0 and not v.stderr;validate_switch_map_shape(v.stdout,item);texts[item['className']]=v.stdout;checks.append(dict(className=item['className'],realShapePassed=True));(o/(path.name+'.javap.txt')).open('x').write(v.stdout)
item=next(x for x in c['standardCompilerSwitchMaps'] if x['className'].endswith('LayoutFieldCatalog$1'));text=texts[item['className']]
for label,body,meta in [('missing_field',text.replace('static final int[] $SwitchMap$dev$codex$schubert$nk$protocol$layout$Presence;',''),item),('wrong_field_count',text.replace('fields: 2, methods: 1,','fields: 1, methods: 1,'),item),('extra_method',text.replace('fields: 2, methods: 1,','fields: 2, methods: 2,'),item),('wrong_source',text.replace('SourceFile: "LayoutFieldCatalog.java"','SourceFile: "Other.java"'),item),('wrong_enum',text,dict(item,enumClass='dev.codex.schubert.nk.protocol.file.MediaType'))]:
 try:validate_switch_map_shape(body,copy.deepcopy(meta))
 except ValueError:checks.append(dict(negative=label,rejected=True))
 else:raise AssertionError(label)
v=dict(actualExit=0,toolChecks=len(checks),checks=checks,originalProtocolJarSha256=sha(jar),verifierSha256=sha(r/'tools/quality/pgpt_closed_host_post_v3.py'),productionClassInitialization=0,applicationTestsExecuted=0,defaultFiltersChanged=False,all176PhysicalStillRequiredInRaw=True);(o/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolChecks=len(checks),applicationTestsExecuted=0)))
