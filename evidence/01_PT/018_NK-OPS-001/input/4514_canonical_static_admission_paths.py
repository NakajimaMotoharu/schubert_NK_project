"""BUG3135 join actual raw paths to declared sources without changing any review or count."""
from pathlib import Path
import copy
import json
import sys

def canonical_path(value,root,allowed):
    p=Path(value)
    if '..' in p.parts:raise ValueError('parent traversal outside declared source')
    if p.is_absolute():
        try:p=p.relative_to(root)
        except ValueError:raise ValueError('outside repository') from None
    name=str(p)
    if name not in allowed:raise ValueError('undeclared source before read')
    return name

def main():
    root=Path.cwd();profile=Path(sys.argv[1]);old=Path(sys.argv[2]);out=Path(sys.argv[3])
    c=json.loads(profile.read_text());previous=json.loads(old.read_text())
    allowed=set(c['mainSources'])|{x['path'] for x in c['testSources']}
    assert previous['profile']==c['id'] and not out.exists()
    sample=next(iter(sorted(allowed)))
    assert canonical_path(sample,root,allowed)==canonical_path(str(root/sample),root,allowed)==sample
    negative=[]
    for value in ['/tmp/Outside.java','../Outside.java',str(root/'src/Undeclared.java')]:
        try:canonical_path(value,root,allowed)
        except ValueError:negative.append(value)
        else:raise ValueError('undeclared or outside source accepted')
    result=copy.deepcopy(previous)
    for row in result['sourceAnchors']:row['path']=canonical_path(row['path'],root,allowed)
    assert len(result['sourceAnchors'])==len(previous['sourceAnchors'])
    for before,after in zip(previous['sourceAnchors'],result['sourceAnchors']):
        assert {k:v for k,v in before.items() if k!='path'}=={k:v for k,v in after.items() if k!='path'}
    out.open('x').write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,siteMessages=len(result['sourceAnchors']),pathPositive2=True,
        pathNegatives=len(negative),reviewsAndMultiplicitiesUnchanged=True)))

if __name__=='__main__':main()
