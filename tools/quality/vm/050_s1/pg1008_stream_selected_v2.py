"""Fixed offline plugin coordinates with same-source dependency reactor, cache untouched."""
import inspect
import pg743_closing_selected as selected
selected.D=selected.W/'pg1008-stream-selected-v2'
selected.TESTS={'batch':['InspectorUnitProbeTest','BrokerJournalQueryTest','InspectorHeldStateContractTest','InspectorUnitSnapshotTest']}

def source():
    code=inspect.getsource(selected.main)
    marker="'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',";assert code.count(marker)==1
    code=code.replace(marker,"'src/schubert-nk-batch', '-am',")
    for old,new in [("'spotbugs:check'","'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'"),
                    ("'jacoco:report'","'org.jacoco:jacoco-maven-plugin:0.8.15:report'")]:
        assert code.count(old)==1;code=code.replace(old,new)
    return code.replace('PG743-closing-selected-v1','PG1008-stream-selected-v2').replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','40ef6e894573d2ffab1d1732124960f9c98d5f97')

if __name__=='__main__':
    env=dict(selected.__dict__);exec(compile(source(),'<PG1008 fully pinned selected reactor>','exec'),env);env['main']()
