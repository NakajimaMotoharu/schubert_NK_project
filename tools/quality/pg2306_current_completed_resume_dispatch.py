"""Exact current staged preparation only; no business start or Root replay."""
import pg1983_fresh_completed_resume_dispatch as template
from pg2304_current_completed_resume_sources import bind,sources,TOOLS,CLASS,SOURCE,BOM
from pg2305_current_completed_resume_compile import TARGET

REMOTE='/home/ubuntu/pg2306-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(template.STAGE).replace('pg1983','pg2306')


def source():
    raw=bind(template.source()).replace('pg1983','pg2306').replace('pg1982-frozen','pg2305-frozen')
    old="    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',CANDIDATE,'--','src','pom.xml']):raise ValueError('fixed clean candidate/operator required')"
    new="""    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean operator required')
    changed=subprocess.check_output(['git','diff','--name-only',CANDIDATE,'--','src','pom.xml'],text=True).splitlines()
    if any('/src/main/'in name or name.endswith('pom.xml')for name in changed):raise ValueError('unchanged current Main required')"""
    if raw.count(old)!=1:raise ValueError('one current source guard required')
    raw=raw.replace(old,new)
    raw=raw.replace(" or fixed['candidateSource']!=CANDIDATE",'').replace("or fixed['candidateSource']!=CANDIDATE",'')
    old="""    generated=sources();bundle=(W/'pg1860-warning-unused-tools-v1/bundle.safe.json').read_bytes()
    generated['pg2304_native_refs.py']='BUNDLE_HASH='+repr(hashlib.sha256(bundle).hexdigest())+'\\n'+generated['pg2304_native_refs.py']"""
    if raw.count(old)!=1:raise ValueError('one historical unused bundle injection boundary required')
    raw=raw.replace(old,'    generated=sources()')
    compile(raw,'<actual current completed resume dispatch>','exec')
    return raw


def main():
    base=template.prior.prior.prior.prior
    namespace={**base.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'CANDIDATE':SOURCE,'BOM':BOM}
    exec(compile(source(),'<current completed resume entry>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
