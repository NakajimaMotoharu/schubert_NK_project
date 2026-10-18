"""Current qualified10 points plus captured normal20 pair; oldsource data never credited."""
import inspect
import pg4830_new_current_bootstrap_catalog as template
import pg5108_corrected_bootstrap_post as post
import pg5070_current_native_catalog as previous

SLOT = 'pg5110-corrected-bootstrap-catalog-v1'


def prerequisites():
    raw = inspect.getsource(template.prerequisites).replace("result['nativePhysicalFiles']==72", "result['nativePhysicalFiles']==88")
    ns = {**vars(template), 'post': post, 'previous': previous}
    exec(compile(raw, '<actual current captured20/native88 only>', 'exec'), ns)
    return ns['prerequisites']()


def payload():
    raw = inspect.getsource(template.payload).replace("'currentPhysicalNative':72", "'currentPhysicalNative':88")
    ns = {**vars(template), 'post': post, 'previous': previous, 'prerequisites': prerequisites}
    exec(compile(raw, '<current10 plus new2 exact catalog>', 'exec'), ns)
    return ns['payload']()


if __name__ == '__main__':
    raise SystemExit(post.role.before.admission.execute(SLOT, payload(), 60))
