import datetime,json,sys
from pathlib import Path
wbs=sys.argv[1]; q=json.loads(sys.argv[2]); reservation=json.loads(Path('deputy-reports/web-display-20261011/reservation.confirmed.json').read_text())
paths=[x['path'] for x in reservation['files'] if x['owner']=='WBS-'+wbs]
r={'wbs':'WBS-'+wbs,'baseCommit':reservation['safeExistingCommit'],'beginJST':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'readOnlyAllowlist':paths,'productionChangesPermittedThisUnit':[],'testExecutionPermittedThisUnit':[],'authority':['UI223/224/225 corresponding screen; SS313; reservation exact owner paths'],'quotaBefore':q['primary']|{'limitId':q['limitId'],'acquisitionUTC':q['acquisitionUTC']},'groupStartEstimateE':17.25}
Path('deputy-reports/web-display-20261011/'+wbs+'-read-allowlist.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
for p in paths:
 print('\nFILE '+p+'\n'+Path(p).read_text())
