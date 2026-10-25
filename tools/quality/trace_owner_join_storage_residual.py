"""Ten reviewed storage composite/helper responsibilities, not wildcard or PT qualification."""
import trace_owner_join_storage_companion as previous

PREFIX='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/'
DECISIONS={
  'LinuxStartupFileLockTest':('LinuxFileLock','WBS-P003-06','TEST'),
  'PrivateDirectoryEntryTest':('OwnedTransferDirectory','WBS-P003-04','TEST'),
  'ChildDirectoryPublicationTest':('OwnedTransferDirectory','WBS-P003-04','TEST'),
  'LinuxProcessExecChild':('LinuxProcessExec','WBS-P003-06','TEST_HELPER'),
  'OwnedDirectoryFactoryTest':('OwnedTransferDirectory','WBS-P003-04','TEST'),
  'PrivateChildDirectoryTest':('OwnedTransferDirectory','WBS-P003-04','TEST'),
  'EnumValueCatalogCompatibilityTest':('ServiceCredentialId','WBS-P003-07','TEST'),
  'FactoryResourceScopeTest':('ResourceScope','WBS-P003-08','TEST'),
  'ExceptionValueContractTest':('StorageIoException','WBS-P003-04','TEST'),
  'LinuxExecDescriptorsChild':('LinuxExecDescriptors','WBS-P003-06','TEST_HELPER')}

def canonical(path,logical):
    name=path.removeprefix(PREFIX).removesuffix('.java')
    if path==PREFIX+name+'.java' and name in DECISIONS and path not in logical:
        owner=DECISIONS[name][1]
        return dict(canonicalOwner=owner,canonicalCostOwner=owner,
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='STORAGE_EXACT_REVIEWED_COMPOSITE_OR_HELPER_SINGLE_PRIMARY_MAIN_RESPONSIBILITY')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):
        raise ValueError('reviewed exact storage residual mapping required')
