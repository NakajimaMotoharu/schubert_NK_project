-- QA050/SSC171; NK-DAT-001/NK-WEB-002; SS314 section 10/331 section 9.2/343; RERUN002.
-- NULL is an unknown current API expiry, never an automatic deletion or authorization proof.
-- Existing known values, checks, leases, indexes and role/grants are retained unchanged.
ALTER TABLE schubert_web_session.pending_context_revocations
    ALTER COLUMN expires_at DROP NOT NULL;
