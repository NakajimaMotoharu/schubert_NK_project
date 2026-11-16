"""Preserve original failed6 XML/exec with property redaction; never reinterpret failure as acceptance."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
from pgpt_public_unit_xml import copy_public_evidence
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';mp=b/'evidence/PG36150-named-record-collection-unit-v1/manifest.json';m=json.loads(mp.read_text());assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(1,6,1,0,0);w=r.parent/'pgpt-runs/PG379/pg36150-named-record-collection-v1';o=b/'evidence/PG36157-named-record-failed-unit-public-v1';o.mkdir();files={};counts=dict(tests=0,failed=0,error=0,skipped=0)
for p in [w/'jacoco.exec',w/'coverage.xml',*sorted((w/'xml').glob('TEST-*.xml'))]:
 result=copy_public_evidence(p,o/p.name);files[p.name]=result
 if p.name.startswith('TEST-'):
  for case in ET.parse(o/p.name).findall('.//testcase'):
   counts['tests']+=1
   for key,tag in [('failed','failure'),('error','error'),('skipped','skipped')]:counts[key]+=case.find(tag) is not None
assert counts==dict(tests=6,failed=1,error=0,skipped=0);v=dict(actualExit=0,originalUnitExit=1,counts=counts,source=m['begin']['source'],productionCoreMain=m['begin']['productionCoreMain'],originalManifest=dict(path=str(mp.relative_to(r)),sha256=hashlib.sha256(mp.read_bytes()).hexdigest()),files=files,productReexecuted=False,failureAccepted=False,coverageCreditedToPass=False,rawPropertiesOrSystemOutErrExported=False);(o/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,originalUnitExit=1,tests=6,failed=1,failureAccepted=False)))
