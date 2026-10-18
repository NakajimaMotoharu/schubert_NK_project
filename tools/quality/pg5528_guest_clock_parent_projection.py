"""New typed18 projection only after the strict failed-prefix/current Browser chain."""
import types
import pg5492_current_parent_projection as previous
import pg5524_guest_clock_same_owner_browser as browser
import pg5526_guest_clock_browser_composite as composite

admission=previous.admission
SLOT='pg5528-guest-clock-parent-projection-v1'


def payload(digest):
    ns={**vars(previous),'composite':composite}
    return types.FunctionType(previous.payload.__code__,ns)(digest)


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(browser.receipt(composite.SLOT)['privateBeforeSha256'])))
