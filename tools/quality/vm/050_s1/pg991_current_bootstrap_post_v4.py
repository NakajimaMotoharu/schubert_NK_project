"""New readonly v4 trace-qualified reauthentication, never Unit restart or fixture replay."""
import pg989_current_bootstrap_post as previous
def payload(proof,seals):
    raw=previous.payload(proof,seals).replace('pg989-bootstrap-post-v3','pg989-bootstrap-post-v4').replace('PG989-bootstrap-post-v3','PG989-bootstrap-post-v4')
    assert "'run':'PG989-bootstrap-post-v4'" in raw
    return raw
if __name__=='__main__':
    env=previous.base_namespace();env['payload']=payload
    raw=previous.base_source();raw=raw[raw.index('def main():'):raw.index("if __name__=='__main__':")]
    raw=raw.replace('pg989-bootstrap-post-v3','pg989-bootstrap-post-v4')
    exec(compile(raw,'<991 new immutable post v4>','exec'),env);env['main']()
