"""Separate new action/remote/archive; qualified compiled namespace stays immutable."""
import pg1932_current_partial_reload_dispatch as prior

REMOTE='/home/ubuntu/pg1938-fixed-stage-v1'
ARCHIVE='pg1938-qualified-tools-v1.tar'
STAGE=prior.STAGE.replace('pg1932-fixed-stage-v1','pg1938-fixed-stage-v1').replace('pg1925-partial-reload-tools-v1.tar',ARCHIVE)


def source():
    raw=prior.source().replace('pg1932-','pg1938-')
    old="archive=P/(TOOLS+'.tar')"
    if raw.count(old)!=1:raise ValueError('one actual archive reservation boundary required')
    return raw.replace(old,'archive=P/'+repr(ARCHIVE))


def main():
    original=prior.prior
    ns={**original.prior.__dict__,'sources':original.sources,'TOOLS':original.TOOLS,'CLASS':original.CLASS,'TARGET':original.TARGET,'GUEST':original.GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(source(),'<actual new unique archive reload entry>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
