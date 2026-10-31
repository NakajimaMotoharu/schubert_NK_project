"""Cross-check three observed metadata transfer defects without reexecuting Product."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15699_media_scenario_pre_sql_twenty_two_independent as oracle
import pg15697_media_scenario_pre_sql_twenty_two_post as post
OUT=data.BASE/'PG15707-media-scenario-metadata-transfer-negatives-v1'
def main():
    invocation=capture(__file__);assert not OUT.exists()
    oracle.raw=data.read_checked(data.BASE/'PG15694-media-scenario-pre-sql-twenty-two-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',oracle.PIN);oracle.assess(p)
    variants=[]
    for label in ['old-suite-three','old-unknown-owner-three','missing-two-nocode']:
        bad=copy.deepcopy(p)
        if label=='old-suite-three':bad['suites']=3
        elif label=='old-unknown-owner-three':bad['owners']['synthetic-unregistered-test']=copy.deepcopy(next(v for v in bad['owners'].values() if v['ownershipStatus']=='UNKNOWN'))
        else:bad['metadataClasses']=[]
        assert json.dumps(bad,sort_keys=True)!=json.dumps(p,sort_keys=True)
        try:oracle.assess(bad)
        except ValueError:variants.append(label)
        else:raise ValueError('old transfer defect accepted '+label)
    assert len(variants)==3
    verify(p['invocation']);verify(oracle.raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=oracle.PIN,negativeLabels=variants,negativeCount=3,bugReferences=['BUG2141','BUG2142','BUG2143'],productTestsExecuted=0,formalUpdated=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
