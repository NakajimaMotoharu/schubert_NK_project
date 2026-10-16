"""New-only complete approved189 release entries incl canonical SHA256SUMS; same fixed Java."""
import inspect
import pg4106_failed_done_owned_inspect_runner as previous

SLOT='pg4144-complete-signed-dispatch-qualification-v1'


def main():
    ns={**vars(previous),'SLOT':SLOT,'ARTIFACT':previous.W/(SLOT+'-artifact')}
    for function in [previous.freeze,previous.main]:
        exec(compile(inspect.getsource(function),'<complete signed dispatch qualification>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
