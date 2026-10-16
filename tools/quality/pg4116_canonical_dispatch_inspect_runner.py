"""New-only exact candidate after canonical oracle correction; former artifact never overwritten."""
import inspect
import pg4106_failed_done_owned_inspect_runner as previous

SLOT='pg4116-canonical-dispatch-qualification-v1'


def main():
    ns={**vars(previous),'SLOT':SLOT,'ARTIFACT':previous.W/(SLOT+'-artifact')}
    for function in [previous.freeze,previous.main]:
        exec(compile(inspect.getsource(function),'<new canonical dispatch qualification>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
