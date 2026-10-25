"""Canonical planning ownership is independent of the engineering group that changed a source.

No source execution, cost allocation, PT qualification or baseline mutation is performed here.
Unknown paths remain unknown. New C07 logical entries require their explicit rule/evidence basis.
"""
import copy
from pathlib import PurePosixPath
import re

def require(value,message):
    if not value: raise ValueError(message)

def proposed_owner(path):
    parts=PurePosixPath(path)
    require(not parts.is_absolute() and '..' not in parts.parts and path.startswith('src/'),'bounded source namespace')
    if '.private.' in parts.name: return None
    if path=='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetimeTest.java':
        return ('WBS-P018-05','P01805_RD171_UI252_SS342_LIFETIME_STOP_BUDGET_TEST')
    if path in ('src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java',
                'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudgetTest.java'):
        return ('WBS-P018-05','P01805_RD171_UI252_SS342_FIRST_API_STOP_NOTIFICATION_BUDGET')
    if path.startswith('src/deployment/monitoring/'):
        return ('WBS-C07','C07_SS351_MONITORING_CONFIGURATION')
    if re.fullmatch(r'src/schubert-nk-(api|web|batch)/src/(main|test)/java/dev/codex/schubert/nk/\1/monitoring/(?:[A-Za-z_][A-Za-z0-9_]*/)*[^/]+\.java',path):
        return ('WBS-P018-09','P01809_RD171_UI252_SS351_MONITORING_CODE_AND_PT')
    if path in ('src/schubert-nk-batch/src/test/resources/monitoring/metric-catalog.tsv','src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'):
        return ('WBS-P018-09','P01809_SS312351_INDEPENDENT_METRIC_AND_ROUTE_FIXTURES')
    if re.fullmatch(r'src/schubert-nk-(api|web|batch|bootstrap)/pom\.xml',path):
        return ('WBS-F02','F02_MODULE_BUILD_DEPENDENCY_INPUT')
    if path=='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java':
        return ('WBS-C06','C06_1556_1557_PUBLIC_CONFIGURATION_TEST_OWNER')
    if path=='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.java':
        return ('WBS-C02','C02_1553_1555_SUPPLEMENTARY_UNIT_TEST_OWNER')
    return None

def canonical(path,logical):
    # A baseline entry always wins, including if its package happens to match a new-entry rule.
    if path in logical:
        row=logical[path]
        require(row['path']==path and row['owner'] and row['costOwner'],'explicit baseline owner pair')
        return dict(canonicalOwner=row['owner'],canonicalCostOwner=row['costOwner'],ownershipStatus='BASELINE_LOGICAL_REFERENCE',basis='485_ORIGINAL_LOGICAL_OWNER_ONLY_NOT_OLD_PT_OR_BYTES')
    proposed=proposed_owner(path)
    if proposed is None:
        return dict(canonicalOwner=None,canonicalCostOwner=None,ownershipStatus='UNKNOWN',basis='NO_BASELINE_OR_APPROVED_INTERNAL_RULE; DO_NOT_INFER_FROM_CHANGE_OWNER')
    owner,basis=proposed
    return dict(canonicalOwner=owner,canonicalCostOwner=owner,ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis=basis)

def join_rows(rows,logical,source_hashes,change_owner):
    require(isinstance(change_owner,str) and change_owner.startswith('WBS-'),'explicit change owner, not inferred canonical assignment')
    require(len(rows)==len({row['path'] for row in rows}),'unique source rows')
    result=[]
    for row in rows:
        path=row['path']
        require(row['sha256']==source_hashes[path],'actual current source byte identity')
        resolved=canonical(path,logical)
        result.append(dict(path=path,sha256=row['sha256'],owner=resolved['canonicalOwner'],**resolved,changeOwner=change_owner,legacyReportedOwner=row.get('owner'),legacyTraceOwnerMeaning='ENGINEERING_CHANGE_GROUP_NOT_CANONICAL_ARTIFACT_OWNER',additionalSharedCostPp=0,actualAllocatedPp=None,historicalCostsReallocated=False,historicalRunReassigned=False,currentSourcePtQualificationInferred=False))
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    expected=join_rows(original,logical,source_hashes,change_owner)
    require(len(rows)==len(expected),'no missing ownership row')
    require(rows==expected,'canonical owner/change owner/byte/cost semantics must match independent logical source')
    require(len(rows)==len({row['path'] for row in rows}),'no duplicate owner assignment')
    return copy.deepcopy(rows)
