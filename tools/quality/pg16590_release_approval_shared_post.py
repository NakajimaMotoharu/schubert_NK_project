"""Frozen public claims all-Code/no-resource/no-crypto profile; unchanged qualified v3."""
import json
import g07_host_class_provenance_inputs as data
import pg16588_release_approval_original_eight_pt as original
import reviewed_whole_pure_source_post_v3 as shared
PROFILE=json.loads("{\"rawFolder\":\"PG16588-release-approval-original-eight-pt-v1\",\"rawSha256\":\"b2c1925427e837974d3097aeec60a7e40b87fa4c57ceb04d3ca2dd7e8d96e2a7\",\"postFolder\":\"PG16590-release-approval-shared-post-v1\",\"sources\":{\"dev/codex/schubert/nk/bootstrap/ReleaseApproval\":{\"path\":\"src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/ReleaseApproval.java\",\"sha256\":\"5c535995426d4e18179189259e8ef12d08d7ac2d1a6e068bb164454f5e8f0c2c\",\"module\":\"bootstrap\",\"closure\":[\"dev/codex/schubert/nk/bootstrap/ReleaseApproval\"],\"owner\":\"WBS-P018-02\"}},\"kind\":\"REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES\",\"originalTestsAlreadyCounted\":false}")
if __name__=='__main__':
    assert data.sha((data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v3.py').read_bytes())=='f41c2d98d5611a4519e2cc71de74998a6c24a491570242664767318e219e145f'
    shared.verify_profile(original,PROFILE)
