"""Exact currentRoot→realBrowser→present24 chain; original owned SSH to real exit."""
import inspect
import types
import pg4768_new_current_browser_composite as previous
import pg4900_current_admission_image as admission
import pg4906_current_whole_seal as root
import pg4910_current_same_owner_browser as actual

SLOT='pg4912-current-browser-composite-v1'


def compose(raw,chain,digest):
    ns={**vars(previous.previous.previous),'root':types.SimpleNamespace(SEAL=root.SLOT),
        'SOURCE':admission.SOURCE,'BOM':admission.BOM,'SLOT':SLOT}
    return types.FunctionType(previous.previous.previous.compose.__code__,ns)(raw,chain,digest)


def payload(observed):
    root_view=types.SimpleNamespace(SEAL=root.SLOT,seal_payload=root.payload)
    ns={**vars(previous.previous),'actual':actual,'root':root_view,'SOURCE':admission.SOURCE,
        'BOM':admission.BOM,'before':admission.before,'compose':compose}
    return types.FunctionType(previous.previous.payload.__code__,ns)(observed)


def main():
    ns={**vars(previous),'admission':admission,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<current exact Browser chain owned exit>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
