"""Current byte-equivalent batch selected streaming outcomes, no VM action."""
import inspect
import pg743_closing_selected as selected
selected.D=selected.W/'pg1007-stream-selected-v1'
selected.TESTS={'batch':['InspectorUnitProbeTest','BrokerJournalQueryTest','InspectorHeldStateContractTest','InspectorUnitSnapshotTest']}

if __name__=='__main__':
    code=inspect.getsource(selected.main)
    marker="'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',"
    assert code.count(marker)==1
    code=code.replace(marker,"'src/schubert-nk-batch', '-am',")
    code=code.replace('PG743-closing-selected-v1','PG1007-stream-selected-v1').replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','40ef6e894573d2ffab1d1732124960f9c98d5f97')
    env=dict(selected.__dict__);exec(compile(code,'<PG1007 selected body>','exec'),env);env['main']()
