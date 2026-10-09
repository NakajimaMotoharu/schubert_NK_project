"""New fixed selected profile: source names and exact actual XML join, old790 not accepted."""
from pathlib import Path
import xml.etree.ElementTree as ET
from pg790_completion_selected import TESTS as OLD_TESTS

R=Path(__file__).resolve().parent
T=R.parents[3]
TESTS={'batch':[n if n!='MorningPendingAdmissionTest'else'MorningResumeAdmissionTest'for n in OLD_TESTS['batch']]}


def source_names(names,files):
    if len(names)!=len(set(names)):return False
    return all(sum(f.name==n+'.java'for f in files)==1 for n in names)


def xml_join(names,files):
    actual={};tests=0
    for f in files:
        node=ET.parse(f).getroot();name=node.get('name','').split('.')[-1]
        if name in actual or any(int(node.get(k,'-1'))!=0 for k in ('failures','errors','skipped')):return False,0
        if int(node.get('tests','0'))<1:return False,0
        actual[name]=f;tests+=int(node.get('tests'))
    return set(actual)==set(names),tests


if __name__=='__main__':
    files=list((T/'src/schubert-nk-batch/src/test').rglob('*.java'));assert source_names(TESTS['batch'],files)
    raw=(R/'pg790_completion_selected.py').read_text().replace('pg790-completion-selected-v1','pg791-completion-selected-v1')
    # The original runner loads its template before fixed TESTS is inserted.
    raw=raw.replace("TESTS={'batch':", "TESTS={'batch':",1).replace("'MorningPendingAdmissionTest'", "'MorningResumeAdmissionTest'")
    env={'__file__':str(R/'pg791_completion_selected.py'),'__name__':'__main__'}
    exec(compile(raw,'<new791 all requested real suites>','exec'),env)
    folder=Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg791-completion-selected-v1/batch')
    okay,count=xml_join(TESTS['batch'],list(folder.glob('TEST-*.xml')));assert okay
    print({'selectedXmlExact':True,'actualSuites':len(TESTS['batch']),'tests':count,'old790NotRunNotAccepted':True})
