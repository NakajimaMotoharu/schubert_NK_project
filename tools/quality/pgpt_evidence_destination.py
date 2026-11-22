"""Select the evidence output tree for the formal collector and its child writers."""

import os
from pathlib import Path


CANDIDATE_ROOT_ENV = "NK_PGPT_CANDIDATE_EVIDENCE_ROOT"


def check_candidate_root(repo, path):
    absolute = path.absolute()
    if absolute.resolve() != absolute or absolute.is_relative_to(repo.resolve()):
        raise ValueError("candidate root must be outside the checkout and use a non-aliased path")
    return absolute


def evidence_output_root(repo):
    candidate = os.environ.get(CANDIDATE_ROOT_ENV)
    if candidate is None:
        return repo / "evidence/01_PT"
    path = check_candidate_root(repo, Path(candidate))
    if not path.is_dir():
        raise ValueError("candidate evidence directory was not reserved")
    return path
