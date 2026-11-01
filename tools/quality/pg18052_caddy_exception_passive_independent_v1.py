"""Independent one-source passive supplement identity, natural branch and no-progress proof."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg18050_caddy_exception_passive_post_v1 as measured
OUT=data.BASE/'PG18052-caddy-exception-passive-independent-v1'
PIN='44dd5ce1b6c9d4f6eac7ab5044ee9fdff10ea292f825723625a48e3f457f6b30'
def require(v,label):
    if not v:raise ValueError(label)
def contract(v):
    require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==measured.SOURCE,'current successful source')
    require(v['originalRawReference']==list(measured.RAW) and v['originalPostReference']==list(measured.POST) and v['originalIndependentReference']==list(measured.INDEPENDENT),'original exact lineage')
    require(v['sourceInputSha256']==measured.PIN and set(v['physicalClasses'])=={measured.NAME} and set(v['sourcePhysicalInventory'])=={measured.NAME},'whole Source and same-count physical identity')
    require(v['fullSourceUnits']=={measured.NAME:dict(physical=[measured.NAME],totals=dict(LINE=dict(missed=0,covered=2),METHOD=dict(missed=0,covered=1),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=0)),four100=False,metadataOnly=False,branchNaturallyZero=True,threeCounter100=True)},'independent literal constructor denominator')
    require(v['singleSession'] is True and v['crcMismatch']==0 and v['allMeasuredApplicableCountersCovered'] is True and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1,'natural zero not strict four')
    require(all(v[k]==0 and type(v[k]) is int for k in ['productTestsExecuted','productTestsReexecuted','newTestIds','newJunitExecutions','newOrdinaryMethods','newQualityMethods','newProductionFiles','actualVmActions','actualDatabaseActions','actualNetworkActions','forbiddenProductProbeHits','newAccepted']),'no replay/count inflation/effects')
    require(v['priorSourceTransferred'] is v['coverageExecUnion'] is v['productClassesLoaded'] is v['productMethodsInvoked'] is v['formalUpdated'] is v['whole451Accepted'] is False and v['effortPercent'] is None and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is v['originalHeldNativeAuditUnchanged'] is True,'no exclusions/transfer/hidden Product')
    require(v['owners'][measured.PATH]['canonicalOwner']==v['owners'][measured.PATH]['canonicalCostOwner']=='WBS-P015-02','canonical not group owner')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    p=data.read_checked(measured.OUT/'manifest.json',PIN);contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalRawReference',[]),('sourceInputSha256','0'*64),('physicalClasses',{'unknown':'0'*64}),('fullSourceUnits',{}),('singleSession',False),('crcMismatch',1),('targetUnitFour100',True),('strictFour100GateExit',0),('newTestIds',6),('newJunitExecutions',1),('productTestsReexecuted',6),('newProductionFiles',1),('coverageExecUnion',True),('productClassesLoaded',True),('forbiddenProductProbeHits',1),('actualDatabaseActions',1),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('invalid passive supplement accepted '+key)
    raw=measured.read(measured.RAW);old=measured.read(measured.POST);qualified=measured.read(measured.INDEPENDENT)
    require(p['execSha256']==raw['execSha256']==old['execSha256'] and p['sessionIdentity']==old['sessionIdentity'],'same original exec/session')
    require(p['xmlHashes']==old['xmlHashes'] and old['cases']==raw['cases'] and qualified['postSha256']==measured.POST[1],'no copied unrelated tests')
    require(p['passiveCoverageStage']['actualExit']==0 and p['passiveCoverageStage']['timedOut'] is False,'true passive terminal')
    for v in [p,old,qualified]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=measured.SOURCE,invocation=invocation,postSha256=PIN,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=1,productTestsExecuted=0,newTestIds=0,newJunitExecutions=0,newMeasuredExistingProductionSources=1,newStrictFour100Sources=0,newNaturalBranchZeroSources=1,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
