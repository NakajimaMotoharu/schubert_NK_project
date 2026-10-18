"""One new sameRoot296 Browser run with independently captured guest-clock window, no Root replay."""
import inspect
import pg5488_current_same_owner_browser as previous
import pg5522_guest_clock_browser_ready as ready

admission=previous.admission
SOURCE=admission.SOURCE
SLOT='pg5524-guest-clock-same-owner-browser-v1'
owned_socks=previous.owned_socks
receipt=previous.receipt
guard=previous.guard


def entry_source():
    template=previous.previous.previous.previous.previous
    raw=inspect.getsource(template.main)
    changes={'shared=ready.previous.previous.previous':'shared=ready.shared',
        'previous.previous.owned_socks()':'owned_socks()',
        'tools/quality/pg3136_browser_rows_oracle.py':'tools/quality/pg5520_guest_clock_contract.py'}
    for before,after in changes.items():
        expected=2 if before=='previous.previous.owned_socks()'else 1
        if raw.count(before)!=expected:raise ValueError('exact before/post Browser driver dependency '+before)
        raw=raw.replace(before,after)
    marker="    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));"
    if raw.count(marker)!=1:raise ValueError('one new truthful result metadata boundary')
    addition="    value.update(clockDomain='guest-postgresql-realtime',guestClockQualified=len(codes)==2 and not any(codes),previousFailedRunPreserved='pg5488-current-same-owner-browser-v1',rootReplayed=False)\n"
    return raw.replace(marker,addition+marker,1)


def main():
    admission.authenticate_host();template=previous.previous.previous.previous.previous
    ns={**vars(template),'SLOT':SLOT,'SOURCE':SOURCE,'ready':ready,'guard':guard,'owned_socks':owned_socks}
    exec(compile(entry_source(),'<new-only coherent guest-clock Browser cohort>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
