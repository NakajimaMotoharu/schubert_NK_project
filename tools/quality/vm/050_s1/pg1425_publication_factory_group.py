from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_BACKUP_PUBLICATION_FACTORY_BOUNDARY','GROUP_START',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-P017-06'],'run':'PG1426-next','workCategory':'SELECTED_TEST',
        'estimateAtGroupStartPp':{'low':.03,'base':.08,'high':.2},'remainingEstimatePp':{'low':.03,'base':.08,'high':.2},
        'quotaBefore':{'usedPercent':33,'remainingPercent':67,'resetsAt':1792229056,'windowDurationMins':10080},
        'estimateChangeReason':'Factory rejects API/Web/Cleanup/Expiry Root snapshots and null explicit resume proof before native namespace access. No fake valid Root or normal native invocation for coverage. Small temp fixture only, live805MB guard first.',
        'unaccepted':['selected7/static/counter','normal resume native and whole owner'],
        'nextCommand':'Format-only -> qualify generated selected7 ->clean fixed source/live capacity ->actual selected7 ->samebyte latest input counter'}))
