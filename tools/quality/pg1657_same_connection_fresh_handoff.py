"""SSC273 new-only independent fresh proof then same-connection owned TERM.

Fresh proof completion is durable before reservation/signal. Original1653
refusal and old actor/proof remain unchanged; only current shared chrono is
recorded separately. No new SSH connection occurs between proof and TERM.
"""
import inspect
import pg1653_retained_no_db_once_handoff as prior
from pg1655_fresh_ancestor_contract import validate_actor, same_fresh

SLOT = 'pg1657-same-connection-fresh-handoff-v1'

FRESH = r'''
 fresh_first=json.loads(json.dumps(actor()));fresh_second=json.loads(json.dumps(actor()));same_fresh(fresh_first,fresh_second)
 fresh_upper_ns=time.time_ns();validate_actor(expected['actor'],fresh_first,fresh_upper_ns)
 linked=pathlib.Path('/run');linked_s=linked.lstat()
 require(stat.S_ISDIR(linked_s.st_mode)and linked_s.st_uid==linked_s.st_gid==0 and not os.listxattr(linked))
 require(tuple(fresh_first['fds']['29']['metadata'])==metadata9(linked_s)==tuple(fresh_first['fds']['32']['metadata']))
 fresh_actor=fresh_first
 owner(289328,5627480)
 save.mkdir(mode=0o700);private('proof-before.private.json',saved)
 fresh_body={'oldProofSha256':PROOF_SHA,'actor':fresh_actor,'oldActor':expected['actor'],'native':native,'oldNativeUnchanged':True,'locks':expected['locks'],'sharedAncestorUpperNs':fresh_upper_ns,'allOriginalValuesUnchanged':True,'allTenKernelEmpty':True,'clientAdvisory0':True,'independentFreshProofComplete':True,'signalsIssued':0}
 fresh_raw=json.dumps(fresh_body,sort_keys=True).encode();fresh_sha=hashlib.sha256(fresh_raw).hexdigest()
 private('fresh-proof.private.json',fresh_raw);private('fresh-complete.private',('independentFreshProofComplete=true\nsignalsIssued=0\nproofSha256='+fresh_sha+'\n').encode())
 same_fresh(fresh_actor,json.loads(json.dumps(actor())));owner(289328,5627480)
 print(json.dumps({'stage':'FRESH_READONLY_PROOF_COMPLETE','actualExit':0,'proofSha256':fresh_sha,'pid':289328,'ticks':5627480,'fdCount':97,'sameConnection':True,'signalsIssued':0,'allOriginalValuesUnchanged':True,'formalAccepted':False}),flush=True)
'''


def payload():
    raw = prior.payload()
    raw = raw.replace('pg1653-retained-no-db-handoff-v1', SLOT)
    old = "require(json.loads(json.dumps(a))==expected['actor']and json.loads(json.dumps(locks))==expected['locks'])"
    if raw.count(old) != 1:
        raise ValueError('one stale actor comparison boundary required')
    raw = raw.replace(old, "same_fresh(fresh_actor,json.loads(json.dumps(a)));require(json.loads(json.dumps(locks))==expected['locks'])")
    marker = " owner(289328,5627480)\n save.mkdir(mode=0o700);private('proof-before.private.json',saved)"
    if raw.count(marker) != 1:
        raise ValueError('one same-connection fresh proof boundary required')
    raw = raw.replace(marker, FRESH.rstrip())
    raw = raw.replace("'formalAccepted':False}))", "'formalAccepted':False,'freshProofSha256':fresh_sha,'sameConnection':True}))")
    raw = inspect.getsource(validate_actor) + '\n' + inspect.getsource(same_fresh) + '\n' + raw
    compile(raw, '<SSC273 complete independent fresh proof and once handoff>', 'exec')
    return raw


def main():
    code = inspect.getsource(prior.main).replace('SSC272', 'SSC273')
    code = code.replace("value['guest'] = json.loads(r.stdout)", "rows=[prior_json.loads(line) for line in r.stdout.splitlines() if line.strip().startswith(b'{')]\n        if len(rows)!=2 or rows[0].get('stage')!='FRESH_READONLY_PROOF_COMPLETE' or rows[0]['signalsIssued']!=0 or rows[1]['freshProofSha256']!=rows[0]['proofSha256']:raise ValueError('separate fresh-proof and actual result required')\n        value['freshProof']=rows[0];value['guest']=rows[1]")
    code = code.replace("(out / 'stderr.private.log').write_bytes(r.stderr)", "(out / 'stderr.private.log').write_bytes(r.stderr)\n    (out / 'stages.private.jsonl').write_bytes(r.stdout)")
    ns = {**prior.__dict__, 'SLOT': SLOT, 'payload': payload, 'design_scope': design_scope, 'prior_json': prior.json}
    exec(compile(code, '<new same-connection proof-stage handoff transport>', 'exec'), ns)
    return ns['main']()


def design_scope(text, path):
    marker = '## SSC-273（' if '/914_' in path else 'SSC273（' if '/354_' in path else 'SSC273：'
    if text.count(marker) != 1:
        raise ValueError('one published fresh-image authority required')
    tail = text[text.index(marker):]
    boundary = '\n## SSC-' if '/914_' in path else '\n\n'
    return tail.split(boundary, 1)[0].strip()


if __name__ == '__main__':
    raise SystemExit(main())
