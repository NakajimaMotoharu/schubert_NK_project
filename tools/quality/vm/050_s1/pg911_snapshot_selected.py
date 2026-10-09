"""Selected genuine state-data contract oracles; main code unchanged, VM untouched."""
import inspect
import pg743_closing_selected as selected
selected.D=selected.W/'pg911-snapshot-selected-v1'
selected.TESTS={'batch':['InspectorHeldStateContractTest','InspectorUnitSnapshotTest','InspectorUnitCycleTest','InspectorUnitProbeTest','MorningControlScopeTest']}
if __name__=='__main__':
 raw=inspect.getsource(selected.main).replace('src/schubert-nk-bootstrap,src/schubert-nk-api','src/schubert-nk-batch').replace('PG743-closing-selected-v1','PG911-snapshot-selected-v1').replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','e01612fcd7f2752df5ae0836b78538fd5e87f120')
 env=dict(selected.__dict__);exec(compile(raw,'<911 selected batch contracts>','exec'),env);env['main']()
