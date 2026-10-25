"""Nineteen individually reviewed storage companion tests, never a package or suffix rule."""
import trace_owner_join_explicit_main_gaps as previous

PREFIX='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/'
DECISIONS={
  'LinuxHostDirectoryCallsTest':'WBS-P003-04','ExistingFileAccessTest':'WBS-P003-04',
  'LinuxDirectoryCallsTest':'WBS-P003-04','OwnedTransferDirectoryTest':'WBS-P003-04',
  'StorageRootInspectionTest':'WBS-P003-05','StorageRootLayoutTest':'WBS-P003-05',
  'LinuxInodeSecurityTest':'WBS-P003-05','StorageAttributeGuardTest':'WBS-P003-05',
  'LinuxExecDescriptorsTest':'WBS-P003-06','LinuxFileLockTest':'WBS-P003-06',
  'LinuxStartupAdmissionTest':'WBS-P003-06','LinuxProcessExecTest':'WBS-P003-06','LinuxSealedProofTest':'WBS-P003-06',
  'ServiceCredentialIdTest':'WBS-P003-07','ServiceCredentialLocationTest':'WBS-P003-07','ServiceConfigFilesTest':'WBS-P003-07',
  'LinuxMonotonicClockTest':'WBS-P003-08','ResourceScopeTest':'WBS-P003-08',
  'LinuxFilesystemClassifierTest':'WBS-P018-03'}

def canonical(path,logical):
    name=path.removeprefix(PREFIX).removesuffix('.java')
    if path==PREFIX+name+'.java' and name in DECISIONS and path not in logical:
        owner=DECISIONS[name]
        return dict(canonicalOwner=owner,canonicalCostOwner=owner,
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='STORAGE_EXACT_COMPANION_TEST_TO_ORIGINAL_485_MAIN_RESPONSIBILITY')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical); row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):
        raise ValueError('exact individually reviewed storage Test mapping required')
