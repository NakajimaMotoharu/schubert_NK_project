"""Public parent eighteen-field projection from actual current full seal only."""
import inspect
import pg2372_current_resume_parent_projection as prior
from pg2446_question_current_observer import SOURCE

SLOT='pg2457-question-current-parent-projection-v1'


def payload(sha):
    return prior.payload(sha).replace('pg2368-current-resume-full-seal-v1','pg2456-question-current-full-seal-v1')


def main():
    raw=inspect.getsource(prior.previous.prior.prior.main).replace('pg2081-current-newrun-full-live-seal-v1','pg2456-question-current-full-seal-v1')
    ns={**prior.previous.prior.prior.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual current parent18 projection>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
