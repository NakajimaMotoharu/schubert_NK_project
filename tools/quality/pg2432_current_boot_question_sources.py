"""BUG1239: complete current boot and actual basename contracts in a new graph."""
from pyflakes.api import check
import pg2412_question_unused_sources as prior

CURRENT,CURRENT_BOM,BEFORE,production=prior.CURRENT,prior.CURRENT_BOM,prior.BEFORE,prior.production
BOOT='b2d6f605-61cf-425f-8fbd-12d606f6ee66'
TOOLS='pg2432-current-boot-question-tools-v1'
SAVE='pg2436-current-boot-question-placement-v1'
ARCHIVE='pg2434-current-boot-question-release-v1.tar'
REMOTE='/home/ubuntu/pg2434-current-boot-question-input-v1'


def bind(raw):
    for a,b in [('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),
                ('3d69f5af6bac46b1a5407591c4a79a0d',BOOT.replace('-','')),
                ('pg2414-current-normal-release-v1.tar',ARCHIVE),
                ('pg2412-current-normal-unused-tools-v1',TOOLS),
                (prior.ARCHIVE,ARCHIVE),(prior.TOOLS,TOOLS),(prior.SAVE,SAVE),(prior.REMOTE,REMOTE),
                ('pg2412','pg2432'),('Pg2412','Pg2432'),('PG2412','PG2432'),
                ('pg2414','pg2434'),('PG2414','PG2434'),
                ('pg2416','pg2436'),('PG2416','PG2436')]:
        raw=raw.replace(a,b)
    return raw


def sources(bom,before=BEFORE):
    values={bind(n):bind(s) for n,s in prior.sources(bom,before).items()}
    for name,body in values.items():
        if '3d69f5af' in body or 'current-normal-unused-tools-v1' in body or 'current-normal-release-v1.tar' in body:
            raise ValueError('all current boot and real names must bind before freeze')
        if name.endswith('.py'):
            context="BUNDLE_HASH='pending-real-bundle'\n" if name in {'pg2432_native_refs.py','pg2432_input_preflight.py'} else ''
            if check(context+body,'<whole current boot '+name+'>'):
                raise ValueError('all current whole graph globals required')
            compile(body,'<bound current boot graph>','exec')
    return values


if __name__=='__main__':raise SystemExit('source factory only')
