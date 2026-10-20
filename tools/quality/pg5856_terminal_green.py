"""Finite70 same-source terminal PG/PT, unchanged prior66 plus four independent contracts."""
import pg5828_isolation_green as previous

CASES={**previous.CASES,'api':previous.CASES['api']|{'api.messaging.inbound.CommittedTerminalAdmissionContractTest'},'web':previous.CASES['web']|{'web.messaging.ReplyCommittedTerminalAdmissionContractTest'}}
COUNTS={**previous.COUNTS,'CommittedTerminalAdmissionContractTest':3,'ReplyCommittedTerminalAdmissionContractTest':1}
TARGETS=previous.TARGETS


def runner_source():
    raw=previous.runner_source()
    for old,new in(('sum(map(len,expected.values()))!=66 or len(expected)!=18','sum(map(len,expected.values()))!=70 or len(expected)!=20'),("'expectedTests':66","'expectedTests':70"),("executionKind='NORMAL_FATAL_ISOLATION_SELECTED66'","executionKind='NORMAL_COMMITTED_TERMINAL_SELECTED70'")):
        if raw.count(old)!=1:raise ValueError('one exact terminal70 predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<finite70 terminal PGPT>','exec');return raw


def main():
    scope={**vars(previous.previous.engine),'SLOT':'pg5856-terminal-selected70-v1','CASES':CASES,'COUNTS':COUNTS,'TARGETS':TARGETS,'test_names':previous.previous.source_test_names}
    exec(compile(runner_source(),'<finite70 terminal PGPT>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
