"""Actual a2ecc Root terminal and original1800s, never API-ready-only success."""
import pg4902_current_genuine_terminal as previous
import pg5036_current_admission_image as admission

TERM = 'pg5038-current-genuine-terminal-v1'


def bind(raw):
    raw = admission.bind(previous.bind(raw))
    for a, b in [(previous.TERM, TERM), ('pg4890-parent-watch-v1', 'pg5018-parent-watch-v1'),
                 ('PG4860', 'PG4980'), ('pg4860-manifest.sig', 'pg4980-manifest.sig')]:
        raw = raw.replace(a, b)
    return raw


def payload(observed):
    return bind(previous.payload(observed))


if __name__ == '__main__':
    raise SystemExit(admission.execute(TERM, payload(admission.live()), 90))
