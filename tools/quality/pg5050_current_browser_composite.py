"""Exact newday Root→actualBrowser→present24 chain, original SSH to actual exit."""
import inspect
import types
import pg4912_current_browser_composite as previous
import pg5036_current_admission_image as admission
import pg5042_current_newday_whole_seal as root
import pg5048_current_same_owner_browser as actual

SLOT = 'pg5050-current-browser-composite-v1'


def compose(raw, chain, digest):
    template = previous.previous.previous.previous
    ns = {**vars(template), 'root': types.SimpleNamespace(SEAL=root.SLOT),
          'SOURCE': admission.SOURCE, 'BOM': admission.BOM, 'SLOT': SLOT}
    return types.FunctionType(template.compose.__code__, ns)(raw, chain, digest)


def payload(observed):
    template = previous.previous.previous
    root_view = types.SimpleNamespace(SEAL=root.SLOT, seal_payload=root.payload)
    ns = {**vars(template), 'actual': actual, 'root': root_view, 'SOURCE': admission.SOURCE,
          'BOM': admission.BOM, 'before': admission.before, 'compose': compose}
    return types.FunctionType(template.payload.__code__, ns)(observed)


def main():
    template = previous.previous
    ns = {**vars(template), 'admission': admission, 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(template.main), '<current exact Browser chain owned exit>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
