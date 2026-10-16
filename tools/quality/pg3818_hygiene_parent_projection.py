"""Read actual eighteen parent fields from genuine composite before any owned stop."""
import inspect
import pg2706_operation_current_parent_projection as previous
import pg3808_hygiene_acceptance as root
import pg3816_hygiene_browser_composite as composite
from pg3798_hygiene_current_observer import SOURCE,BOM

SLOT='pg3818-hygiene-parent-projection-v1'


def payload(sha,bom=None):
    if bom is not None and bom!=BOM:raise ValueError('exact signed current BOM required')
    return root.bind(previous.payload(sha,BOM)).replace(root.SEAL,composite.SLOT)


def main():
    raw=inspect.getsource(previous.main).replace('pg2704-operation-current-full-seal-v1',composite.SLOT)
    values={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current actual composite eighteen parent fields>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
