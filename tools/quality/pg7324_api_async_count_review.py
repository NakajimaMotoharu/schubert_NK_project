"""Current API16 independent static/domain review, no runtime replay or acceptance transfer."""
import hashlib
import json
import subprocess
import pg7310_api_async_metric_review as review
import pg7318_api_async_count_six_compile as compilation

def classify(current):
    pmd=current['staticRaw']['pmd'];style=current['staticRaw']['checkstyle']
    review.require(pmd['actualExit']==4 and pmd['processingErrors']==0 and len(pmd['findings'])==2
      and style['actualExit']==0 and style['processingErrors']==0 and not style['findings'],
      'exact two raw PMD findings and zero processing/Checkstyle issues')
    expected={('statement','39'),('rows','43')};seen=set();rows=[]
    path='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/persistence/AsyncJobCountRepository.java'
    source=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=review.host.ROOT)
    review.require(hashlib.sha256(source).hexdigest()==current['sourceFiles'][path],
      'disposition tied to original executed repository bytes')
    text=source.decode()
    for finding in pmd['findings']:
        key=(finding.get('variable'),finding.get('beginline'))
        review.require(key in expected and key not in seen and finding.get('rule')=='CloseResource'
          and finding.get('class')=='AsyncJobCountRepository' and finding.get('method')=='read'
          and finding.get('package')=='dev.codex.schubert.nk.api.monitoring.persistence',
          'no generic CloseResource suppression or unclassified finding')
        variable=key[0];review.require('try ('+variable+') {' in text,
          'actual existing-variable try-with-resources owns resource')
        seen.add(key)
        rows.append(dict(raw=finding,classification='FALSE_POSITIVE',sourcePath=path,
          sourceSha256=current['sourceFiles'][path],reason='Java existing-variable try-with-resources closes acquired resource on all exits; original ASYNCDB001..008 verify reverse close/partial acquisition/SQL and close faults, no actual DB',
          ordinaryTestWitness='PG7314-api-async-count-host-v1',counterWitness='PG7316-api-async-count-post-v1',
          sourceOrRulesChanged=False,suppressionAdded=False))
    review.require(seen==expected,'both exact resource owners classified')
    return rows

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE
    review.OUT=review.host.BASE/'PG7324-api-async-count-review-v1'
    review.CURRENT_TESTS=16;review.CURRENT_SUITES=2;review.CURRENT_EXECUTABLE=4
    review.PHYSICAL_COUNT=1727;review.ADDED_PHYSICAL=58
    review.PREVIOUS_COUNT=65;review.INTRODUCED_COUNT=2
    review.STATIC_CLASSIFIER=classify
    review.PINS=dict(review.PINS)
    for key,path in {
      'currentApi':'PG7316-api-async-count-post-v1/manifest.json',
      'physical':'PG7320-api-async-count-six-post-v1/manifest.json',
      'trace':'PG7322-api-async-count-trace-v1/manifest.json',
      'previous':'PG7308-api-async-metric-trace-v1/manifest.json'}.items():
        review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    # Reuse the original twelve static guards only where their exact input bytes remain unchanged.
    contract=json.loads((review.host.BASE/review.PINS['contract'][0]).read_bytes())
    inputs={
      'tools/quality/harnesses/monitoring-api-jobs-pom.xml':contract['harness']['apiSha256'],
      'tools/quality/harnesses/monitoring-pom.xml':contract['harness']['knownBatchSha256'],
      'src/schubert-nk-api/pom.xml':contract['apiPom']['sha256'],
      contract['canonicalDdl']['path']:contract['canonicalDdl']['sha256']}
    for path,digest in inputs.items():
        blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=review.host.ROOT)
        review.require(hashlib.sha256(blob).hexdigest()==digest,'unchanged original contract input bytes, not historical test transfer')
    review.main()
