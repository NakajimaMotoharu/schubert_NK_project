"""BUG3191: keep both added registrations, repair only an immutable historical metadata table."""
from pathlib import Path
import datetime,hashlib,json,subprocess
from wbs_current_source_structure import value_digest
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
d=ld(p);before=p.read_bytes();view=d['currentSourceArtifactStructureView20261108'];origin='b1c68a0c1e54f15c2507f85aec99e81db037ddc1';original=json.loads(subprocess.check_output(['git','show',origin+':'+str(p.relative_to(r))]));legacy=original['currentPhysicalCandidate'];current=d['currentPhysicalCandidate'];registry=d['artifacts']
assert value_digest(legacy)==view['preservedLegacyCandidateDigest'] and len(legacy['artifacts'])==943 and len(current['artifacts'])==945
assert set(legacy)==set(current) and all(current[k]==v for k,v in legacy.items() if k!='artifacts')
old={x['path']:x for x in legacy['artifacts']};now={x['path']:x for x in current['artifacts']};reg={x['path']:x for x in registry};assert set(old)<=set(now) and all(now[n]==v for n,v in old.items())
extras=sorted(set(now)-set(old));expected=['src/schubert-nk-api/src/main/resources/db/migration/V029__strict_nullable_compound_checks.sql','src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningSqlFailures.java'];assert extras==expected
assert all(now[n]==reg[n] and now[n]['acceptance']=='NOT_RUN' for n in extras)
out=b/'evidence/PG37820-wbs-fixed-candidate-history-repair-v1';assert not out.exists();out.mkdir();beforefile=out/'previous-mixed-candidate945.json';beforefile.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n');extrafile=out/'later-registrations2-preserved.json';extrafile.write_text(json.dumps([now[n] for n in extras],ensure_ascii=False,indent=2)+'\n')
d['currentPhysicalCandidate']=legacy
assert d['artifacts']==registry and p.read_bytes()==before
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');assert value_digest(ld(p)['currentPhysicalCandidate'])==view['preservedLegacyCandidateDigest']
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),legacyOrigin=origin,candidateSourceUnchanged=legacy['source']==current['source'],old943RowsExact=True,otherCandidateTopFieldsExact=True,currentRegistry1123Unchanged=True,newRegistrations2PreservedInRegistryAndSidecar=extras,rawSourceSqlOrMainRead=False,previousMixedCandidate=ref(beforefile),preservedRegistrations=ref(extrafile),beforeInventorySha256=hashlib.sha256(before).hexdigest(),afterInventorySha256=sha(p),fixedCandidateSemanticSha256=value_digest(legacy),oldViewExpectedDigestUnchanged=True,noGitResetOrHistoryRewrite=True,newAcceptance=0,formalUpdated=False,latestProductionSourceQualified=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,old943Exact=True,twoLaterRowsPreserved=True,sourceRead=False,wholeWbsAccepted=False))
