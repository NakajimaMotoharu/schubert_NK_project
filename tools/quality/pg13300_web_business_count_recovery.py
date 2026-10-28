"""Record original count guard1 without replay, verify every same-source mapping and reject bad totals."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13286_web_business_literal_config as old
import pg13301_web_business_literal_config_v2 as cfg
from f03_literal_batch_sources import select,prior_normal,out
OUT = data.BASE/'PG13300-web-business-count-recovery-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not out(old,old.ORIGINAL_NUMBER).exists()
    normal = prior_normal(cfg);rows = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    ids,refs,_ = cfg.PREVIOUS_STATE();counts = {}
    for path,(sha,count,_) in cfg.PATHS.items():
        raw = (data.ROOT/path).read_bytes();assert data.sha(raw) == sha == normal['begin']['inputHashes'][path]
        counts[path] = len(select(raw.decode(),[r for r in rows if r['path'] == path and r['id'] in ids-refs],count))
    assert sum(counts.values()) == 149 and old.EXPECTED_CORRECTIONS == 159
    labels = []
    bad_paths = copy.deepcopy(cfg.PATHS);bad_paths.pop(next(iter(bad_paths)))
    bool_paths = copy.deepcopy(cfg.PATHS);p = next(iter(bool_paths));sha,_,owner = bool_paths[p];bool_paths[p] = (sha,True,owner)
    for label,paths,total in [('old-159',cfg.PATHS,159),('missing-file',bad_paths,149),('bool-count',bool_paths,149),('bool-total',cfg.PATHS,True)]:
        try:cfg.checked_total(paths,total)
        except AssertionError:labels.append(label)
        else:raise AssertionError('invalid total accepted')
    failed = {'tools/quality/pg13286_web_business_literal_config.py':'d5feb072e4f382ee0731737a2ff091051982bedca82ee746d21a814756f0245c',
        'tools/quality/pg13288_web_business_originals.py':'a3f1f1f9ce2742d2345e8675c5689d0b665de7e0f6370dbf10e3b4c3bd92a2a3'}
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in failed.items())
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,source=cfg.BASE_SOURCE,
        originalFailedInvocation=dict(session=29918,actualExit=1,operatorObserved=True,originalFailureReportPersisted=False,entryAndConfigHashes=failed,originalOutAbsent=True,sourceChanged=False),
        originalPlannedTotal=159,correctedTotal=149,perFileCounts=counts,originalPlannedNegatives=204,correctedNegatives=194,metadataNegativeVectors=len(labels),negativeLabels=labels,
        targetsOrOriginalHashesChanged=False,startEstimateChanged=False,sourceCodeChanged=False,productTestsExecuted=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
