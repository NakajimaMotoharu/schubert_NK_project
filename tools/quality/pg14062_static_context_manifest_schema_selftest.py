"""New raw-schema vectors only; prior core eight/49 are verified by hash, never replayed."""
import copy
import hashlib
import json
import static_context_reader_v1 as reader
import static_context_post_v2 as post
from pg14060_static_context_common_core_selftest import fixture,NAME
from host_tool_invocation import capture,verify

OUT=reader.data.BASE/'PG14062-static-context-manifest-schema-tool-selftest-v1'
CORE='0c7a1ec635fbc463645249950a5803f9ed4c6cdf69828ca8ee794f8bd94dc9b9'
def main():
    invocation=capture(__file__);assert not OUT.exists()
    core=reader.data.read_checked(reader.data.BASE/'PG14060-static-context-common-core-tool-selftest-v1/manifest.json',CORE)
    verify(core['invocation']);assert core['toolPositiveVectors']==8 and core['toolNegativeVectors']==49 and core['productTestsExecuted']==0
    plan=fixture()[0];rows=[dict(id='PMD-00001',path=NAME)];measurement_source='db33c6a371d3dbc8e84f70462e0e56351bbb18b4'
    raw=dict(actualExit=0,source=reader.cfg.SOURCE,planSha256=hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(',',':')).encode()).hexdigest(),reviewSha256='a'*64,normalManifestSha256=reader.NORMAL_SHA,measurementReference=list(reader.MEASURED),measurementSource=measurement_source,wholeCurrentStaticMeasurement=False,sourceContexts=1,sourceFiles=1,rawRetained=1,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,qualityGatePass=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False)
    positives=[];negatives=[]
    post.validate_manifest(raw,plan,rows,measurement_source);positives.append('explicit-raw-schema')
    post.validate_manifest(json.loads(json.dumps(raw)),plan,rows,measurement_source);positives.append('json-roundtrip-typed-schema')
    def rejected(label,value,items=rows):
        assert reader.wire(value)!=reader.wire(raw) or reader.wire(items)!=reader.wire(rows)
        try:post.validate_manifest(value,plan,items,measurement_source)
        except ValueError:negatives.append(label)
        else:raise AssertionError('false original manifest accepted: '+label)
    for key in ['actualExit','sourceContexts','sourceFiles','rawRetained','productTestsExecuted','newAccepted']:
        for value in [raw[key]+1,bool(raw[key])]:
            bad=copy.deepcopy(raw);bad[key]=value;rejected(key+':'+type(value).__name__,bad)
    for key in ['sourceChanged','wholeCurrentStaticMeasurement','nativeQualification','qualityGatePass','formalUpdated','wholeF03Accepted','whole451Accepted']:
        for value in [True,0,'MISSING']:
            bad=copy.deepcopy(raw)
            if value=='MISSING':bad.pop(key)
            else:bad[key]=value
            rejected(key+':'+str(value),bad)
    for key in ['coverage','effortPercent']:
        bad=copy.deepcopy(raw);bad[key]=0;rejected(key+':zero',bad)
        bad=copy.deepcopy(raw);bad.pop(key);rejected(key+':missing',bad)
    for key,value in [('source','0'*40),('normalManifestSha256','0'*64),('planSha256','0'*64),('reviewSha256','not-a-digest'),('measurementReference',[]),('measurementSource','0'*40)]:
        bad=copy.deepcopy(raw);bad[key]=value;rejected(key+':mismatch',bad)
    rejected('unknown-row-id',raw,[dict(id='PMD-00002',path=NAME)])
    rejected('unknown-row-path',raw,[dict(id='PMD-00001',path='UNKNOWN')])
    rejected('duplicate-row',raw,rows+rows)
    assert len(positives)==2 and len(negatives)==46
    verify(core['invocation']);verify(invocation);OUT.mkdir()
    reader.data.write(OUT/'manifest.json',dict(actualExit=0,source=reader.cfg.SOURCE,invocation=invocation,priorPureCoreManifestSha256=CORE,priorCoreVectorsReexecuted=0,toolPositiveVectors=len(positives),positiveLabels=positives,toolNegativeVectors=len(negatives),negativeLabels=negatives,pureMetadataFixturesOnly=True,filesystemFixtureCreated=False,productTestsExecuted=0,productClassesLoaded=False,oldSuccessfulContextReplayed=False,currentContext22Replayed=False,actualExternalActions=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None,toolStatus='PURE_CORE_AND_RAW_SCHEMA_QUALIFIED_FIRST_NEW_CONTEXT_IO_POST_PENDING',correctedToolBug='BUG2086/YKT1834',whole451Accepted=False))
    print(reader.data.sha((OUT/'manifest.json').read_bytes()))
    print(reader.wire(dict(positive=len(positives),negative=len(negatives),productTestsExecuted=0)))
if __name__=='__main__':main()
