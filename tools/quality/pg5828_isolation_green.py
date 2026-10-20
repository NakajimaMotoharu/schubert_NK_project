"""Finite66 after SS322 isolation-phase correction; normal PT, no operational entry point."""
import pg5800_rollback_green as previous

CASES={**previous.CASES,
 'protocol':previous.CASES['protocol']|{'protocol.transport.FailedJmsIsolationExceptionTest'},
 'api':previous.CASES['api']|{'api.messaging.inbound.FatalIsolationConsumersContractTest'},
 'web':previous.CASES['web']|{'web.messaging.ReplyFatalIsolationContractTest'}}
COUNTS={**previous.COUNTS,'FailedJmsIsolationExceptionTest':4,'FatalIsolationConsumersContractTest':6,'ReplyFatalIsolationContractTest':2}
TARGETS={**previous.TARGETS,'protocol':previous.TARGETS['protocol']+['protocol/transport/FailedJmsIsolationException']}


def runner_source():
    raw=previous.runner_source()
    changes={
      'sum(map(len,expected.values()))!=54 or len(expected)!=15':'sum(map(len,expected.values()))!=66 or len(expected)!=18',
      "'expectedTests':54":"'expectedTests':66",
      'len(physical)==1665':'len(physical)==1666',
      'len(target_counters)==7':'len(target_counters)==8',
      "executionKind='NORMAL_ROLLBACK_SELECTED54'":"executionKind='NORMAL_FATAL_ISOLATION_SELECTED66'"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact finite66 predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<finite66 isolation>','exec');return raw


def main():
    scope={**vars(previous.engine),'SLOT':'pg5828-isolation-selected66-v1','CASES':CASES,'COUNTS':COUNTS,'TARGETS':TARGETS,'test_names':previous.source_test_names}
    exec(compile(runner_source(),'<finite66 isolation>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
