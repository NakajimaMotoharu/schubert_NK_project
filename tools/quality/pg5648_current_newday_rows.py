"""Actual0ea all24 raw-first capture and independent same-day/query postconditions."""
import types
import pg4756_new_current_same_day_rows as previous
import pg5644_current_admission_image as admission
import pg5646_current_genuine_terminal as terminal

SLOT='pg5648-current-same-day-all24-v2'
key_source=previous.key_source


def payload(observed,before_hash):
    ns={**vars(previous),'admission':admission,'terminal':terminal,'SLOT':SLOT}
    return types.FunctionType(previous.payload.__code__,ns)(observed,before_hash)


def main():
    ns={**vars(previous),'admission':admission,'terminal':terminal,'SLOT':SLOT,'payload':payload}
    return types.FunctionType(previous.main.__code__,ns)()


if __name__=='__main__':raise SystemExit(main())
