"""Same immutable Root/all24/Browser chain; preserve historical nested bytes."""
import types
import pg4272_current_browser_composite as previous
import pg4586_current_independent_acceptance as root
import pg4584_current_admission_image as admission
import pg4604_current_same_owner_browser as actual

SLOT='pg4606-current-browser-composite-v1'


def compose(raw,chain,digest):
    ns={**vars(previous.previous),'root':types.SimpleNamespace(SEAL=root.SEAL),'SOURCE':admission.SOURCE,'BOM':admission.BOM,'SLOT':SLOT}
    return types.FunctionType(previous.previous.compose.__code__,ns)(raw,chain,digest)


def payload(binding):
    ns={**vars(previous),'actual':actual,'root':root,'SOURCE':admission.SOURCE,'BOM':admission.BOM,'before':admission.before,'compose':compose}
    return types.FunctionType(previous.payload.__code__,ns)(binding)


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(admission.live()),90))
