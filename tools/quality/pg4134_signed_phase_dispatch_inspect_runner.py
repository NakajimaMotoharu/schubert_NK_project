"""New-only full signed-phase candidate; old73f0 inspect artifact remains immutable."""
import inspect
import pg4106_failed_done_owned_inspect_runner as previous

SLOT='pg4134-signed-phase-dispatch-qualification-v1'


def main():
    ns={**vars(previous),'SLOT':SLOT,'ARTIFACT':previous.W/(SLOT+'-artifact')}
    for function in [previous.freeze,previous.main]:
        exec(compile(inspect.getsource(function),'<signed phase dispatch qualification>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
