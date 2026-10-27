"""Metadata negatives for42 historical reasons and two new source-only catch reviews."""
import pg11580_batch_session_source_review as stage

if __name__=='__main__':
    stage.PRIMARY_SHA='198461923534abf92c0bb71cecb4c83bc98f5dd3f0b5228c67f95ca1c24dcadc'
    stage.post()
