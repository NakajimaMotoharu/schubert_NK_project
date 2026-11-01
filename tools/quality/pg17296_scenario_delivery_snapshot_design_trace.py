"""Bind handwritten Scenario response offsets to approved UI tables, not Production-generated goldens."""
import copy
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17296-scenario-delivery-snapshot-design-trace-v1'
IND=('PG17294-scenario-delivery-snapshot-six-independent-v1','24606bbc94227b36567f4d0bfc8a3f09e1b734112fb72786239fcfdf7aa9a612')
POST=('PG17292-scenario-delivery-snapshot-six-post-v1','7b20529012b0ffe4964a7216607503184ce24d82537c6c5c61639b0c6f242316')
DATA=[('Script file ID',1,12),('Game code',13,12),('Display title',25,256),('Display path',281,512),('Previous file ID',793,12),('Previous title',805,256),('Next file ID',1061,12),('Next title',1073,256),('Delivery mode',1329,1),('File ID',1330,36),('File relative path',1366,256),('File byte長',1622,12),('File SHA-256',1634,64),('File record長',1698,6),('File record件数',1704,9),('Reserved',1713,16)]
RECORD=[('Entry ID',1,12),('Entry sequence',13,6),('Line番号',19,8),('Entry type',27,10),('Speaker名',37,128),('本文',165,4096),('Audio sequence',4261,3),('Audio ID',4264,12),('Audio display path',4276,512),('Reserved',4788,13)]
def require(ok,why):
    if not ok:raise ValueError(why)
def rows(section):
    result=[]
    for line in section.splitlines():
        if not line.startswith('|'):continue
        cells=[v.strip() for v in line.strip('|').split('|')]
        if len(cells)>=3 and cells[1].replace(',','').isdigit() and cells[2].replace(',','').isdigit():
            result.append((cells[0],int(cells[1].replace(',','')),int(cells[2].replace(',',''))))
    return result
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    q,p=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in [IND,POST]]
    require(all(v['actualExit']==0 and v['source']==SOURCE and v['tests']==6 for v in [q,p]) and q['postSha256']==POST[1],'qualified actual six')
    refs={};contents={}
    for root,nums in [('documents/300_SS',['323','332','333']),('documents/200_UI',['234','237']),('documents/100_RD',['121','141'])]:
        for num in nums:
            paths=list((data.ROOT/root).glob('*/'+num+'_*.md'));require(len(paths)==1,'unique approved document')
            path=paths[0];relative=str(path.relative_to(data.ROOT));blob=path.read_bytes()
            require(blob==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'same approved design')
            refs[relative]=data.sha(blob);contents[num]=blob.decode()
    ui=contents['234'];actual_data=rows(ui.split('### 10.2 ',1)[1].split('### 10.3 ',1)[0]);actual_record=rows(ui.split('### 10.3 ',1)[1].split('## 11.',1)[0])
    require(actual_data==DATA and actual_record==RECORD,'independent complete one-based UI tables')
    require(DATA[-1][1]+DATA[-1][2]-1==1728 and RECORD[-1][1]+RECORD[-1][2]-1==4800,'whole exact widths')
    labels=[]
    for index in range(len(DATA)):
        bad=copy.deepcopy(DATA);name,begin,length=bad[index];bad[index]=(name,begin+1,length)
        require(bad!=actual_data,'one-byte shifted data field rejected');labels.append('data-'+name)
    for index in range(len(RECORD)):
        bad=copy.deepcopy(RECORD);name,begin,length=bad[index];bad[index]=(name,begin,length+1)
        require(bad!=actual_record,'one-byte length change rejected');labels.append('record-'+name)
    require(all(x in contents['333'] for x in ['200 record','1,000,000','1～10,000','最大48,000,000','file I/Oはcommit後']),'approved threshold/physical responsibility')
    methods=[dict(testId=v['classname']+'#'+v['name'],className=v['classname'],method=v['name'],result=v['result']) for v in p['cases']]
    require(len(methods)==6 and len({v['testId'] for v in methods})==6,'unique actual identities')
    verify(q['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,independentPost=list(IND),originalPost=list(POST),approvedDesignHashes=refs,originMain=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),programId='NK-SCN-001',caseMappings=methods,uiOneBasedDataFields=DATA,uiOneBasedRecordFields=RECORD,goldenUsesZeroBasedOffsets=True,offsetConversion='ZERO_BASED=APPROVED_ONE_BASED-1',dataBytes=1728,recordBytes=4800,metadataNegativeVectors=len(labels),negativeLabels=labels,directRequirementIds=['FUN-004'],supportingRequirementIds=['FIL-002','FIL-006'],unqualifiedPhysicalRequirementIds=['FIL-001','FIL-003','FIL-004','FIL-005','FIL-007','FIL-008','FIL-009','FUN-005'],stubDescriptorHashNotContentOracle=True,actualFileOrDatabaseOwnershipQualified=False,snapshotShapeBranchesStillMissing=2,productTestsExecuted=0,sourceChanged=False,designChanged=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
