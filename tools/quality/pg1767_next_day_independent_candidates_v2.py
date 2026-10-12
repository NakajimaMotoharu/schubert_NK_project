"""Fresh BUG1164 fixed emitted namespace; previous failed slot immutable."""
import inspect
import pg1766_next_day_independent_candidates as prior


def payload():
    raw=prior.payload().replace('import datetime,json\n','import datetime,json\nUTC=datetime.timezone.utc\n',1)
    raw=raw.replace('pg1766-next-day-independent-candidates-v1','pg1767-next-day-independent-candidates-v2')
    from pyflakes.api import check
    if check(raw,'<actual independent selector namespace>'):raise ValueError('undefined emitted dependency refused')
    compile(raw,'<actual independent selector namespace>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1766-next-day-independent-candidates-v1','pg1767-next-day-independent-candidates-v2')
    ns={**prior.__dict__,'payload':payload};exec(compile(raw,'<new-only selector transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
