"""PG926 qualified explicit non-root reactor, four selected batch suites only."""
import inspect
import pg743_closing_selected as selected
selected.D=selected.W/'pg1009-stream-selected-v3'
selected.TESTS={'batch':['InspectorUnitProbeTest','BrokerJournalQueryTest','InspectorHeldStateContractTest','InspectorUnitSnapshotTest']}

def source():
    code=inspect.getsource(selected.main)
    marker="'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',";assert code.count(marker)==1
    code=code.replace(marker,"'src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch',")
    assert "'-am'"not in code
    return code.replace('PG743-closing-selected-v1','PG1009-stream-selected-v3').replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','40ef6e894573d2ffab1d1732124960f9c98d5f97')

if __name__=='__main__':
    env=dict(selected.__dict__);exec(compile(source(),'<PG1009 qualified explicit dependency reactor>','exec'),env);env['main']()
