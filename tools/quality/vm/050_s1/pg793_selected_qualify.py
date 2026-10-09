"""Independent fixed791 qualification; only the literal branchless enum has sparse BRANCH0."""
import inspect
from pg792_selected_qualify import main as prior_main


def counters_valid(name,counters):
    required={'LINE','METHOD','CLASS'}
    if name.endswith('$CompletionPhase'):
        if 'BRANCH'in counters:return False
    else:required.add('BRANCH')
    return required<=counters.keys()and all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in required)


if __name__=='__main__':
    import pg792_selected_qualify as previous
    raw=inspect.getsource(prior_main).replace('pg792-selected-qualification-v1.safe.json','pg793-selected-qualification-v1.safe.json')
    raw=raw.replace("assert all(counters[k]['missed']==0 for k in ('LINE','METHOD','CLASS','BRANCH'))", "assert counters_valid(cls.get('name'),counters)\n            if cls.get('name').endswith('$CompletionPhase'):counters['BRANCH']={'missed':0,'covered':0,'applicable':False,'reason':'literal enum contains no conditional branch; JaCoCo sparse XML'}")
    context={**previous.__dict__,'counters_valid':counters_valid};exec(compile(raw,'<793 fixed same XML>','exec'),context);context['main']()
