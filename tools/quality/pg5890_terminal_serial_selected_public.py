"""Read original83 XML/all1666 bytes/six independent terminal design identities; no PT."""
import inspect
import pg5866_terminal_selected_public as previous
from pg5886_terminal_serial_whole import SOURCE,ROOT,W
from pg5880_terminal_serial_green import CASES,COUNTS,TARGETS

API='dev.codex.schubert.nk.api.messaging.inbound.CommittedTerminalAdmissionContractTest'
WEB='dev.codex.schubert.nk.web.messaging.ReplyCommittedTerminalAdmissionContractTest'
TERMINAL_CASES={(API,n)for n in('term001SyncCommitStopsAllFourContextAdmissions','term002QuestionCommitStopsFurtherAdmissions','term003WebLogCommitStopsFurtherAdmissions','term005SyncTwoInFlightCommittedCallbacksSignalOnce','term006SyncTwoInFlightIsolationFailuresSignalOnce')}|{(WEB,'term004ReplyCommitStopsFurtherAdmissions')}


def reader_source():
    raw=inspect.getsource(previous.main)
    changes={'pg5856-terminal-selected81-v3':'pg5880-terminal-serial83-v1','PG5858-terminal-static-v1':'PG5882-terminal-serial-static-v1','pg5858-terminal-static-v1':'pg5882-terminal-serial-static-v1','sum(map(len,actual.values()))==81':'sum(map(len,actual.values()))==83','range(1,5)':'range(1,7)',"'tests':81,'suites':22":"'tests':83,'suites':22",'PG5866-terminal81-v1':'PG5890-terminal83-v1',"'tests':81,'newDesignIdsTraced':4":"'tests':83,'newDesignIdsTraced':6"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact six-terminal current83 binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<original83 independent XML projection>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'ROOT':ROOT,'W':W,'CASES':CASES,'COUNTS':COUNTS,'TARGETS':TARGETS,'added_cases':lambda:sorted(TERMINAL_CASES)}
    exec(compile(reader_source(),'<original83 independent XML projection>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
