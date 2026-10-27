"""Independent metadata negatives; no JUnit, analyzer, external system or fixture execution."""
import copy
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg11451_gc_fake_guard_context_v3 as stage

def main():
    invocation=capture(__file__)
    assert not stage.POST.exists()
    stage.PRIMARY_SHA='6c9486363b2b4c101036c92542be9fe945bb357aae447fbf5520370bb76f0cfb'
    normal,original,actual=stage.inputs()
    new=stage.discoveries(actual,normal['begin']['inputHashes'])
    path,node=next((p,n) for p,n in actual if n.get('rule')=='AvoidDuplicateLiterals')
    mutations=[]
    bad=copy.deepcopy(node);bad.text=re.sub(r'appears ([0-9]+) times',lambda m:'appears '+str(int(m[1])+1)+' times',bad.text);mutations.append(bad)
    bad=copy.deepcopy(node);bad.text=re.sub(r'on line ([0-9]+)',lambda m:'on line '+str(int(m[1])+1),bad.text);mutations.append(bad)
    bad=copy.deepcopy(node);bad.set('beginline',str(int(bad.get('beginline'))+1));mutations.append(bad)
    for bad in mutations:
        try:
            stage.identity(path,bad,original,actual,new)
        except ValueError:
            pass
        else:
            raise AssertionError('wrong literal count/first coordinate accepted')
    rows=data.read_checked(stage.OUT/'contexts.json',data.read_checked(stage.OUT/'manifest.json',stage.PRIMARY_SHA)['contextsSha256'])
    selected=[r for r in rows if re.fullmatch(r'(api|web|batch)gc016\w*',r['attributes'].get('method',''))]
    assert len(selected)==3
    guard='finally{resource.onCloseCallback=()->{};if(!resource.closeConfirmed)resource.close();}'
    mutants=[guard.replace('resource.onCloseCallback=()->{};',''),guard.replace('if(!resource.closeConfirmed)resource.close();','if(!other.closeConfirmed)other.close();'),
        'finally{if(!resource.closeConfirmed)resource.close();resource.onCloseCallback=()->{};}']
    for row in selected:
        body=''.join(stage.method_tokens((data.ROOT/row['path']).read_text(),row['attributes']['method']))
        assert guard in body and all(mutant not in body for mutant in mutants)
        for mutant in mutants:
            bad=copy.deepcopy(rows);index=next(i for i,r in enumerate(bad) if r['id']==row['id']);bad[index]['basis']['ownership']=mutant
            try:
                stage.require(bad,original,normal['begin']['inputHashes'],actual,new)
            except ValueError:
                pass
            else:
                raise AssertionError('wrong concrete cleanup basis accepted')
    verify(invocation)
    stage.post()
    data.write(stage.POST/'additional-negative-vectors.json',dict(invocation=invocation,coordinateNegatives=3,cleanupBasisNegatives=9,productTestsExecuted=0,coverage=None))
    print(data.sha((stage.POST/'additional-negative-vectors.json').read_bytes()))

if __name__=='__main__':
    main()
