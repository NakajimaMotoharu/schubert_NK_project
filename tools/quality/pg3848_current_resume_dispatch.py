"""New-only finite current resume preparation; never dispatch an external Root."""
import inspect
import pg3568_current_browser_resume_dispatch as previous
from pg3844_current_resume_sources import bind, sources, TOOLS, CLASS, SOURCE, BOM
from pg3846_current_resume_compile import TARGET

REMOTE='/home/ubuntu/pg3848-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(previous.STAGE)


def source():
    raw=bind(previous.source())
    compile(raw,'<current completed-resume finite dispatcher>','exec')
    compile(STAGE,'<current completed-resume immutable stage>','exec')
    return raw


def main():
    namespace={**previous.__dict__,'bind':bind,'sources':sources,'TOOLS':TOOLS,
        'CLASS':CLASS,'SOURCE':SOURCE,'BOM':BOM,'TARGET':TARGET,'REMOTE':REMOTE,
        'GUEST':GUEST,'STAGE':STAGE,'source':source}
    exec(compile(inspect.getsource(previous.main),'<new-only finite dispatcher entry>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
