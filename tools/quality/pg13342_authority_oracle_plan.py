"""Bind current six source originals/seven sites/SS314 and protected actual-encoder assertions before PG."""
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13340_authority_oracle_config as cfg
import f03_authority_oracle_sources as source
OUT = data.BASE/'PG13342-authority-oracle-plan-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13342-authority-oracle-plan-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    n = data.read_checked(data.BASE/cfg.OLD_NORMAL[0]/'manifest.json',cfg.OLD_NORMAL[1]);SLOT.mkdir()
    data.write(SLOT/'begin.safe.json',dict(source=cfg.BASE_SOURCE,invocation=invocation,sourceHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in cfg.SPECS},productTestsExecuted=0))
    ids,refs,pending = cfg.PREVIOUS_STATE();assert [len(v) for v in [ids,refs,pending]] == [7747,3349,1370]
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    removed, = [r for r in original if r['id'] == cfg.REMOVED_FINDING];assert removed['id'] in ids-refs and removed['rule'] == 'AvoidDuplicateLiterals' and '"ROLE_USER" appears 4 times' in removed['message']
    protected = {p:n['begin']['inputHashes'][p] for p in cfg.PROTECTED};assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in protected.items())
    rows = [];domain = source.ss_domain()
    for path,spec in cfg.SPECS.items():
        old = (data.ROOT/path).read_text();assert data.sha(old.encode()) == spec['sha256'] == n['begin']['inputHashes'][path]
        new = source.planned(path);proof = source.project(source.tokens(new),spec,old);labels = source.negatives(new,spec,old)
        rows.append(dict(path=path,originalSha256=spec['sha256'],canonicalOwner=spec['owner'],canonicalCostOwner=spec['owner'],callerSites=source.callers(old),projection=proof,
            originalRoleLiteralCounts={value:Counter(source.tokens(old))[source.tokens('"'+value+'"')[0]] for _,value in cfg.FIELDS.values()},negativeLabels=labels,negativeVectors=len(labels)))
    assert sum(len(r['callerSites']) for r in rows) == 7 and len(rows)*len(domain) == 12
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,source=cfg.BASE_SOURCE,sourceRows=rows,protectedSourceHashes=protected,ssReference=dict(path=cfg.SS[0],sha256=cfg.SS[1],originMainByteEqual=True),
        domain=domain,oracleCallsPlanned=7,newPrivateHelpers=6,newPrivateFixedFields=12,removedPmdFinding=removed,metadataNegativeVectors=sum(r['negativeVectors'] for r in rows),
        unresolvedR09AcceptanceOwnership='UNKNOWN_UNCHANGED_NOT_SOURCE_OWNER_INFERRED',sourceCodeChanged=False,newTestIds=0,productTestsExecuted=0,newAccepted=0,coverage=None,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
