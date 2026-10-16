"""Safe failed/new tool receipts only; existing watch remains running, no VM operation."""
import hashlib
import inspect
import pg4232_publish_fresh_observer_qualification as previous


def main():
    ns={**vars(previous),'SLOTS':['pg4222-fresh-current-noargs-once-v1','pg4236-canonical-fresh-qualification-v1']}
    raw=inspect.getsource(previous.main).replace('PG4232-fresh-observer-qualification-v1','PG4238-canonical-entry-qualification-v1').replace('pg4230-final-fresh-observer-qualification-v1','pg4236-canonical-fresh-qualification-v1')
    exec(compile(raw,'<canonical source safe publication>','exec'),ns)
    result=ns['main']()
    digest=hashlib.sha256((previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4238-canonical-entry-qualification-v1/manifest.json').read_bytes()).hexdigest()
    if len(digest)!=64:raise ValueError('complete publication')
    return result


if __name__=='__main__':raise SystemExit(main())
