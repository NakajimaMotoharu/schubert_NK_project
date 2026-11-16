"""Reconstruct XML independently of the producer summary before returning static acceptance."""
from collections import Counter
from pathlib import Path
import datetime
import hashlib
import json
import xml.etree.ElementTree as ET

r=Path.cwd(); b=r/'evidence/01_PT/018_NK-OPS-001/evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
load=lambda p:json.loads(p.read_text())
cp=b/'PG36820-storage-main-compile-v1/manifest.json'; c=load(cp)
sp=b/'PG36822-storage-main-full-static-v1/manifest.json'; s=load(sp)
pp=b/'PG36824-storage-main-independent-v1/manifest.json'; p=load(pp)
out=b/'PG36826-storage-main-xml-return-v1'; assert not out.exists()
assert c['actualExit']==s['actualExit']==p['actualExit']==0
sb=ET.parse(sp.parent/'spotbugs.xml').getroot()
assert not any(sb.findall('.//'+name) for name in ['BugInstance','MissingClass','Error'])
stats=[n.get('class') for n in sb.findall('.//ClassStats')]
assert len(stats)==len(set(stats))==80
assert {n.replace('.','/')+'.class' for n in stats}==set(c['physicalClassHashes'])
assert stats==sorted(stats) or sorted(stats)==s['summary']['spotbugs']['classStats']
pd=ET.parse(sp.parent/'pmd.xml').getroot(); raw=[]
assert not [n for n in pd.iter() if n.tag.rsplit('}',1)[-1] in ['error','configerror']]
for node in pd:
    if node.tag.rsplit('}',1)[-1]!='file':continue
    for item in node:
        if item.tag.rsplit('}',1)[-1]=='violation':
            raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),
              **item.attrib,message=(item.text or '').strip()))
assert raw==load(sp.parent/'raw-findings.json') and len(raw)==18
dispositions=load(pp.parent/'pmd18-site-dispositions.json')
assert [v['rawFindingIndex'] for v in dispositions]==list(range(18))
assert [v['raw'] for v in dispositions]==raw
assert all(v['disposition']=='NOT_APPLICABLE' for v in dispositions)
assert Counter(v['raw']['rule'] for v in dispositions)==Counter(
    AvoidCatchingGenericException=8,AvoidInstanceofChecksInCatchClause=10)
out.mkdir()
m=dict(actualExit=0,source=c['sourceCore'],terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 sourceDomain='CURRENT_STORAGE25_STATIC_FULL80_XML_INDEPENDENT_NOT_PRODUCT_PT',
 compile=ref(cp),static=ref(sp),siteReviewAndPhysicalPost=ref(pp),
 xmlHashes={name:sha(sp.parent/name) for name in ['pmd.xml','spotbugs.xml']},
 mainSources=25,physicalClassStats=80,staticApplicable=0,unclassified=0,
 rawPmdFindings=18,individuallyClassifiedPmdFindings=18,missingClasses=0,analysisErrors=0,
 productTestsExecuted=0,old39Replayed=0,heldClassfileActions=0,actualDbVmNativeServiceActions=0,
 wholeProductCoverageAccepted=False,wholeF03Accepted=False,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').open('x').write(json.dumps(m,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,Main25=True,physical80=True,raw18classified=True)))
