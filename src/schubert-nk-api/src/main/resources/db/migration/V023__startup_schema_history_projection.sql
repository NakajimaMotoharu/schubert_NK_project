-- NK-DAT-001/NK-OPS-001; DAT009/SYS002/OPS009; UI212/253; SS3313.3/3439.1;
-- SSC095/PG312/PT-DB-SCHEMA001..008. Fixed non-business metadata only; no direct history grant.
CREATE FUNCTION schubert_meta.startup_schema_history()
RETURNS TABLE (
    installed_rank integer,
    version text,
    type text,
    script text,
    checksum integer,
    success boolean
)
LANGUAGE SQL STABLE SECURITY DEFINER
SET search_path = pg_catalog, pg_temp
AS $function$
    SELECT history.installed_rank,
           history.version::text,
           history.type::text,
           history.script::text,
           history.checksum,
           history.success
      FROM schubert_meta.flyway_schema_history AS history
$function$;

ALTER FUNCTION schubert_meta.startup_schema_history() OWNER TO nk_owner;
REVOKE ALL ON FUNCTION schubert_meta.startup_schema_history() FROM PUBLIC;
GRANT USAGE ON SCHEMA schubert_meta TO schubert_app, schubert_web_session, schubert_batch;
GRANT EXECUTE ON FUNCTION schubert_meta.startup_schema_history()
    TO schubert_app, schubert_web_session, schubert_batch;
