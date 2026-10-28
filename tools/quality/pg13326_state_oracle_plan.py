"""Bind two same-byte source originals and fixed UI eight cases, before required source-only oracle PG."""
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13324_state_oracle_config as cfg
import f03_state_oracle_sources as source
OUT = data.BASE/'PG13326-state-oracle-plan-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13326-state-oracle-plan-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists();normal = data.read_checked(data.BASE/cfg.OLD_NORMAL[0]/'manifest.json',cfg.OLD_NORMAL[1])
    SLOT.mkdir();data.write(SLOT/'begin.safe.json',dict(source=cfg.BASE_SOURCE,invocation=invocation,sourceHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in cfg.SPECS},uiSha256=data.sha((data.ROOT/cfg.UI[0]).read_bytes()),productTestsExecuted=0))
    ids,refs,pending = cfg.PREVIOUS_STATE();assert [len(x) for x in [ids,refs,pending]] == [7747,3349,1370]
    domains = source.ui_domain();rows = []
    for path,spec in cfg.SPECS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == spec['sha256'] == normal['begin']['inputHashes'][path]
        planned = source.planned(path);proof = source.project(source.tokens(planned),spec,text);labels = source.negatives(planned,spec,text)
        rows.append(dict(path=path,originalSha256=spec['sha256'],canonicalOwner=spec['owner'],canonicalCostOwner=spec['owner'],existingCallers=source.callers(text),
            helperName=spec['helper'],enum=spec['enum'],fixedFields=spec['fields'],projection=proof,negativeLabels=labels,negativeVectors=len(labels)))
    assert sum(len(r['existingCallers']) for r in rows) == 8 and sum(len(r['fixedFields']) for r in rows) == 8
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,source=cfg.BASE_SOURCE,operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        sourceRows=rows,domainCases=domains,originalSourceRetrieval='git show '+cfg.BASE_SOURCE+':<exact path>, hash checked against pinned normal',originalNormalManifestSha256=cfg.OLD_NORMAL[1],
        uiReference=dict(path=cfg.UI[0],sha256=cfg.UI[1],originMainByteEqual=True),callerCorrections=8,newPrivateHelpers=2,newFields=0,newTestIds=0,productTestsExecuted=0,newAccepted=0,
        sourceCodeChanged=False,staticMetadataNegativeVectors=sum(r['negativeVectors'] for r in rows),coverage=None,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
