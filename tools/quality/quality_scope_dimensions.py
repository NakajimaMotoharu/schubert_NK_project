"""Pure manifest dimensions: cases, suites, source files and physical classes are distinct."""
from dataclasses import asdict, dataclass
import re


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def count(value, name, positive=False):
    require(type(value) is int and value >= (1 if positive else 0), name)
    return value


@dataclass(frozen=True)
class ScopeDimensions:
    source: str
    observed_cases: int
    suites: int
    whole_test_sources: int
    new_test_ids: int
    old_test_physical_unchanged: int
    new_test_physical: int
    main_physical_unchanged: int

    def public(self):
        return asdict(self)


def bind(plan, host, proof):
    """Validate modern selected-PT manifests; unsupported schemas fail, never infer counts."""
    source = plan['source']
    require(isinstance(source,str) and re.fullmatch('[0-9a-f]{40}',source) is not None,'source SHA')
    require(host['source'] == proof['source'] == source,'same source')
    require(all(type(row['actualExit']) is int and row['actualExit'] == 0 for row in (plan,host,proof)),'terminal success')
    cases = plan['cases']
    require(isinstance(cases,list) and len(cases) > 0,'nonempty cases')
    expected = [(row['className'],row['method']) for row in cases]
    require(all(all(isinstance(x,str) and x for x in pair) for pair in expected),'case labels')
    require(len(set(expected)) == len(expected),'unique cases')
    observed = host['cases']
    actual = [(row['classname'],row['name']) for row in observed]
    require(len(actual) == len(expected) and set(actual) == set(expected),'exact actual cases')
    require(all(row['nonPass'] == [] for row in observed),'no nonpass')
    sources = plan['wholeTestSourceHashes']
    require(isinstance(sources,dict) and bool(sources),'whole test sources')
    require(set(sources) == {row['path'] for row in cases},'whole source set')
    require(all(row['sourceSha256'] == sources[row['path']] and re.fullmatch('[0-9a-f]{64}',row['sourceSha256']) for row in cases),'case source hashes')
    n = count(plan['totalTests'],'planned cases',True)
    require(n == len(expected) == count(host['observedTestExecutions'],'host cases',True) == count(proof['observedTestExecutions'],'proof cases',True),'case dimensions')
    suites = count(proof['suites'],'suites',True)
    require(suites == len({pair[0] for pair in expected}),'suite dimensions')
    new = count(plan['newTests'],'new cases')
    require(new == count(proof['newTestIds'],'proof new cases') and new <= n,'new ID dimensions')
    require(count(plan['originalTests'],'old cases') + new == n,'planned old/new partition')
    require(host['oldExecUnion'] is False and plan['oldExecUnion'] is False and proof['oldExecUnion'] is False,'no old exec union')
    return ScopeDimensions(source,n,suites,len(sources),new,
        count(proof['oldTestPhysicalUnchanged'],'old physical'),
        count(proof['newTestPhysical'],'new physical'),
        count(proof['allMainClassesUnchanged'],'main physical',True))


def verify_qualification(dimensions, qualification):
    """Only like-for-like dimensions: never compare class count to Test source count."""
    fields = {
        'source': dimensions.source,
        'observedTestExecutions': dimensions.observed_cases,
        'suites': dimensions.suites,
        'newTestIds': dimensions.new_test_ids,
        'allMainClassesUnchanged': dimensions.main_physical_unchanged,
        'oldTestPhysicalUnchanged': dimensions.old_test_physical_unchanged,
        'newTestPhysical': dimensions.new_test_physical,
    }
    require(all(type(qualification[k]) is type(value) and qualification[k] == value for k,value in fields.items()),'qualification dimensions')
