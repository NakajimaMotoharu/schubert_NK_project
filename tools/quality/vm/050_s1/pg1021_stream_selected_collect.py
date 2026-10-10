"""New domain mapper four-counter closure, only one changed class, full/native still pending."""
import inspect
import pg1017_stream_selected_collect as previous

def code():
    raw=inspect.getsource(previous.main)
    for a,b in (
      ('pg1016-stream-selected-v7','pg1020-stream-selected-v9'),
      ('2db946551bc8ed861acd277af3c31285d633d097','d4faf8e7eadd2d22563e15380ff80f43883cd6a8'),
      ("assert counters['LINE']=={'covered':128,'missed':1}","assert counters['LINE']=={'covered':129,'missed':0}"),
      ("assert classes(p/'batch'/jar)==classes(old/'batch'/jar)","actual=classes(p/'batch'/jar);prior=classes(old/'batch'/jar)\n    assert actual.keys()==prior.keys() and len(actual)==568\n    assert [n for n in actual if actual[n]!=prior[n]]==['dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader.class']"),
      ("'all343BatchMainBytesEqualQualified926':True","'unchangedBatchClassEntries':567,'changedBatchClassEntries':1,'analyzedBatchClasses':343,'jarClassEntries':568"),
      ("'nativeReaderFourCounter100':False,'unaccepted':['NativeReader caller line212 remains missed despite actual provider failures; do not exclude or claim100']","'nativeReaderFourCounter100':True,'unaccepted':['new source whole regression','new signed/native class','formal global100']"),
      ("'productionMainSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97'","'referenceMainSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97'")):
        assert raw.count(a)==1,a;raw=raw.replace(a,b)
    return raw

if __name__=='__main__':
    env=dict(previous.__dict__);exec(compile(code(),'<PG1021 genuine independent mapper qualification>','exec'),env);env['main']()
