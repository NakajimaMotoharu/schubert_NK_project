"""Independent frozen API/Web42 source responsibility table, no target or network execution."""
from pathlib import Path
import explicit_primary_source_post as post

def other_module(path):
    for current,other in (('schubert-nk-api','schubert-nk-web'),('schubert-nk-web','schubert-nk-api')):
        prefix='src/'+current+'/src/test/java/'
        if path.startswith(prefix):return 'src/'+other+'/src/test/java/'+path[len(prefix):]
    raise ValueError('explicit API or Web module required')

if __name__=='__main__':
    assert other_module('src/schubert-nk-api/src/test/java/p/Foo.java')=='src/schubert-nk-web/src/test/java/p/Foo.java'
    assert other_module('src/schubert-nk-web/src/test/java/p/Foo.java')=='src/schubert-nk-api/src/test/java/p/Foo.java'
    post.run(Path(__file__),post.BASE/'PG9520-api-web42-source-post-v1','PG9518-api-web42-source-metadata-v1',
      '61ef8d45de754b88b2f9dfe9fb2f81ef14f539eba830910a605dd81f85d8b295','c28c55fc121ce2bf76cc2fafd1392a42a4b11a8a9b44be2a81dc55db0c64474a',
      'evidence/01_PT/018_NK-OPS-001/1930_G13ApiWeb42_主関連責任仕様.md','2cbdbc1ab1e051dfa4a5aeacb1d314c2f710f782b3e811c6a332e00777ba7e27',
      'src/',('schubert-nk-api/','schubert-nk-web/'),42,
      {'UserMutationApplicationService':'WBS-P010-02','LogRequest':'WBS-P018-09','MediaRequest':'WBS-P009-01','FixedPayload':'WBS-P001-03',
       'MediaApplicationService':'WBS-P009-01','QuestionWorkerService':'WBS-P012-03','QuestionQueryRepository':'WBS-P014-01',
       'QuestionSubmissionService':'WBS-P011-02','MessageStageGuard':'WBS-P006-01','ScenarioRequest':'WBS-P008-01',
       'ApiStartupInputs':'WBS-P018-05','ApiManagementServer':'WBS-P018-05','ApiBrokerContexts':'WBS-P005-03','InspectorApplication':'WBS-P004-04',
       'OwnedTransferDirectory':'WBS-P003-04','InboxCleanup':'WBS-P004-02','AuthenticationInboxInspector':'WBS-P004-04',
       'InspectionProgress':'WBS-P004-04','InspectorDatabaseConnections':'WBS-P004-04','ResultBoundResponseSnapshotCodec':'WBS-P006-01',
       'JmsMessageGuard':'WBS-P005-03','AuthenticationService':'WBS-P007-01','ArtemisConnectionFactoryProvider':'WBS-P005-04',
       'AuthorizationException':'WBS-P007-03','ApiApplicationPreparation':'WBS-P018-05','ScenarioFileWriter':'WBS-P008-03',
       'WebLogDispatcher':'WBS-P006-04','WebRequestLogProducer':'WBS-P006-03','WebLogIngestService':'WBS-P006-05',
       'JmsRequestReplyException':'WBS-P005-02','JmsRequestReplyClient':'WBS-P005-02','WebBrokerContexts':'WBS-P005-02'},
      source_path_mutator=other_module,source_mutator_vectors=2)
