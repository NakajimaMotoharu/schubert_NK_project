"""New-only three-file stage after BUG1342. Old4176 tools and failed proof remain unchanged."""
import inspect
import pg4176_partial_coordinator as previous

SLOT='pg4182-bounded-pool-tools-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+SLOT


def main():
    ns={**vars(previous),'SLOT':SLOT,'GUEST':GUEST}
    for f in [previous.stage_payload,previous.main]:
        exec(compile(inspect.getsource(f),'<bounded pool stage/proof>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
