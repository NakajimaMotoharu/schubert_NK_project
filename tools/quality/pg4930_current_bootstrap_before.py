"""Current04bb stopped full post, enriched for approved existing-ADMIN20 only."""
import inspect
import pg4818_new_current_bootstrap_before as previous
import pg4922_current_owned_post as post
import pg4900_current_admission_image as admission

SLOT='pg4930-current-bootstrap-before-v1'
SOURCE,BOM=admission.SOURCE,admission.BOM
AFTER='685ae63ba3c5f29d32a4362b1d49e6138adaaa82df4f329944600d952ca53740'


def payload():
    raw=inspect.getsource(previous.payload)
    for old,new in [("manifest['nativePhysicalFiles']==70","manifest['nativePhysicalFiles']==78"),
                    ('exact actual stopped all24/70/current source proof first','exact actual stopped all24/78/current source proof first'),
                    (previous.post.SLOT,post.SLOT)]:
        if raw.count(old)!=1:raise ValueError('one exact current stopped Bootstrap boundary')
        raw=raw.replace(old,new,1)
    ns={**vars(previous),'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'AFTER':AFTER,'post':post,'admission':admission}
    exec(compile(raw,'<current full24/32/187/78 enriched baseline>','exec'),ns)
    return ns['payload']()


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(),120))
