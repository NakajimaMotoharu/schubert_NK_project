"""1916 exact API transaction/JMS20 source labels; no provider, DB, native or test execution."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PREFIX='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/'
TRANSACTION=[
 'dispatch/JdbcRollbackAttachment330Test.java','dispatch/JdbcTransactionBoundary329Test.java','dispatch/JdbcTransactionFatal329Test.java']
JMS=[
 'messaging/config/ApiBrokerFactoryRemainderTest.java','messaging/config/ApiFactoryNativeRetentionTest.java',
 'messaging/config/ArtemisTransportContractTest.java','messaging/config/BrokerGraph334Test.java',
 'messaging/inbound/ApiConsumerCloseOwnershipTest.java','messaging/inbound/ApiConsumerRemainderTest.java',
 'messaging/inbound/ApiConsumerTerminalRemainderTest.java','messaging/inbound/ApiNativeRetentionTest.java',
 'messaging/inbound/CommittedTerminalAdmissionContractTest.java','messaging/inbound/ConfirmedRollbackCallbackTest.java',
 'messaging/inbound/ConsumerCleanup333Test.java','messaging/inbound/ConsumerGraph332Test.java',
 'messaging/inbound/ConsumerRollbackUnconfirmedContractTest.java','messaging/inbound/FatalIsolationConsumersContractTest.java',
 'messaging/inbound/InboundTransactionsPrimaryContractTest.java','messaging/inbound/InternalEventListenerTest.java',
 'messaging/outbound/OutboundJmsAdapterTest.java']
PRIMARY={**{PREFIX+name:'WBS-P004-05' for name in TRANSACTION},**{PREFIX+name:'WBS-P005-03' for name in JMS}}

if __name__=='__main__':
    assert len(TRANSACTION)==3 and len(JMS)==17 and len(PRIMARY)==20
    metadata.run(Path(__file__),metadata.BASE/'PG9434-api-jms20-source-metadata-v1',metadata.ROOT.parent/'pgpt-runs/PG379/pg9434-api-jms20-source-metadata-v1',
      PRIMARY,'PG9426-resource33-source-join-v1/manifest.json','91f349d3158c28d4b6da2bfddf9c2ca1b9469de764ebb2d87cb4c7d137f21690',False)
