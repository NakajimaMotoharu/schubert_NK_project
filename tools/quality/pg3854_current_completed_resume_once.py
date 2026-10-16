"""One new activation of the same completed run after independent literal full11 post."""
import ast
import inspect
import json
from pyflakes.api import check
import pg2360_current_completed_resume_once as proven
import pg3574_current_browser_resume_once as transport
import pg3850_current_resume_post as post
from pg3844_current_resume_sources import SOURCE,BOM,RUN
from pg3852_current_resume_observer import namespace
from pg3800_hygiene_browser_ready import require_ready
from pg1446_current_cold_stage import W

SLOT='pg3854-current-completed-resume-once-v1'


def body():
    proof=json.loads((W/post.SLOT/'manifest.safe.json').read_bytes())
    if not(proof['actualExit']==0 and proof['source']==SOURCE and proof['result']['independentResumeOnlyDeltaVerified']):
        raise ValueError('actual same-source strict independent preparation required')
    raw=proven.body()
    for a,b in [('pg2358','pg3852'),(proven.SLOT,SLOT),
                ('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8',SOURCE),
                ('62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',BOM),
                ('PG2126','PG3748'),('91f5484b-9702-4c7c-97f3-dd5110a853f9',RUN),
                (proven.BEFORE,proof['result']['preparedAfterSha256']),
                ("accepted_before={**after,'configuration':dict(current_view)}",'accepted_before=after'),
                ('require(len(records)==10)','require(len(records)==40)'),
                ('hashlib.sha256(manifest).hexdigest()','hashlib.sha256(manifest.read_bytes()).hexdigest()')]:
        if a not in raw:raise ValueError('one exact current completed-resume role missing '+a[:50])
        raw=raw.replace(a,b)
    old="require(hashlib.sha256(json.dumps(native,sort_keys=True).encode()).hexdigest()=="+repr(proven.NATIVE)+")"
    if raw.count(old)!=1:raise ValueError('one historical native boundary')
    raw=raw.replace(old,"require(native==after['native'])")
    return "def snapshot():return tree(pathlib.Path('/run/schubert-nk/pt-coverage'))\nsummary={'run':"+repr(RUN)+",'completedOriginalOnly':True,'newActivationRequired':True}\n"+raw


def payload(hashes):
    raw=post.payload();tree=ast.parse(raw)
    scopes=[n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='units'for t in x.targets)for x in n.body)]
    if len(scopes)!=1:raise ValueError('one finite fresh ten-reference scope')
    scope=scopes[0];lines=raw.splitlines(keepends=True)
    end=next(i for i in range(scope.lineno-1,scope.end_lineno)if lines[i].startswith('finally:'))
    cut=next(i for i in range(scope.lineno-1,end)if lines[i].startswith(" save=base/"))
    prelude="after=expected;native=expected['native']\n"
    result='WATCH_FILES='+repr(hashes)+'\n'+''.join(lines[:cut])+'\n'.join(' '+line if line else line for line in(prelude+body()).splitlines())+'\n'+''.join(lines[end:scope.end_lineno])+"\ncurrent.update(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    if check(result,'<whole current completed resume admission>'):raise ValueError('complete new admission namespace required')
    compile(result,'<one durable same-run fresh activation>','exec');return result


def main():
    require_ready()
    raw=inspect.getsource(transport.main).replace('pg3572','pg3852').replace('from pg3578_current_browser_ready import require_ready','from pg3800_hygiene_browser_ready import require_ready')
    values={**transport.__dict__,'SOURCE':SOURCE,'BOM':BOM,'RUN':RUN,'SLOT':SLOT,'post':post,'namespace':namespace,'payload':payload}
    exec(compile(raw,'<new current once transport>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
