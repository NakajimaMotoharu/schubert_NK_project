"""Actual296 Root genuine terminal and original1800; API ready alone is not completion."""
import pg5038_current_genuine_terminal as previous
import pg5476_current_admission_image as admission

TERM='pg5478-current-genuine-terminal-v1'


def bind(raw):
    raw=admission.bind(previous.bind(raw))
    for before,after in((previous.TERM,TERM),('pg5018-parent-watch-v1','pg5466-parent-watch-v1'),
        ('PG4980','PG5430'),('pg4980-manifest.sig','pg5430-manifest.sig')):
        raw=raw.replace(before,after)
    return raw


def payload(observed):return bind(previous.payload(observed))


if __name__=='__main__':raise SystemExit(admission.execute(TERM,payload(admission.live()),90))
