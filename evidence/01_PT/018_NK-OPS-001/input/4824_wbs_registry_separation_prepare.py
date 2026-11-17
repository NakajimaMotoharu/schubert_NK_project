"""Preserve exact fixed legacy1061 and current1123 metadata, no artifact source/byte access."""
from pathlib import Path
import datetime,hashlib,json,subprocess
from wbs_current_source_structure import value_digest
import wbs_preparation_registry as registry
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=r/'documents/400_PGPT/470_PMO';ip=p/'485_WBS網羅性・受入対応.json';sp=p/'486_WBS現行実績.json'
ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
inventory=ld(ip);view=inventory['currentSourceArtifactStructureView20261108'];master=ld(p/'481_PGPT詳細WBS.json');snapshot=ld(sp);raw_before=ip.read_bytes();snapshot_before=sp.read_bytes()
origin='b1c68a0c1e54f15c2507f85aec99e81db037ddc1';legacy_source=subprocess.check_output(['git','show',origin+':'+str(ip.relative_to(r))]);legacy= json.loads(legacy_source)['artifacts'];current=inventory['artifacts']
assert len(legacy)==1061 and value_digest(legacy)==view['preservedLegacyArtifactRowsDigest'] and len(current)==1123
old={x['path']:x for x in legacy};now={x['path']:x for x in current};changes={}
for n,x in old.items():
    assert all(x[k]==now[n][k] for k in ['owner','costOwner','kind'])
    delta={k:dict(legacy=v,registered=now[n].get(k)) for k,v in x.items() if now[n].get(k)!=v}
    if delta:changes[n]=delta
assert len(changes)==11 and all(set(v)<= {'sha256','basis'} for v in changes.values())
out=b/'evidence/PG37814-wbs-registry-separation-input-v1';assert not out.exists();out.mkdir()
legacyfile=out/'frozen-legacy-artifacts1061.json';legacyfile.write_text(json.dumps(legacy,ensure_ascii=False,indent=2)+'\n')
observed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();names=subprocess.check_output(['git','ls-tree','-r','--name-only','-z',observed,'--','src','program/characterization/src/main/java']).decode().rstrip('\0').split('\0')
costrefs={n:now[n]['role11DdlStaticEvidence'] for n in sorted(set(now)-set(old)) if now[n]['owner']!=now[n]['costOwner']};assert len(costrefs)==2;proofs={}
for n,reference in costrefs.items():
    file=r/reference['path'];assert reference['path'].startswith('evidence/01_PT/018_NK-OPS-001/evidence/') and reference['path'].endswith('.json');assert sha(file)==reference['sha256'];proofs[n]=ld(file)
binding=dict(schema='WBS_PREPARATION_REGISTRY_SEPARATION_V1',observedGitHead=observed,productionCoreMainAtObservation='a013a6d676454082de3c59bc199e87f37fefe159',legacyOrigin=dict(commit=origin,path=str(ip.relative_to(r)),fileSha256=hashlib.sha256(legacy_source).hexdigest()),legacyReference=ref(legacyfile),legacySemanticSha256=value_digest(legacy),registrySemanticSha256=value_digest(current),registeredAdditions=sorted(set(now)-set(old)),legacyFieldUpdates=changes,retainedRetiredHistoricalPaths=view['retiredHistoricalPaths'],costSeparationReferences=costrefs,runtimeQualified=False,wholeAcceptance=False,sourceBytesRecomputed=False,newAcceptance=0,effortRate=None,meaning='Names and current unqualified registry metadata only; original legacy SHA/source/runtime is never replaced by later hashes. A filename is not an execution permission.')
checked=registry.verify(legacy,current,binding,master['tasks'],names,proofs);assert checked['registeredAdditions']==62
bindingfile=out/'preparation-registry-binding.json';bindingfile.write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n')
assert 'legacyArtifactRows' not in view and 'currentPreparationRegistryBinding20261117' not in inventory
view['legacyArtifactRows']=ref(legacyfile);inventory['currentPreparationRegistryBinding20261117']=ref(bindingfile)
assert current==inventory['artifacts'] and ip.read_bytes()==raw_before and sp.read_bytes()==snapshot_before
ip.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
manifest=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalFixedLegacySemanticHash=view['preservedLegacyArtifactRowsDigest'],legacyOrigin=binding['legacyOrigin'],legacy1061Current1123Preserved=True,currentArraySemanticExact=True,currentRegistryDifferences=checked,oldViewSource=view['source'],latestProductionCoreMainAtObservation=binding['productionCoreMainAtObservation'],oldViewSourceNotRelabelled=True,sourceBytesOrRuntimeAccess=False,formalSnapshotBeforeSha256=hashlib.sha256(snapshot_before).hexdigest(),beforeInventorySha256=hashlib.sha256(raw_before).hexdigest(),afterInventorySha256=sha(ip),oldLegacyDigestNotChanged=True,newAcceptance=0,formalUpdated=False,files=[ref(legacyfile),ref(bindingfile)])
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,legacy1061Preserved=True,registeredAdditions=62,updates=11,ownerCostSeparatedWithProof=2,actualSourceRead=False))
