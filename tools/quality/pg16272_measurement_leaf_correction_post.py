"""Bounded public event correction proof; no history rewrite, cost allocation, or Product execution."""
import copy
import json
from collections import deque
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG16272-measurement-leaf-correction-post-v1'
ORIGINALS=[('PGPT-20261008-3453','5ac11580afa39e991bfdb53a90cbbbb98d6faa2bc2698b55f353c56562150977'),
 ('PGPT-20261008-3454','eadaae69f28218c8ea32f6e279c53f1f2cc4ce21ff53a2222ef06de6e85d2eab'),
 ('PGPT-20261008-3455','b5abd1b114323c0d5b0e611765c50d2e6892d7eaa7fb3cf23d5aba20f67477dc'),
 ('PGPT-20261008-3456','b919ba7bfad9fcb677288fb449109fa29c1057e6d85512272d5cb91531418b16')]

def require(ok,why):
    if not ok:raise ValueError(why)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    file=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
    with file.open() as stream:tail=list(deque(stream,maxlen=100))
    rows={json.loads(line)['eventId']:(line,json.loads(line))for line in tail}
    for i,pin in ORIGINALS:require(data.sha(rows[i][0].encode())==pin,'entire original row including LF unchanged')
    specifications=[('PG16216-PUBLIC-LAUNCH-FIVE',dict(low=1,base=4,high=8),[v[0]for v in ORIGINALS[:2]],'PGPT-20261008-3465'),
        ('PG16232-PUBLIC-PROOF-EIGHT',dict(low=0.5,base=2,high=4),[v[0]for v in ORIGINALS[2:]],'PGPT-20261008-3466')]
    def contract(v,group,budget,ids):
        require(v['eventType']=='CHECKPOINT' and v['groupId']==group and v['source']==SOURCE and v['workCategory']=='ADMIN','correction not a new execution group')
        require(v['correctionOfEventIds']==ids and v['groupStartEstimatePp']==v['originalGroupEstimatePp']==budget
                and v['originalEventRowSha256']=={i:dict(ORIGINALS)[i]for i in ids},'all original budget/record bindings')
        require(v['wbsLeafIds']==v['measurementLeafIds']==['WBS-P018-03.02'] and v['primaryWbs']=='WBS-P018-03.02'
                and v['originalPrimaryWbs']==v['canonicalArtifactOwnerPreserved']=='WBS-P018-03','leaf link does not reassign artifact owner')
        require(v['measurementLeafStatus']=='PARTIAL_DELIVERABLE_EVIDENCE_LINK_ONLY_NOT_LEAF_ACCEPTANCE'
                and v['leafAcceptedByCorrection'] is False and type(v['newAccepted'])is int and v['newAccepted']==0
                and v['parentAndChildCostsNotSummed'] is True and v['groupBudgetAdditive'] is False
                and v['componentAdditionalBudgetPp']==0 and v['actualAllocatedPp'] is v['componentActualAllocationPp'] is v['effortPercent'] is None
                and v['attribution']=='UNKNOWN_SHARED_ACCOUNT','no new budget/acceptance/actual allocation')
    for group,budget,ids,i in specifications:
        for old in ids:
            v=rows[old][1];require(v['source']==SOURCE and v['groupId']==group and v['groupStartEstimatePp']==budget and v['actualAllocatedPp']is None,'frozen original group')
        contract(rows[i][1],group,budget,ids)
    config=data.ROOT/'documents/400_PGPT/470_PMO';pins={};nodes={}
    def walk(v):
        if isinstance(v,dict):
            identity=v.get('id');cost=v.get('cost',v.get('remainingCost',{}))
            if identity and 'countsInTotal'in cost:nodes[identity]=cost['countsInTotal']
            for child in v.values():walk(child)
        elif isinstance(v,list):
            for child in v:walk(child)
    for name,pin in [('481_PGPT詳細WBS.json','a37f9c07337a51b61bc2656e6b3d5713221184806c9fb537ed4c545b70a914a5'),
        ('484_WBSコスト枠・細分化.json','7e931d6139d6cd17be240ca9d88a2677e0b7d8828be482b546df1ca00d06e02f'),
        ('487_WBS実行計測規約.json','b4b8c860a44774dc4c90f70fe22db1429aae440e2524e84b3a5ad2de6c6c3713')]:
        blob=(config/name).read_bytes();require(data.sha(blob)==pin,'no WBS/standard rewrite');pins[name]=pin
        if name[:3]in ('481','484'):walk(json.loads(blob))
    sample=[v for _,v in rows.values()if 3385<=int(v['eventId'].rsplit('-',1)[1])<=3464]
    starts=[v for v in sample if v['eventType']=='GROUP_START'];ids={i for v in starts for i in v['wbsLeafIds']}
    require(len(sample)==80 and len(starts)==35 and len(ids)==11 and {i for i in ids if nodes[i]is False}=={'WBS-P018-03'}
            and nodes['WBS-P018-03.02'] is nodes['WBS-P003-05'] is True,'all sampled other leaves/next known leaf checked')
    erratum=rows['PGPT-20261008-3467'][1]
    require(erratum['sampleEventCount']==80 and erratum['sampleGroupStartCount']==35 and erratum['incorrectNotesGroupStartCount']==37
            and erratum['measurementLeafLinksNotReissued'] is True,'explicit notes count correction not second leaf remap')
    negative=[];group,budget,ids,i=specifications[0];v=rows[i][1]
    for key,value in [('source','OLD'),('groupStartEstimatePp',{}),('primaryWbs','WBS-P018-03'),('canonicalArtifactOwnerPreserved','WBS-P018-03.02'),
        ('measurementLeafStatus','ACCEPTED'),('actualAllocatedPp',0),('groupBudgetAdditive',True),('newAccepted',1)]:
        bad=copy.deepcopy(v);bad[key]=value
        try:contract(bad,group,budget,ids)
        except ValueError:negative.append(key)
        else:raise ValueError('false metadata correction')
    require(len(negative)==8,'finite8')
    selected=[rows[i][1]for i,_ in ORIGINALS]+[rows[i][1]for i in ['PGPT-20261008-3465','PGPT-20261008-3466','PGPT-20261008-3467']]
    verify(invocation);OUT.mkdir();data.write(OUT/'original-and-correction-events.safe.json',selected)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,files={'original-and-correction-events.safe.json':data.sha((OUT/'original-and-correction-events.safe.json').read_bytes())},
        originalEventRows=4,leafCorrectionEvents=2,notesCountErratumEvents=1,originalRowsUnchanged=True,
        originalGroupBudgets=[s[1]for s in specifications],measurementLeaf='WBS-P018-03.02',canonicalArtifactOwner='WBS-P018-03',
        sampledEvents=80,sampledGroupStarts=35,sampledWbsIds=11,wbsStandardHashes=pins,metadataNegativeVectors=8,negativeLabels=negative,
        actualCostAllocated=False,individualCostPp=None,productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
