"""Current nine streams plus captured20 pair only; all78 prior files preserved."""
import inspect
import pg4830_new_current_bootstrap_catalog as template
import pg4938_current_bootstrap_post as post
import pg4924_current_native_catalog as previous

SLOT='pg4940-current-bootstrap-catalog-v1'


def prerequisites():
    raw=inspect.getsource(template.prerequisites).replace("result['nativePhysicalFiles']==72","result['nativePhysicalFiles']==80")
    ns={**vars(template),'post':post,'previous':previous}
    exec(compile(raw,'<actual current captured20 and all80 full post>','exec'),ns)
    return ns['prerequisites']()


def payload():
    raw=inspect.getsource(template.payload).replace("'currentPhysicalNative':72","'currentPhysicalNative':80")
    ns={**vars(template),'post':post,'previous':previous,'prerequisites':prerequisites}
    exec(compile(raw,'<current exact old10 plus new2 points>','exec'),ns)
    return ns['payload']()


if __name__=='__main__':raise SystemExit(post.role.before.admission.execute(SLOT,payload(),60))
