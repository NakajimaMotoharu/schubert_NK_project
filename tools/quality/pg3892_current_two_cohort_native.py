"""Two actual same7fff cohorts only, all1643 physical CRC and eighteen latest streams."""
import pg3632_current_browser_native_qualified as previous
import pg3832_hygiene_native_qualified as current
from pg3798_hygiene_current_observer import SOURCE
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate


def server():
    raw=previous.server()
    for old,new in [('PG3632','PG3892'),('PG3412','PG3734'),('qualified3412Tests','qualified3734Tests'),('3712','3714'),(previous.SOURCE,SOURCE)]:raw=raw.replace(old,new)
    compile(raw,'<current3714 two same-source cohorts CRC/session>','exec');return raw


def source():
    raw=previous.source()
    for old,new in [('pg3632-current-browser-native-qualified-v1','pg3892-current-two-cohort-native-v1'),('pg3630-current-browser-native-catalog-v1','pg3890-current-resume-native-catalog-v1'),('pg3414-outbox-full-qualified-v1','pg3738-hygiene-whole-qualified-v1'),('PG3632','PG3892'),('pg3532-outbox-current-native-qualified-v3','pg3832-hygiene-native-qualified-v1'),('pg3530-outbox-current-native-catalog-v1','pg3830-hygiene-native-catalog-v1')]:raw=raw.replace(old,new)
    compile(raw,'<same7fff first cohort immutable cache plus new eligible cohort>','exec');return raw


def main():
    values={**previous.transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':current.qualify_snapshot}
    exec(compile(source(),'<current two-cohort native qualification>','exec'),values)
    with management_gate(P/'current-management-critical.lock'):return values['main']()


if __name__=='__main__':raise SystemExit(main())
