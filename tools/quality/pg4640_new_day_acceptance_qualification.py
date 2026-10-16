"""Affected new-day/full24/seal/Browser tools only; no Production regression or live login."""
import inspect
import pg4612_current_browser_chain_qualification as previous

SLOT='pg4640-new-day-acceptance-qualification-v1'


def main():
    raw=inspect.getsource(previous.main)
    raw=raw.replace("'pg4584_current_acceptance_test','pg4608_current_browser_chain_test'","'pg4584_current_acceptance_test','pg4608_current_browser_chain_test','pg4632_current_new_day_rows_oracle_test','pg4636_current_new_day_whole_seal_test'")
    raw=raw.replace("b'Ran 7 tests'","b'Ran 16 tests'").replace("'toolTests':7","'toolTests':16")
    raw=raw.replace("'pg4612_current_browser_chain_qualification.py']","'pg4612_current_browser_chain_qualification.py','pg4632_current_new_day_rows_oracle.py','pg4632_current_new_day_rows_oracle_test.py','pg4634_current_saved24_qualification.py','pg4636_current_new_day_whole_seal.py','pg4636_current_new_day_whole_seal_test.py','pg4640_new_day_acceptance_qualification.py']")
    ns={**vars(previous),'SLOT':SLOT}
    exec(compile(raw,'<all affected16 same-day/new-day/raw/seal/Browser qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
