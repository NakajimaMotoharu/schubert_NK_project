"""Independent document-defined API transaction/JMS20 source primary/related post."""
from pathlib import Path
import explicit_primary_source_post as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9436-api-jms20-source-post-v1','PG9434-api-jms20-source-metadata-v1',
      '829cfcd34370eb408c3097295a410a528e5f390d6a052f8892ac1ba908831d61','c40aab42f6b468d167ff847e39aa6ad142bbc66a0eda650eaa9cbb6701a8b76c',
      'evidence/01_PT/018_NK-OPS-001/1916_G13ApiJms20_主関連責任仕様.md','453fdff2da6dc87d10221f41d5fe5f759453bd8949e4285a112fbdf7d70660fb',
      'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/',('dispatch/','messaging/'),20,
      {'JdbcSyncRequestProcessor':'WBS-P004-05','ApiBrokerContexts':'WBS-P005-03','SyncRequestListener':'WBS-P005-03',
       'InboundTransactions':'WBS-P005-03','InternalEventProcessor':'WBS-P005-03','ReplySender':'WBS-P005-03','DlqSender':'WBS-P005-03'})
