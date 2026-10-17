"""SSC303 new-only stage/verify/execute of current existingADMIN20; no Root replay."""
import inspect
import sys
import pg4826_new_current_bootstrap_dispatch as previous
import pg4932_current_bootstrap_sources as role

W=role.W
SLOT='pg4936-current-bootstrap'
REMOTE='/home/ubuntu/pg4936-current-bootstrap-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
STAGE=previous.STAGE.replace('PG4702','PG4860')


def namespace():
    ns={**vars(previous),'role':role,'W':W,'SLOT':SLOT,'REMOTE':REMOTE,'GUEST':GUEST,'STAGE':STAGE}
    fixed=inspect.getsource(previous.fixed).replace('pg4824-frozen-v1.safe.json','pg4934-frozen-v1.safe.json')
    main=inspect.getsource(previous.main).replace('Pg4820','Pg4932').replace('PG4702','PG4860')
    exec(compile(fixed+'\n'+main,'<current once closed nested stage and existing20>','exec'),ns)
    return ns


if __name__=='__main__':
    if sys.argv[1:]not in (['stage'],['verify'],['execute']):raise SystemExit('one explicit current existing20 phase')
    raise SystemExit(namespace()['main']())
