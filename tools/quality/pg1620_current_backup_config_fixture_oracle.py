"""SS343 SSC150/160 literal fixture1 vs signed default59627, no inferred expected."""
import hashlib
import re

KEY='nk.api.storage.asset-manifest-entries'
def verify_fixture_api(archive,host,template,source_identity,archive_identity,expected_gid,signed_hashes):
    if any(type(v)is not bytes for v in [archive,host,template])or archive!=host or type(expected_gid)is not int or expected_gid<1 or type(signed_hashes)is not dict:raise ValueError('fixed fixture API source inputs refused')
    if source_identity!=(0,expected_gid,0o640)or archive_identity!=source_identity or hashlib.sha256(template).hexdigest()!=signed_hashes.get('config/templates/api.yml'):raise ValueError('signed template/fixture source identity refused')
    def view(raw,wanted):
        text=raw.decode('utf-8');result=[];count=0
        pattern=r'^\s*(?:"nk\.api\.storage\.asset-manifest-entries"|nk\.api\.storage\.asset-manifest-entries)\s*:\s*(?:"([0-9]+)"|([0-9]+))\s*$'
        for line in text.splitlines():
            if line.lstrip().startswith('#'):continue
            if KEY in line:
                m=re.fullmatch(pattern,line)
                if m is None or(m[1]or m[2])!=wanted:raise ValueError('independent literal Asset count refused')
                count+=1
            else:result.append(line)
        if count!=1:raise ValueError('unique Asset count property required')
        return result
    if view(host,'1')!=view(template,'59627'):raise ValueError('nonfixture API configuration changed')
    return 'SIGNED_TEMPLATE_WITH_ONLY_APPROVED_FIXTURE_ASSET_COUNT_1'
