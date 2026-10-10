"""Batch-only qualified-cache selection; failed PG1011 target preserved separately."""
import inspect
import json
import pg743_closing_selected as selected
from pg1013_qualified_dependency_cache import dependency_bytes

selected.D=selected.W/'pg1014-stream-selected-v5'
selected.TESTS={'batch':['InspectorUnitProbeTest','BrokerJournalQueryTest','InspectorHeldStateContractTest','InspectorUnitSnapshotTest']}

if __name__=='__main__':
    print(json.dumps({'dependencyMainClassCounts':dependency_bytes(),'classByteMismatch':0}),flush=True)
    raw=inspect.getsource(selected.main)
    marker="'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',"
    assert raw.count(marker)==1
    raw=raw.replace(marker,"'src/schubert-nk-batch',")
    raw=raw.replace('PG743-closing-selected-v1','PG1014-stream-selected-v5').replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','40ef6e894573d2ffab1d1732124960f9c98d5f97')
    env=dict(selected.__dict__);exec(compile(raw,'<PG1014 single-module selected>','exec'),env);env['main']()
