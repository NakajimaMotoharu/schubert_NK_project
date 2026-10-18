"""Fresh current a2ecc stopped all24/187/86 baseline; no start or credential mutation."""
import inspect
import pg4818_new_current_bootstrap_before as template
import pg5066_current_owned_post as post
import pg5036_current_admission_image as admission

SLOT = 'pg5080-current-bootstrap-before-v1'
SOURCE, BOM = admission.SOURCE, admission.BOM
AFTER = '3943f5c32d2e7ddccf93917b9dd6480beb92fb3fd8fafddb55111d0f280ec9a4'


def payload():
    raw = inspect.getsource(template.payload)
    for old, new in [("manifest['nativePhysicalFiles']==70", "manifest['nativePhysicalFiles']==86"),
                     ('exact actual stopped all24/70/current source proof first',
                      'exact actual stopped all24/86/current source proof first'),
                     ("base / 'pg4778-new-current-owned-post-v1'", "base / 'pg5066-current-owned-post-v1'")]:
        if raw.count(old) != 1:
            raise ValueError('one current stopped enrichment boundary')
        raw = raw.replace(old, new, 1)
    ns = {**vars(template), 'SLOT': SLOT, 'SOURCE': SOURCE, 'BOM': BOM,
          'AFTER': AFTER, 'post': post, 'admission': admission}
    exec(compile(raw, '<current a2ecc stopped86 enriched baseline>', 'exec'), ns)
    return ns['payload']()


if __name__ == '__main__':
    raise SystemExit(admission.execute(SLOT, payload(), 120))
