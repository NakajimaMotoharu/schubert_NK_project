"""Safe failed/final typed tool receipts. No replay of watcher, prior entry, source or regression."""
import inspect
import pg4232_publish_fresh_observer_qualification as previous


def main():
    ns={**vars(previous),'SLOTS':['pg4234-canonical-fresh-noargs-once-v1','pg4242-typed-bom-fresh-qualification-v1']}
    raw=inspect.getsource(previous.main).replace('PG4232-fresh-observer-qualification-v1','PG4244-typed-entry-qualification-v1').replace('pg4230-final-fresh-observer-qualification-v1','pg4242-typed-bom-fresh-qualification-v1')
    exec(compile(raw,'<typed safe receipts>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
