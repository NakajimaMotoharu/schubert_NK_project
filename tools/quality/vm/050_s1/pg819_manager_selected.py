"""Fresh selected run after818 format-only refusal; old actual1 preserved."""
from pathlib import Path
from pg818_manager_selected import source,TESTS
R=Path(__file__).resolve().parent
if __name__=='__main__':
 for name in TESTS['batch']:assert len(list((R.parents[3]/'src/schubert-nk-batch/src/test').rglob(name+'.java')))==1
 raw=source().replace('pg818-manager-selected-v1','pg819-manager-selected-v1')
 exec(compile(raw,'<819 fresh selected afterformat>','exec'),{'__file__':str(R/'pg819_manager_selected.py'),'__name__':'__main__'})
