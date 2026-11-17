"""Exact two static decisions, class-complete actual API2 SB, no checks suppressed."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as E
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();folder=b/'evidence/PG37342-request-details-prepare-v1';p=ld(folder/'manifest.json');assert p['actualExit']==0 and p['heldFourClassfileActions']==0 and p['mainSourceCount']==279
assert all(sha(r/n)==h for n,h in p['inputHashes'].items());assert all(sha(r/n)==h for n,h in p['testSourceHashes'].items());decisions=[]
for title in ['main','test']:
 root=E.parse(folder/(title+'-pmd.xml')).getroot();assert not any(x.tag.rsplit('}',1)[-1] in ['error','suppressedviolation'] for x in root)
 for f in root:
  if not f.tag.endswith('file'):continue
  path=Path(f.get('name'));lines=path.read_text().splitlines()
  for v in f:
   assert v.tag.endswith('violation');rule=v.get('rule');line=int(v.get('beginline'));anchor=lines[line-1].strip()
   if title=='main':
    assert rule=='UnusedReturnValue' and anchor=='reader.peek();';reason='STRICT Gson reader peek after endObject is an intentional trailing-document rejection: only successful value is END_DOCUMENT. Its checked parse exception is the contract, not token consumption. Original source comment and PT-IDEM012 independent {} {},{}true,comments plus RAW003 trailing canary prove rejection/fixed exception. Keeping the old parser behavior avoids relaxing oracle.'
   else:
    assert rule=='AvoidAccessibilityAlteration' and anchor=='constructor.setAccessible(true);';reason='Exact pure RequestLogDetails zero-arg private ctor only, restore flag in finally and assert false. No arbitrary type lookup/Root/private key/runtime/authority access. RAW001 verifies non-instantiation invariant; no broad reflection helper.'
   decisions.append(dict(path=str(path.relative_to(r)),sourceSha256=sha(path),line=line,rule=rule,anchor=anchor,decision='NOT_APPLICABLE',reason=reason))
assert len(decisions)==2
sb=E.parse(folder/'spotbugsXml.xml').getroot();assert not sb.findall('BugInstance') and not sb.findall('.//MissingClass') and not sb.findall('.//Error');assert {x.get('class') for x in sb.findall('.//ClassStats')}=={n[:-6].replace('/','.') for n in p['physicalClassHashes']['api']}
out=b/'evidence/PG37344-request-details-static-admission-v1';assert not out.exists();out.mkdir();(out/'pmd-decisions.json').write_text(json.dumps(decisions,indent=2)+'\n');(out/'manifest.json').write_text(json.dumps(dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMain=p['productionCoreMain'],preparePath=str((folder/'manifest.json').relative_to(r)),prepareSha256=sha(folder/'manifest.json'),rawPmdSites=2,applicable=0,unclassified=0,checkstyle=0,spotbugsAllApiPhysical2=True,spotbugsBugMissingErrors=0,originalPomsNullAwayCompile279=True,heldFourClassfileActions=0,productTestsExecuted=0,rulesOrSuppressionChanges=0,formalUpdated=False),indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawPmd2=True,applicable=0,unclassified=0,testsExecuted=0)))
