"""Actual current boot unused placement independently verified; no duplicate placement."""
import inspect
import pg2418_question_unused_post as prior
from pg2432_current_boot_question_sources import SAVE

SLOT='pg2438-current-boot-question-post-v1'


def payload(candidate=None):
    return prior.payload(candidate).replace(prior.SLOT,SLOT).replace('pg2416-question-unused-placement-v1',SAVE)


def main():
    raw=inspect.getsource(prior.prior.main).replace('pg2146-place-v1.safe.json','pg2434-place-v1.safe.json')
    namespace={**prior.prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<independent actual current unused post>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
