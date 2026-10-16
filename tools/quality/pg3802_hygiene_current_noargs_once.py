"""One new-source ordinary noargs run; sealed originals/native preserved, no old authority."""
import ast
import inspect
import json
from pyflakes.api import check
import pg3464_outbox_current_noargs_once as proven
import pg2178_newsource_noargs_once as transport
import pg3794_hygiene_publication_post as post
from pg3798_hygiene_current_observer import namespace, SOURCE, BOM
from pg3800_hygiene_browser_ready import require_ready
from pg1446_current_cold_stage import W

SLOT='pg3802-hygiene-current-noargs-once-v1'


def body():
    raw=proven.body()
    for a,b in [('pg3462','pg3798'),(proven.SLOT,SLOT),(proven.SOURCE,SOURCE),(proven.BOM,BOM),('PG3420','PG3748'),('require(len(records)==22)','require(len(records)==34)')]:
        if a not in raw:raise ValueError('one actual newsource ordinary boundary required: '+a)
        raw=raw.replace(a,b)
    return raw


def payload(hashes):
    raw=post.payload();cut=raw.index("save=base/'pg3794-hygiene-publication-independent-post-v1'");raw=raw[:cut]
    tree=ast.parse(raw);scopes=[n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='units'for t in x.targets)for x in n.body)]
    if len(scopes)!=1:raise ValueError('one actual finite ten-reference admission scope')
    selected=scopes[0];lines=raw.splitlines(keepends=True);end=next(i for i in range(selected.lineno-1,selected.end_lineno)if lines[i].startswith('finally:'))
    action=body().replace('print(json.dumps(current))\nraise SystemExit(r.returncode)','')
    if action==body():raise ValueError('client output only after finite scope closes')
    _,summary,_=post.role.mapping.current_tuple()
    prelude="""parser_raw=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parser_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
parser_node=next(n for n in ast.parse(parser_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
parser_ns={'re':re};exec(compile(ast.Module(body=[parser_node],type_ignores=[]),'<fixed actual ExecStart declaration parser>','exec'),parser_ns)
exec_record=parser_ns['exec_record']
after=expected;native=expected['native'];manifest=(root/'RELEASE-MANIFEST.json').read_bytes()
def snapshot():return tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
"""+'summary='+repr(summary)+'\n'
    result='import ast\nWATCH_FILES='+repr(hashes)+'\n'+''.join(lines[:end])+'\n'.join(' '+line if line else line for line in(prelude+action).splitlines())+'\n'+''.join(lines[end:selected.end_lineno])+"\ncurrent.update(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    if check(result,'<whole independent fresh ordinary admission>'):raise ValueError('complete admission namespace required')
    compile(result,'<new7fff ordinary one durable Root start>','exec');return result


def main():
    require_ready()
    if transport.subprocess.check_output(['git','diff','--name-only',SOURCE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('qualified source unchanged before new admission')
    proof=json.loads((W/post.SLOT/'manifest.safe.json').read_bytes())
    if proof.get('actualExit')!=0 or proof.get('result',{}).get('productionSource')!=SOURCE or proof['result'].get('unitExchangeAndReload')is not False:raise ValueError('genuine newsource independent post required')
    raw=inspect.getsource(transport.main).replace('pg2176','pg3798').replace('pg2174-normal-publication-full-post-v1',post.SLOT).replace("post['guest']","post['result']")
    values={**transport.__dict__,'namespace':namespace,'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<one newsource noargs admission transport>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
