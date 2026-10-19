"""Actual0ea genuine Root terminal/original1800; API ready alone is insufficient."""
import pg5478_current_genuine_terminal as previous
import pg5644_current_admission_image as admission

TERM='pg5646-current-genuine-terminal-v1'


def bind(raw):
    raw=admission.bind(previous.bind(raw))
    for before,after in((previous.TERM,TERM),('pg5466-parent-watch-v1','pg5634-parent-watch-v1'),
      ('PG5430','PG5598'),('pg5430-manifest.sig','pg5598-manifest.sig')):raw=raw.replace(before,after)
    return raw


def payload(observed):return bind(previous.payload(observed))


if __name__=='__main__':raise SystemExit(admission.execute(TERM,payload(admission.live()),90))
