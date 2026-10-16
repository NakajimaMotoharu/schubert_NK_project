"""Current typed parent18 projection from separately qualified composite artifact."""
import pg4280_current_parent_projection as previous
import pg4584_current_admission_image as admission
import pg4648_composite_artifact_requalification as composite
import pg4604_current_same_owner_browser as browser

SLOT='pg4650-current-parent-projection-v1'


def payload(digest):
    raw=admission.entry.observer.bind(previous.payload(digest))
    return raw.replace(previous.composite.SLOT,composite.SLOT)


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(browser.receipt(composite.SLOT)['privateBeforeSha256'])))
