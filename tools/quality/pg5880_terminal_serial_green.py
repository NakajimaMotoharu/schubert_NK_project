"""Finite83: dedicated serialized receivers and legal two-context Sync concurrency."""
import pg5856_terminal_green as previous

CASES=previous.CASES
COUNTS={**previous.COUNTS,'CommittedTerminalAdmissionContractTest':5}
TARGETS=previous.TARGETS


def runner_source():
    raw=previous.runner_source()
    for old,new in(('sum(map(len,expected.values()))!=81 or len(expected)!=22','sum(map(len,expected.values()))!=83 or len(expected)!=22'),("'expectedTests':81","'expectedTests':83"),("executionKind='NORMAL_COMMITTED_TERMINAL_SELECTED81'","executionKind='NORMAL_SERIAL_AND_LEGAL_SYNC_SELECTED83'")):
        if raw.count(old)!=1:raise ValueError('one exact serial83 inventory predicate')
        raw=raw.replace(old,new,1)
    compile(raw,'<serial and legal two-context83>','exec');return raw


def main():
    scope={**vars(previous.previous.previous.engine),'SLOT':'pg5880-terminal-serial83-v1','CASES':CASES,'COUNTS':COUNTS,'TARGETS':TARGETS,'test_names':previous.previous.previous.source_test_names}
    exec(compile(runner_source(),'<serial and legal two-context83>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
