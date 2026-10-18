"""Independent PID1 RO mount and returned scopes plus all24/32/full11/native88 preservation."""
import ast
import json
from pyflakes.api import check
import pg5444_ownership_unused_post as unused_post
import pg5446_ownership_ro_sources as role
from pg3786_hygiene_ro_post import EXTRA

SLOT='pg5452-ownership-ro-independent-post-v1'


def payload():
    role.qualify();raw=unused_post.payload()
    marker='save = base / '+repr(unused_post.SLOT)
    if raw.count(marker)!=1:raise ValueError('one new evidence-only RO output')
    raw=raw.replace(marker,'save = base / '+repr(SLOT),1)
    extra=EXTRA.replace('PG3748','PG5430').replace('pg3784-hygiene-ro-completed-v1',role.SAVE)
    marker="    proof = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in root.iterdir() if p.is_file()}"
    if raw.count(marker)!=1:raise ValueError('one held tenRef PID1 RO boundary')
    raw=raw.replace(marker,'\n'.join('    '+line for line in extra.strip().splitlines())+'\n'+marker,1)
    tree=ast.parse(raw);last=tree.body[-1];summary=last.value.args[0].args[0]
    summary.keys.append(ast.Constant('candidateHostReadonlyVerified'));summary.values.append(ast.Constant(True))
    raw=raw.replace(ast.get_source_segment(raw,last),ast.unparse(ast.fix_missing_locations(last)),1)
    if check(raw,'<independent A2/full11/native88 PID1RO>'):raise ValueError('complete standalone static0')
    compile(raw,'<new296 RO independent post>','exec');return raw


def main():
    actual=json.loads((role.W/'pg5450-prepare-ro-v1.safe.json').read_bytes())
    expected={'actualExit':0,'sourceQualified':True,'candidateSource':role.SOURCE,'currentApprovalEpochChanged':False}
    if any(type(actual.get(k))is not type(v)or actual[k]!=v for k,v in expected.items()):raise ValueError('actual currentA2/candidate296 RO completion first')
    return unused_post.current.admission.execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
