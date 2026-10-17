"""Genuine current guard/independent all24/whole full11/72 seal; no lifecycle mutations."""
import inspect
import pg4760_new_current_whole_seal as previous
import pg4900_current_admission_image as admission
import pg4902_current_genuine_terminal as terminal
import pg4904_current_same_day_rows as rows

SLOT='pg4906-current-whole-seal-v1'
replace_constant=previous.replace_constant


def payload(observed,before_hash):
    ns={**vars(previous),'admission':admission,'terminal':terminal,'rows':rows,'SLOT':SLOT}
    exec(compile(inspect.getsource(previous.payload),'<same-source full11/72 genuine whole seal>','exec'),ns)
    return ns['payload'](observed,before_hash)


def main():
    ns={**vars(previous),'admission':admission,'terminal':terminal,'rows':rows,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<current genuine/all24 required before seal>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
