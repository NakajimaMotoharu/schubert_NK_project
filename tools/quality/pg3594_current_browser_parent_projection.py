"""Actual current composite seal parent eighteen fields, no fabricated receipt."""
import inspect
import pg3478_outbox_parent_projection as template
import pg3650_current_browser_composite_seal_v2 as composite
from pg3564_current_browser_resume_sources import SOURCE

SLOT='pg3594-current-browser-parent-projection-v1'


def payload(sha,bom=None):
    raw=template.payload(sha,bom)
    return raw.replace(template.current.SEAL,composite.SLOT)


def main():
    raw=inspect.getsource(template.old.main).replace('pg2704-operation-current-full-seal-v1',composite.SLOT)
    ns={**template.old.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current actual composite parent18>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
