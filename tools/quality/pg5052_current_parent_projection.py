"""Typed18 current parent data from exact Root/Browser seal, never new authority."""
import pg4914_current_parent_projection as previous
import pg5036_current_admission_image as admission
import pg5038_current_genuine_terminal as terminal
import pg5048_current_same_owner_browser as browser
import pg5050_current_browser_composite as composite

SLOT = 'pg5052-current-parent-projection-v1'


def payload(digest):
    raw = previous.previous.template.payload(digest, admission.BOM)
    raw = admission.entry.observer.bind(raw.replace(previous.previous.template.SOURCE, admission.SOURCE))
    return terminal.bind(raw).replace('pg2704-operation-current-full-seal-v1', composite.SLOT)


if __name__ == '__main__':
    raise SystemExit(admission.execute(SLOT, payload(browser.receipt(composite.SLOT)['privateBeforeSha256'])))
