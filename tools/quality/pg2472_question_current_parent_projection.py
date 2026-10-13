"""BUG1240: actual full payload Source and signed BOM, not transport-only binding."""
import inspect
import pg2457_question_current_parent_projection as prior
from pg2446_question_current_observer import SOURCE,BOM

SLOT='pg2472-question-current-parent-projection-v1'
ROOT_FIELDS=frozenset('ActiveState,ControlPID,ExecMainCode,ExecMainExitTimestampMonotonic,ExecMainStartTimestampMonotonic,ExecMainStatus,Id,InvocationID,Job,KillMode,LoadState,MainPID,RemainAfterExit,Restart,Result,SendSIGKILL,SubState,Type'.split(','))


def payload(sha):
    raw=prior.payload(sha)
    old="SOURCE='3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'"
    if raw.count(old)!=1:raise ValueError('one immutable historical source role required')
    raw=raw.replace(old,'SOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM))
    marker="assert len(fields)==18 and before['source']==SOURCE"
    if raw.count(marker)!=1:raise ValueError('one whole actual parent tuple boundary required')
    return raw.replace(marker,marker+" and before['manifestSha256']==BOM\nassert type(fields)is dict and set(fields)==set("+repr(sorted(ROOT_FIELDS))+") and all(type(v)is str for v in fields.values())\nassert fields['Id']=='schubert-nk-morning-controller.service'")


def main():
    raw=inspect.getsource(prior.prior.previous.prior.prior.main).replace('pg2081-current-newrun-full-live-seal-v1','pg2456-question-current-full-seal-v1')
    ns={**prior.prior.previous.prior.prior.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new actual parent Source/BOM reader>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
