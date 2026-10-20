"""Finite54 same-source rollback PG/PT, including owned in-process broker fixtures only."""
import inspect
import re
import pg5732_enum48_selected as engine

CASES={**engine.CASES,
 'protocol':{'protocol.codec.PayloadGoldenVectorTest','protocol.transport.UnconfirmedJmsRollbackExceptionTest'},
 'api':{'api.messaging.inbound.ConsumerRollbackUnconfirmedContractTest','api.messaging.inbound.InboundTransactionsPrimaryContractTest','api.messaging.inbound.SyncRequestListenerTest','api.messaging.inbound.ApiConsumerTerminalRemainderTest'},
 'web':{'web.messaging.ReplyRollbackUnconfirmedContractTest','web.messaging.ReplyRollbackSignalContractTest','web.messaging.ReplyIsolationPrimaryContractTest','web.messaging.ArtemisReplyConsumerTest','web.messaging.ArtemisReplyConsumersTest'}}
COUNTS={
 'PayloadGoldenVectorTest':3,'UnconfirmedJmsRollbackExceptionTest':4,
 'ConsumerRollbackUnconfirmedContractTest':6,'InboundTransactionsPrimaryContractTest':5,
 'SyncRequestListenerTest':7,'ApiConsumerTerminalRemainderTest':3,
 'ReplyRollbackUnconfirmedContractTest':1,'ReplyRollbackSignalContractTest':5,
 'ReplyIsolationPrimaryContractTest':2,'ArtemisReplyConsumerTest':7,'ArtemisReplyConsumersTest':7,
 'EnumValueCatalogCompatibilityTest':1}
TARGETS={
 'protocol':['protocol/transport/UnconfirmedJmsRollbackException'],
 'api':['api/messaging/inbound/'+s for s in('InboundTransactions','SyncRequestConsumers','QuestionWorkConsumers','WebLogConsumers')],
 'web':['web/messaging/ArtemisReplyConsumer','web/messaging/ArtemisReplyConsumers']}


def source_test_names(path):
    raw=path.read_text()
    if any(s in raw for s in('@Disabled','@ParameterizedTest','@RepeatedTest','@TestFactory')):raise ValueError('one ordinary executed Test only, no parameterized/skip aliases')
    names=re.findall(r'@Test\s+(?:@[A-Za-z0-9_.]+(?:\([^)]*\))?\s+)*(?:public\s+)?void\s+(\w+)\s*\([^{}]*\)',raw)
    if len(names)!=len(re.findall(r'@Test\b',raw))or len(set(names))!=len(names):raise ValueError('unique one-to-one Test source names, including TempDir injection')
    return set(names)


def runner_source():
    raw=inspect.getsource(engine.main)
    changes={
      "count=3 if module=='protocol'else 4 if module=='web'else 1":"count=COUNTS[cls.rsplit('.',1)[1]]",
      'sum(map(len,expected.values()))!=12 or len(expected)!=7':'sum(map(len,expected.values()))!=54 or len(expected)!=15',
      "'expectedTests':12":"'expectedTests':54",
      "method=case.get('name','').removesuffix('()')":"method=case.get('name','').split('(',1)[0]",
      'len(physical)==1664':'len(physical)==1665',
      'len(target_counters)==14':'len(target_counters)==7',
      '    done=done and target100':'    # Report actual target counters; program/full/native completion is a later requirement.',
      "with(out/'manifest.safe.json').open('x')as f:":"value.update(executionKind='NORMAL_ROLLBACK_SELECTED54',xmlNamesNormalizedOnlyForOrdinaryTempDirMethods=True,noExternalRuntimeOperation=True,targetFour100RequiredForCompletion=True)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact finite54 runner predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<finite54 current rollback PT>','exec')
    return raw


def main():
    namespace={**vars(engine),'SLOT':'pg5800-rollback-selected54-v2','CASES':CASES,'COUNTS':COUNTS,'TARGETS':TARGETS,'test_names':source_test_names}
    exec(compile(runner_source(),'<finite54 current rollback PT>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
