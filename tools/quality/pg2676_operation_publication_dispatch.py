"""New-only finite publication; no Unit exchange/reload or business start."""
import json
import pg2534_strict_normal_publication_dispatch as previous
from pg2674_operation_publication_sources import sources,TOOLS,CLASS,candidate_bom,bind,BEFORE,CURRENT,production
from pg2675_operation_publication_compile import TARGET
from pg1446_current_cold_stage import W

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2676-operation-publication-stage-v1'


def stage(bom):return bind(previous.stage(bom),bom).replace(previous.REMOTE,REMOTE)


def source(bom):
    raw=bind(previous.source(bom),bom)
    for a,b in [('pg2533-frozen','pg2675-frozen'),('pg2534-','pg2676-'),
      ('pg2530-strict-candidate-ro-post-v1','pg2672-operation-ro-post-v1'),
      ('pg2516-current-strict-candidate-tools-v1','pg2658-operation-unused-tools-v1')]:raw=raw.replace(a,b)
    old="['git','diff','--name-only',CANDIDATE,'--','src','pom.xml']"
    if raw.count(old)!=1:raise ValueError('one complete selected source boundary required')
    raw=raw.replace(old,"['git','diff','--name-only','2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0','HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']")
    compile(raw,'<new operation finite publication dispatch>','exec');return raw


def main():
    bom=candidate_bom();post=json.loads((W/'pg2672-operation-ro-post-v1/manifest.safe.json').read_bytes())
    if type(post.get('actualExit'))is not int or post['actualExit']!=0 or post['guest']['candidateHostReadonlyVerified']is not True:raise ValueError('actual new candidate independent RO required')
    engine=previous.previous.prior.prior
    ns={**engine.__dict__,'__file__':__file__,'TARGET':TARGET,'TOOLS':TOOLS,'CLASS':CLASS,'GUEST':GUEST,'REMOTE':REMOTE,
      'STAGE':stage(bom),'sources':sources,'CANDIDATE':production(),'OLD':CURRENT,'BOM':bom,'BEFORE':BEFORE}
    exec(compile(source(bom),'<new resource finite publication entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
