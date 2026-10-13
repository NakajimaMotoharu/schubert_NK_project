"""BUG1214 new-only actual stage and main current release bound together."""
import pg2154_normal_candidate_ro_dispatch as prior

REMOTE='/home/ubuntu/pg2156-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/pg2156-normal-candidate-ro-tools-v1'
TOOLS='pg2156-normal-candidate-ro-tools-v1'


def source():
    raw=prior.source().replace('pg2154-','pg2156-')
    raw=raw.replace("archive=P/(TOOLS+'.tar')","archive=P/(TOOLS+'-pg2156.tar')")
    raw=raw.replace("GUEST+' && mkdir -m700 '","GUEST+' && mkdir -m700 '")
    return raw


STAGE=prior.STAGE.replace('0.1.0-PG1638','0.1.0-PG1846').replace('pg2154-fixed-stage-v1','pg2156-fixed-stage-v1').replace(prior.TOOLS,TOOLS).replace(TOOLS+'.tar',TOOLS+'-pg2156.tar')


def main():
    # Keep the already qualified frozen graph bytes and internal root names.
    # Deploy to its original internal root (never extracted by rejected oldstage).
    ns={**prior.prior.__dict__,'__file__':__file__,'TARGET':prior.TARGET,'TOOLS':prior.TOOLS,'CLASS':prior.CLASS,'GUEST':prior.GUEST,'REMOTE':REMOTE,'STAGE':STAGE.replace(TOOLS,prior.TOOLS),'sources':prior.sources,'CANDIDATE':prior.production(),'OLD':prior.CURRENT,'BEFORE':prior.BEFORE}
    exec(compile(source(),'<new-only fixed current RO stage>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
