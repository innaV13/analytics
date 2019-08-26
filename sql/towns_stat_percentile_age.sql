DROP FUNCTION IF EXISTS towns_stat_percentile_age(bigint);
CREATE OR REPLACE FUNCTION towns_stat_percentile_age(_import_id bigint)
  RETURNS json AS $$
DECLARE
	_response json;
BEGIN

    IF not exists(select 1 from imports where id = _import_id) THEN
        RAISE EXCEPTION 'Import does not exists';
    END IF;
	-- получаем массив возрастов по каждому городу
	select json_agg(a) into _response
	from (
		select 
			town, 
			array_agg((EXTRACT(EPOCH FROM age(birth_date::timestamp)) / 60 / 60 / 24 / (365.25))::numeric(5, 2)) as years
		from citizens
		where import_id = _import_id
		group by town
	) a;

	return _response;

END;
$$ LANGUAGE 'plpgsql';
ALTER FUNCTION towns_stat_percentile_age(bigint) OWNER TO analytics;		