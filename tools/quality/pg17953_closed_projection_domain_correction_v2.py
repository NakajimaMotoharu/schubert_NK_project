"""Correct one copied disclosure field; preserve original completed PT and analyzer bytes."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
OLD=('PG17952-closed-projection-six-post-v1','d82c2f5047798011110314ec634bcbd8abff267c00dd6d906d4f61455bd928c7')
OUT=data.BASE/'PG17953-closed-projection-six-post-v2'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
def contract(value):
    assert value['normalOrdinaryTestSourceDomain'] is False
    assert value['normalOrdinaryMethodCount']==0 and value['independentQualityMethodCount']==6
def main():
    invocation=capture(__file__);assert not OUT.exists()
    old=data.read_checked(data.BASE/OLD[0]/'manifest.json',OLD[1]);verify(old['invocation'])
    raw=data.read_checked(data.BASE/'PG17950-closed-projection-six-pt-v1/manifest.json','c32700867c3272c5453906200ebde55b097f6f93e7ac638b1c3ad8b954bddf7a')
    assert old['source']==raw['source']==SOURCE and old['actualExit']==raw['actualExit']==0 and old['tests']==raw['tests']==6 and old['suites']==1
    assert old['normalOrdinaryTestSourceDomain']=='MIXED_ORIGINAL_FOUR_AND_SEPARATE_QUALITY_TWO'
    quality=data.ROOT/'tools/quality/architecture/ClosedProjectionValueContractTest.java'
    assert raw['begin']['selectedSuites']=={'ClosedProjectionValueContractTest':6} and raw['begin']['testSourceHashes'][str(quality)]==data.sha(quality.read_bytes())=='96dc488720504882f06ef476b0482b34975b400a7d6feec55a9b839385c9c29d'
    assert all(not name.startswith(str(data.ROOT/'src/')) for name in raw['begin']['testSourceHashes'])
    result=copy.deepcopy(old);result['normalOrdinaryTestSourceDomain']=False
    result.update(normalOrdinaryMethodCount=0,independentQualityMethodCount=6)
    contract(result);checks=[]
    for field,value in [('normalOrdinaryTestSourceDomain','MIXED_ORIGINAL_FOUR_AND_SEPARATE_QUALITY_TWO'),('normalOrdinaryMethodCount',4),('independentQualityMethodCount',2)]:
        bad=copy.deepcopy(result);bad[field]=value
        try:contract(bad)
        except AssertionError:checks.append(field)
        else:raise AssertionError('wrong source domain accepted')
    changed={'normalOrdinaryTestSourceDomain','normalOrdinaryMethodCount','independentQualityMethodCount'}
    assert all(result[k]==v for k,v in old.items() if k not in changed)
    result.update(invocation=invocation,originalCompletedPostReference=list(OLD),originalCompletedPostInvocation=old['invocation'],domainCorrectionNegativeVectors=checks,productAndAnalyzerReexecutedByCorrection=0)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
