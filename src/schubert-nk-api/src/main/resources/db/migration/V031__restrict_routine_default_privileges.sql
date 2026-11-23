-- NK-DAT-001 / DAT-009 / UI212,241 / SS331 §3.2, SS343 §9.
-- SSC-479 / BUG-3721 / YKT-2921 / PT-DB-ACL031-001.
SET ROLE nk_owner;

-- PostgreSQL adds schema defaults to the database-wide defaults for each role.
ALTER DEFAULT PRIVILEGES FOR ROLE nk_owner
    REVOKE EXECUTE ON ROUTINES FROM PUBLIC;

RESET ROLE;
