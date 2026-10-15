"""BUG1309 corrected new-only seal; original failed3592 payload/input/actual1 preserved."""
import inspect
import pg3592_current_browser_composite_seal as previous

SLOT='pg3650-current-browser-composite-full-seal-v2'


def namespace():
    ns={**previous.__dict__,'SLOT':SLOT}
    for fn in [previous.compose,previous.payload,previous.main]:
        exec(compile(inspect.getsource(fn),'<new-only immutable-input composite v2>','exec'),ns)
    return ns


def payload(binding):return namespace()['payload'](binding)


def main():return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
