"""Save both complete images before classifying; no candidate admission acceptance."""
import hashlib
from pyflakes.api import check
import pg4438_failed_current_canonical_view as previous
from pg4260_stable_admission_image import execute

SLOT = 'pg4440-failed-full-image-diagnosis-v1'


def payload():
    raw = previous.payload()
    if hashlib.sha256(raw.encode()).hexdigest() != '31c1341f3d5ed06edc5e87c4182ed2aaa3f93b11794f98de56967fc1d0446cb9':
        raise ValueError('exact original failed canonical reader first')
    raw = raw.replace(previous.SLOT, SLOT)
    marker = 'full_first,journal_first=canonical_image(post2);full_second,journal_second=canonical_image(snapshot())\n require(full_first==full_second and journal_first==journal_second)'
    if raw.count(marker) != 1: raise ValueError('one original two-image gate')
    replacement = """full_first,journal_first=canonical_image(post2)
 first_image_sha=save_private('canonical-first11.private.json',full_first)
 first_journal_sha=save_private('journal-first-raw.private.json',{'hex':journal_first.hex()})
 full_second,journal_second=canonical_image(snapshot())
 second_image_sha=save_private('canonical-second11.private.json',full_second)
 second_journal_sha=save_private('journal-second-raw.private.json',{'hex':journal_second.hex()})
 differences=[key for key in full_first if full_first[key]!=full_second[key]]
 diagnosis={'allFieldDifferences':differences,'allFullValuesEqual':full_first==full_second,
  'rawJournalEqual':journal_first==journal_second,'fullJournalValuesEqual':journal_contract['project'](journal_first)==journal_contract['project'](journal_second),
  'firstFullSha256':first_image_sha,'secondFullSha256':second_image_sha,'firstJournalSha256':first_journal_sha,'secondJournalSha256':second_journal_sha,
  'canonicalAdmissionAccepted':False,'allFieldsRetained':True,'oldParentNormal':False}
 diagnosis_sha=save_private('diagnosis.private.json',diagnosis)"""
    raw = raw.replace(marker, replacement, 1)
    final = "(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))"
    if raw.count(final) != 1: raise ValueError('one complete diagnostic receipt')
    raw = raw.replace(final, "value.update(canonicalAdmissionAccepted=False,diagnosis=diagnosis,diagnosisSha256=diagnosis_sha)\n" + final, 1)
    if check(raw, '<full images saved before independent diagnosis>'): raise ValueError('all emitted static0')
    return raw


def main():
    previous.previous.authenticate_host()
    return execute(SLOT, payload(), 220)


if __name__ == '__main__':
    raise SystemExit(main())
