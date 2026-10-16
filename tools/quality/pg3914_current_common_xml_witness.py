"""Actual current3714 original XML witnesses, with unchanged independent Test bytes."""
import inspect
import pg3540_current_common_xml_witness as previous
from pg3798_hygiene_current_observer import SOURCE

SLOT='pg3914-current-common-xml-witness-v1'
PUBLIC=previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3914-current-common-xml-witness-v1'


def payload():
    raw=inspect.getsource(previous.payload)
    for old,new in [('pg3414-outbox-full-qualified-v1','pg3738-hygiene-whole-qualified-v1'),('3712','3714'),('PG3412','PG3734')]:raw=raw.replace(old,new)
    values={**previous.__dict__,'SOURCE':SOURCE}
    exec(compile(raw,'<actual current selected common XML witness factory>','exec'),values)
    return values['payload']()


def main():
    values={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'PUBLIC':PUBLIC,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<current original common XML witness transport>','exec'),values)
    return values['main']()


if __name__=='__main__':raise SystemExit(main())
