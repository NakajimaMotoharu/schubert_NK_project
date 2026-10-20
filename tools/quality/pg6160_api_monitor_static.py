"""Strict compile/SpotBugs of close-only private monitors; no JUnit/VM/service actions."""
import inspect
from types import FunctionType
import xml.etree.ElementTree as ET
import pg6153_api_test_compile_preflight as profile

OLD='8f0ba4cb06467e5e1c9b25f8360bbc1db4d963ea'
CHANGED_MAIN={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'+n+'.java'
    for n in ('SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers','ApiMessagingRuntime')}
CHANGED=CHANGED_MAIN|{'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/ApiConsumerCloseOwnershipTest.java'}


def runner_source():
    raw=inspect.getsource(profile.main)
    replacements={
        " != {TEST}:":" != CHANGED:",
        "'pg6153-api-test-compile-preflight-v1'":"'pg6160-api-monitor-static-v1'",
        "'PG6153-api-test-compile-preflight-v1'":"'PG6160-api-monitor-static-v1'",
        "W/'pg6150-api-factory-close-selected-v1/source'":"W/'pg6154-api-factory-close-selected-v2/source'",
        "if len(main_paths) != 851 or any(sha(p) != sha(previous/p.relative_to(snapshot)) for p in main_paths):":
            "if len(main_paths) != 851 or {p.relative_to(snapshot).as_posix() for p in main_paths if sha(p) != sha(previous/p.relative_to(snapshot))} != CHANGED_MAIN:",
        "'-am', 'test-compile']":"'-am', 'test-compile', 'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']",
        "code = actual if actual else 0 if fixed and not reports and not jacoco else 1":
            "static_issues = {m: len(ET.parse(snapshot/('src/schubert-nk-'+m+'/target/spotbugsXml.xml')).getroot().findall('BugInstance')) if (snapshot/('src/schubert-nk-'+m+'/target/spotbugsXml.xml')).exists() else None for m in ('protocol','storage','bootstrap','api')}\n    code = actual if actual else 0 if fixed and not reports and not jacoco and all(v == 0 for v in static_issues.values()) else 1",
        "all851MainUnchanged=True, testsExecuted=0":"all851MainUnchanged=False, changedMainCount=4, staticIssues=static_issues, testsExecuted=0",
        "compileConfiguration='existing unchanged module -Xlint:all/-Werror and inherited Main type/null compiler; lifecycle ends at test-compile'":
            "compileConfiguration='unchanged four module format/type/null/Test-Xlint-Werror plus pinned SpotBugs; no test phase'"}
    for before,after in replacements.items():
        if raw.count(before)!=1:raise ValueError('one explicit static-only profile binding: '+before)
        raw=raw.replace(before,after,1)
    compile(raw,'<four private monitor strict static>','exec')
    return raw


def main():
    if profile.subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=profile.ROOT):
        raise ValueError('rules/build/Current unchanged, no exclusions or suppressions')
    scope={**vars(profile),'OLD':OLD,'CHANGED':CHANGED,'CHANGED_MAIN':CHANGED_MAIN,'ET':ET}
    exec(compile(runner_source(),'<strict private owner monitor static>','exec'),scope)
    return FunctionType(scope['main'].__code__,scope)()


if __name__=='__main__':raise SystemExit(main())
