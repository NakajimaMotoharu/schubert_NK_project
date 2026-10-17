"""Current04bb all24 raw-first SQL capture and independent same-day query oracle."""
import inspect
import pg4756_new_current_same_day_rows as previous
import pg4900_current_admission_image as admission
import pg4902_current_genuine_terminal as terminal

SLOT='pg4904-current-same-day-all24-v1'
key_source=previous.key_source


def payload(observed,before_hash):
    ns={**vars(previous),'admission':admission,'terminal':terminal,'SLOT':SLOT,'key_source':key_source}
    exec(compile(inspect.getsource(previous.payload),'<all24/current04bb actual same-day oracle>','exec'),ns)
    return ns['payload'](observed,before_hash)


def main():
    ns={**vars(previous),'admission':admission,'terminal':terminal,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<current same-cohort terminal before all24>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
