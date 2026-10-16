"""Actual current composite's typed18 parent data; no stop/start authority by itself."""
import pg4040_literal_invariant_parent_projection as previous
import pg4272_current_browser_composite as composite
import pg4270_current_same_owner_browser as browser
from pg4260_stable_admission_image import execute,BOM

SLOT='pg4280-current-parent-projection-v1'


def payload(digest):return previous.payload(digest,BOM).replace(previous.composite.SLOT,composite.SLOT)


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(browser.receipt(composite.SLOT)['privateBeforeSha256'])))
