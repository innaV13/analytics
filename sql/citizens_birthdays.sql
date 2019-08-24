DROP FUNCTION IF EXISTS citizens_birthdays(bigint);
CREATE OR REPLACE FUNCTION citizens_birthdays(_import_id bigint)
  RETURNS json AS $$
DECLARE
	_response json;
BEGIN

	with data as (
		select c1.citizen_id, c2.citizen_id as b_c_id, date_part('month',c2.birth_date) as b_month
		from citizens c1
			join citizens c2 on c1.import_id = c2.import_id and c2.citizen_id = any(c1.relatives)
		where c1.import_id = _import_id
	), groupped as (
		select b_month, citizen_id, count(*) as presents
		from data
		group by b_month, citizen_id
		order by b_month, citizen_id
	), result as (
		select b_month,
			(select json_agg(a) from (
				select
					g2.citizen_id,
					g2.presents
				from groupped g2
				where g2.b_month = g1.b_month
			) a) as data
		from groupped g1
		group by b_month
	)
	select to_json(a) into _response
	from (
		select json_object_agg(a.a,coalesce(r1.data,'[]'::json)) as data
		from generate_series(1,12) a
			left join result r1 on r1.b_month = a.a
	) a;

	return _response;

END;
$$ LANGUAGE 'plpgsql';
ALTER FUNCTION citizens_birthdays(bigint) OWNER TO analytics;