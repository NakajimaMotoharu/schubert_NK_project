"""New source actual nine latest streams and full3637 all1643 Main CRC/session qualification."""
import json
import subprocess
import pg2384_current_resume_native_qualification as prior
from pg1446_current_cold_stage import W
from pg2446_question_current_observer import SOURCE
from pg2404_question_jdbc_full_six import validate


def qualify_snapshot():
    v=json.loads((W/'pg2405-question-jdbc-full-qualified-v1/manifest.safe.json').read_bytes())
    if v['actualExit']!=0:raise ValueError('actual new whole3637 qualification required')
    f=v['result']
    if not(f['productionSource']==SOURCE and f['tests']==3637 and f['suites']==540 and f['mainClasses']==1643 and f['FESFlakyNotRun']==0 and f['staticSixModules']==0):
        raise ValueError('new current full3637/540/1643/static6 required')
    validate(f['sourceSnapshot'])
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',f['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):
        raise ValueError('fixed complete current Main and test inputs required')


def server():
    raw=prior.server().replace('PG2384','PG2468').replace('PG2300','PG2404').replace('qualified2300Tests','qualified2404Tests').replace('3635','3637').replace(prior.SOURCE,SOURCE)
    compile(raw,'<new current nine latest full3637 server>','exec');return raw


def source():
    raw=prior.source()
    for a,b in [('pg2382-current-resume-native-catalog-v1','pg2466-question-current-native-catalog-v1'),
                ('pg2384-current-resume-native-qualified-v1','pg2468-question-current-native-qualified-v1'),
                ('PG2384','PG2468'),('pg2301-jdbc-host-integration-qualified-v1','pg2405-question-jdbc-full-qualified-v1')]:raw=raw.replace(a,b)
    compile(raw,'<new current native CRC/session transport>','exec');return raw


def entry():
    ns={**prior.previous.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<new current all Main/native qualification>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
