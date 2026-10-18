"""Actual296 all24 raw-first capture and independent newday/session/query postconditions."""
import types
import pg5040_current_newday_rows as previous
import pg5476_current_admission_image as admission
import pg5478_current_genuine_terminal as terminal

SLOT='pg5480-current-newday-all24-v1'
key_source=previous.key_source


def payload(observed,before_hash):
    ns={**vars(previous),'admission':admission,'terminal':terminal,'SLOT':SLOT}
    return types.FunctionType(previous.payload.__code__,ns)(observed,before_hash)


def main():
    ns={**vars(previous),'admission':admission,'terminal':terminal,'SLOT':SLOT,'payload':payload}
    return types.FunctionType(previous.main.__code__,ns)()


if __name__=='__main__':raise SystemExit(main())
