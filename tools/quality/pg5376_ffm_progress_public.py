import json
import pg5372_ffm_progress_selected as entry
import pg5368_ffm_outputs_public as previous
import pg5281_factory_finish as finish
from pg5374_ffm_progress_bytecode import RUN,OUT

NAME='ffmown008PositiveAuthenticationProgressUsesNoWaitAndNeverRenewsBudget'


def revalidated_case_ids(owner_new=False):
    values=previous.revalidated_case_ids(owner_new=owner_new)
    values[('dev.codex.schubert.nk.bootstrap.LinuxSystemdSessionTest',NAME)]={
        'testId':'PT-OPS-FFMOWN008','newIndependentCase':True,'newInThisChange':owner_new}
    return values


if __name__=='__main__':
    result=json.loads((finish.public.W/RUN/'manifest.safe.json').read_bytes())
    raise SystemExit(finish.publish_current(entry=entry,run_name=RUN,proof_name=OUT,counts=(1100,132),
        spec='1096_FFM返却先行所有・UNKNOWN保持_PT仕様.md',proof_key='ffmOutputsBytecodeProofSha256',
        independent_cases=88,case_overrides=revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':4,'newIndependentCases':8,'priorIndependentCasesRevalidated':80,
            'newJavaCasesInThisGroup':8,'logicalTestMethods':1091,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'fixtureDatabase':result['fixtureDatabase'],'additionalBoundariesOutsideOriginal':2,
            'implementationDecision':'PG-D429'}))
