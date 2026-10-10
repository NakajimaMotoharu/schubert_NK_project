"""Readonly complete1197 comparison before immutable stop stage/dispatch."""
import ast
import inspect
from pg1197_completed_current_capture import payload as previous
import pg1120_current_failed_capture as transport


def payload():
    raw=previous().replace('completed-current-before-v1\'','completed-stop-preflight-v1\'')
    t=ast.parse(raw);last=next(n for n in reversed(t.body)if isinstance(n,ast.Try))
    raw=raw[:last.col_offset+sum(len(x)for x in raw.splitlines(keepends=True)[:last.lineno-1])]
    raw+='''
sealed_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/completed-current-before-v1/before.private.json').read_bytes()
require(hashlib.sha256(sealed_raw).hexdigest()=='398324fdea98d2469067a1e93858cd292b4e0328da5712b709c7bb99cffeadfa');sealed_current=json.loads(sealed_raw)
try:
 for u in CAPTURE_UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 actual=capture();require(actual==capture());require(actual==sealed_current)
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'fullCurrentBeforeIdentical':True,'currentFourOwnedLive':True,'actualPid1DoneStillQualified':True,'newMetadataReferencesNormalClose':True,'guestStartsStopsWrites0':True,'formalAccepted':False}))
'''
    ast.parse(raw);return raw


def main():
    raw=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1200-current-stop-preflight-v1').replace('PG1120-current-failed-capture-v1','PG1200-current-stop-preflight-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(raw,'<current stop readonly preflight>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
