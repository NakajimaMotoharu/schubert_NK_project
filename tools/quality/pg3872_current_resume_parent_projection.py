"""Actual parent18 projection before completed-resume owned stop."""
import inspect
import pg3818_hygiene_parent_projection as previous
import pg3870_current_resume_composite as composite
from pg3858_current_resume_acceptance import SOURCE,BOM

SLOT='pg3872-current-resume-parent-projection-v1'


def payload(sha,bom=None):
    if bom is not None and bom!=BOM:raise ValueError('exact signed current BOM required')
    return previous.payload(sha,BOM).replace(previous.composite.SLOT,composite.SLOT)


def main():
    raw=inspect.getsource(previous.previous.main).replace('pg2704-operation-current-full-seal-v1',composite.SLOT)
    values={**previous.previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current completed-resume parent18>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
