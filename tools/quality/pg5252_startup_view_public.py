"""Current829/98 and eight independent ViewOwner cases, failed673 never imported."""
import json
import pg5122_root_elf_public as public
import pg5180_backup_public as common
import pg5204_morning_owner_public as morning
import pg5248_startup_view_selected as entry

selected=entry.selected
NAMES=('viewfd001PrimitiveHighDescriptorsCloseInReverseExactlyOnce',
    'viewfd002CapacityClosedNullAndParentRefuseBeforeNativeOpen',
    'viewfd003NegativeAndDuplicateNeverCreateAnExtraOwnershipSlot',
    'viewfd004AllNativeOpenFailureKindsRetainOnlyPriorOwnedDescriptors',
    'viewfd005All64ReverseCloseStatesMatchFixedIndependentGolden',
    'viewfd006ExistingSuppressedAndRepeatedThrowableStaySanitized',
    'viewfd007BodyAndOwnerCloseKeepExistingIndependentPriority',
    'viewfd008IndependentParallelOwnersNeverShareSlotsOrConsumeEachOther')


def revalidated_case_ids(*,view_new=False):
    overrides=common.revalidated_case_ids()
    overrides.update({('dev.codex.schubert.nk.batch.file.MorningBackupRequestPublicationTest',name):
        {'testId':'PT-OPS-MBPUB'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':False}
        for i,name in enumerate(morning.NAMES,7)})
    overrides.update({('dev.codex.schubert.nk.batch.file.StartupAdmissionViewOwnerTest',name):
        {'testId':'PT-OPS-VIEWFD-'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':view_new}
        for i,name in enumerate(NAMES,1)})
    return overrides


def main():
    run=public.W/'pg5248-startup-view-owner-green-v1';result=json.loads((run/'manifest.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5250-startup-view-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('same-source actual primitive/typed-catch/drain and Owner four100 first')
    entry.configure();overrides=revalidated_case_ids(view_new=True)
    diagnostic=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5247-view-runtime-diagnostic-v1/manifest.json'
    return public.main(factory_run_name=run.name,measurement_module=selected,required_counts=(829,98,54),
        case_overrides=overrides,extra_suites=entry.extra_suites(),
        case_name_aliases=entry.previous.previous.previous.aliases.invocation_aliases(),
        extra_fields={'newIndependentCases':8,'priorIndependentCasesRevalidated':46,'newJavaCasesInThisGroup':8,
        'newJavaCasesInCorrection':0,'spec':'1073_StartupViewOwner_primitive登録・全逆順drain_PT仕様.md',
        'ssc':['SSC308'],'bugs':['BUG1414','BUG1432'],'ykt':['YKT1178','YKT1196'],
        'startupViewBytecodeProofSha256':selected.sha(path),'storageFourCounters':result['storageFourCounters'],
        'ownerFourCounters':proof['ownerFourCounters'],'semanticClasses':2,
        'nestedMethodEquivalent':proof['nestedMethodEquivalent'],
        'otherPhysicalClassesUnchanged':proof['otherPhysicalClassesUnchanged'],
        'typedNativeCatchPrimaryPreserved':True,'secondaryPrimitiveBitmap':True,'noSyntheticThrowEscape':True,
        'originalFailedSource673DiagnosticSha256':selected.sha(diagnostic),'failedSource673Imported':False,
        'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
