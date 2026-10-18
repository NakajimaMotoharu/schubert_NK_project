import pg5304_permit_intent_selected as entry
import pg5281_factory_finish as finish
import pg5300_handoff_public as ids


def revalidated_case_ids():
    overrides=ids.revalidated_case_ids()
    for number in range(1,11):
        overrides[('dev.codex.schubert.nk.batch.file.BackupStartIntentFilesTest',
            f'concurrentDistinctOwnersCannotPublishTwoIntents()[{number}]')]={
                'testId':f'PT-OPS-ISS006-R{number:02d}','newIndependentCase':False,'newInThisChange':False}
    return overrides


if __name__=='__main__':
    raise SystemExit(finish.publish_current(entry=entry,run_name='pg5304-permit-intent-green-v1',
        proof_name='PG5306-permit-intent-bytecode-v1',counts=(1038,126),
        spec='1085_Permit・Intent完全owner連鎖_PT仕様.md',
        proof_key='permitIntentBytecodeProofSha256',independent_cases=60,case_overrides=revalidated_case_ids(),
        qualification_path=entry.selected.ROOT.parent/'pgpt-runs/PG379/pg5304-permit-intent-green-v1/qualification.safe.json',
        case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':4,'internalAssemblyHandoffs':3,'extraDirectoryOwnerFactories':2,
               'protectedAcquisitionBoundaries':9,'physicalDirectoryFactorySites':3,
               'logicalTestMethods':1029,'repeatedLogicalMethods':1,'repeatedInvocations':10,
               'originalRunnerActualExit':1,'bugs':['BUG1414','BUG1438'],'ykt':['YKT1178','YKT1202']}))
