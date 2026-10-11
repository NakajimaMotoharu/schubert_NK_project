"""Current failed managed role pair before mutation; exact private Ref and full originals."""
import pg1367_bootstrap_failed_ref_pair_proof as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    raw=previous.payload(seals)
    changes=(
        ('Pg1362BootstrapExisting','Pg1374BootstrapRolePreparation'),
        ('pg1362-bootstrap-tools-v3','pg1374-bootstrap-role-tools-v2'),
        ('pg1362_bootstrap_existing.py','pg1374_bootstrap_role_refs.py'),
        ('pg1362-bootstrap-verify-v3','pg1374-bootstrap-role-prepare-v1'),
        ("b'verify'","b'prepare'"),('Existing\\x00verify\\x00','Preparation\\x00prepare\\x00'),
        ("'refs-prepare.private.log'","'refs.private.log'"),
        ('pg1367-bootstrap-failed-ref-pair-v1','pg1381-role-failed-ref-pair-v1'),
        ('PG1367-bootstrap-failed-ref-pair-v1','PG1381-role-failed-ref-pair-v1'))
    # Candidate has the renamed class string; operation argument changes independently.
    raw=raw.replace('Pg1374BootstrapRolePreparation\\x00verify\\x00','Pg1374BootstrapRolePreparation\\x00prepare\\x00')
    for old,new in changes:
        raw=raw.replace(old,new)
    raw=raw.replace('Pg1374BootstrapRolePreparation\\x00verify\\x00','Pg1374BootstrapRolePreparation\\x00prepare\\x00')
    compile(raw,'<current exact role helper pair>','exec');return raw

def source():
    return previous.source().replace('pg1367-bootstrap-failed-ref-pair-v1','pg1381-role-failed-ref-pair-v1')

def main():
    env=dict(previous.previous.previous.previous.prior.prior.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(source(),'<current failed role pair proof>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
