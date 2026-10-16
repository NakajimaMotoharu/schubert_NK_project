"""BUG1348 affected four owned tests and full closures; no running parent/source mutation."""
import inspect
import pg4290_current_owned_qualification as previous

SLOT='pg4296-immutable-owned-qualification-v1'


def main():
    ns={**vars(previous),'SLOT':SLOT,'__file__':__file__}
    raw=inspect.getsource(previous.main)
    if raw.count("b'Ran 3 tests'")!=1 or raw.count("'toolTests':3")!=1:raise ValueError('one affected test inventory required')
    raw=raw.replace("b'Ran 3 tests'","b'Ran 4 tests'").replace("'toolTests':3","'toolTests':4")
    exec(compile(raw,'<immutable final output affected qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
