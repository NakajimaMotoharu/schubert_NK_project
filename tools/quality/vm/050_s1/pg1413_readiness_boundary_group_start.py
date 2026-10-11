"""Limited public readiness byte/type contracts, not repeated full-leaf budgets."""
from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_READINESS_RAW_BYTE_ROLE_TYPE','GROUP_START',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-P018-07','WBS-P017-10'],
        'run':'PG1413-next','workCategory':'SELECTED_TEST','estimateAtGroupStartPp':{'low':.05,'base':.15,'high':.35},'remainingEstimatePp':{'low':.05,'base':.15,'high':.35},
        'estimateChangeReason':'Two new public contract cases only: raw high-bit proc status (String ASCII replacement did not cover it) and role array with correct count but non-object members. Owner/inventory/SS341/SS321 join checked. Reuse qualified same Main dependencies, format-first, strict selected/static and latest-only inputs; no VM/whole6/parent fee repetition.',
        'quotaBefore':{'usedPercent':32,'remainingPercent':68,'resetsAt':1792229056,'windowDurationMins':10080},
        'unaccepted':['actual selected tests/static/Main byte/counter','remaining owner classes/native/fault/wholeleaf'],
        'nextCommand':'Add raw-byte Fixture and correctly sized malformed role arrays ->format-only ->fixed selected Maven with unchanged dependency reuse -> latest-only counter'}))
