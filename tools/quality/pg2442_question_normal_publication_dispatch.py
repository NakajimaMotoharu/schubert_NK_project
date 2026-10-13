"""New-only finite publication, preserving the actual normal Unit without reload."""
import pg2172_normal_publication_dispatch as prior
from pg2440_question_normal_publication_sources import sources,TOOLS,CLASS,BOM,BEFORE,CURRENT,BOOT,production
from pg2441_question_normal_publication_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2442-question-publication-stage-v1'
STAGE=prior.STAGE.replace(prior.REMOTE,REMOTE).replace(prior.TOOLS,TOOLS).replace('0.1.0-PG1846','0.1.0-PG2126').replace('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT)


def source():
    raw=prior.source()
    for a,b in [('pg2171-frozen','pg2441-frozen'),
                ('pg2168-normal-candidate-ro-post-v1','pg2426-question-candidate-ro-post-v1'),
                ('pg2126-candidate-build','pg2428-candidate-build'),
                ('pg2144-current-normal-unused-tools-v1','pg2432-current-boot-question-tools-v1'),
                ('pg2170','pg2440'),('Pg2170','Pg2440'),('PG2170','PG2440'),
                ('pg2172-','pg2442-'),('0.1.0-PG1846','0.1.0-PG2126')]:raw=raw.replace(a,b)
    compile(raw,'<actual finite publication new-only transport>','exec')
    return raw


def main():
    post=prior.prior.json.loads((prior.prior.W/'pg2426-question-candidate-ro-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['guest']['candidateHostReadonlyVerified']is not True:
        raise ValueError('actual new candidate independent hostRO post required')
    ns={**prior.prior.__dict__,'__file__':__file__,'TARGET':TARGET,'TOOLS':TOOLS,'CLASS':CLASS,
        'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,'CANDIDATE':production(),
        'OLD':CURRENT,'BOM':BOM,'BEFORE':BEFORE}
    exec(compile(source(),'<current finite publication new-only entry>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
