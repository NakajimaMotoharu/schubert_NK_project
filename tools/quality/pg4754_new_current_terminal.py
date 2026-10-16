"""Read-only independent genuine terminal on this Root; never API-ready-only success."""
import pg4586_current_independent_acceptance as previous
import pg4752_new_current_admission_image as admission

TERM='pg4754-new-current-genuine-terminal-v1'


def bind(raw):
    raw=admission.bind(raw)
    for old,new in [(previous.TERM,TERM),('pg4560-parent-watch-v1','pg4734-parent-watch-v1'),
                    ('PG4432','PG4702'),('pg4432-manifest.sig','pg4702-manifest.sig')]:raw=raw.replace(old,new)
    return raw


def payload(observed):return bind(previous.terminal_payload(observed))


if __name__=='__main__':raise SystemExit(admission.execute(TERM,payload(admission.live()),90))
