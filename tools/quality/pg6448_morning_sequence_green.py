"""Same23 pure normal contracts after one owner-list preallocation correction."""
import json
import subprocess
import pg6440_morning_diagnostic_green as prior

ROOT, W, BASE, sha, MAIN = prior.ROOT, prior.W, prior.BASE, prior.sha, prior.MAIN
OLD = '5aa08a26ef867810ddf73349e09a13c6520341b1'
inventory = prior.inventory


def guard_source(source):
    p = BASE/'PG6442-morning-diagnostic-qualification-v1/manifest.json'; q = json.loads(p.read_bytes())
    m = W/'pg6442-morning-diagnostic-qualification-v1/manifest.safe.json'
    if sha(p) != '0a1a830e54043d67f1ace8abb61aedc008eaa3431517719ecabcd8589400f3ff' or q['actualExit'] != 0 or q['source'] != OLD or (q['tests'], q['suites'], q['physicalMain']) != (23, 10, 1667) or sha(m) != q['privateManifestSha256']:
        raise ValueError('original23 all-source/Jar/XML qualification first')
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [MAIN]:
        raise ValueError('one Main capacity only; all independent Test bytes preserved')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing gates/Current unchanged')
    before = subprocess.check_output(['git', 'show', OLD+':'+MAIN], cwd=ROOT)
    after = subprocess.check_output(['git', 'show', source+':'+MAIN], cwd=ROOT)
    if before.count(b'var started = new ArrayList<T>();') != 1 or after != before.replace(b'var started = new ArrayList<T>();', b'var started = new ArrayList<T>(2);'):
        raise ValueError('exact fixed-two preallocation only, no diagnostic or protocol drift')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed localized PG first')
    guard_source('HEAD'); scope = prior.definitions()
    scope['SLOT'] = 'pg6448-morning-sequence-green-v1'
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
