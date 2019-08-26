from app import app,db
from flask import request
from flask import jsonify
from app.schemas import CitizenSchema, ImportSchema, ChangeCitizenSchema
from app.models import Imports, Citizens
from marshmallow import ValidationError
from sqlalchemy import func
import numpy as np
from sqlalchemy.exc import IntegrityError

import_schema = ImportSchema()
citizen_schema = CitizenSchema()
change_citizen_schema = ChangeCitizenSchema()

@app.route('/imports', methods=['POST'])
def imports():
	try:
		content = request.get_json()
		# Валидация
		import_obj = import_schema.load(content)
		# Сохраняем import и получаем import_id
		new_import = Imports()
		db.session.add(new_import)
		db.session.flush()
		db.session.refresh(new_import)

		# Сохраняем каждого горожанина
		for c in import_obj['citizens']:
			citizen = Citizens(**c)
			citizen.import_id = new_import.id
			db.session.add(citizen)
		db.session.commit()
		return success_response(dict(import_id=new_import.id)), 201
	except ValidationError as e:
		return jsonify(error=e.messages), 400
	except IntegrityError as e:
		return failed_response(e)
	except Exception as e:
		return failed_response('Something went wrong')

@app.route('/imports/<import_id>/citizens/<citizen_id>', methods=['PATCH'])
def change_citizen(import_id, citizen_id):
	try:
		import_id, citizen_id = int(import_id), int(citizen_id)
		content = request.get_json()
		citizen = Citizens.query.filter_by(citizen_id=citizen_id, import_id=import_id).first()
		if not citizen:
			return failed_response('Citizen not found')

		#Валидация
		change_citizen_obj = change_citizen_schema.load(content)
		if change_citizen_obj.get('relatives',None) is not None:
			# Убираем дубли родственников, если есть
			change_citizen_obj['relatives'] = list(set(change_citizen_obj['relatives']))
			old_rel = Citizens.query.filter_by(citizen_id=citizen_id, import_id=import_id).with_entities(Citizens.relatives).scalar()
			if old_rel != change_citizen_obj['relatives']:

				# Проверяем, что все родственники - существуюшие горожане
				res = db.session.query(func.count(Citizens.citizen_id))\
					.filter(Citizens.import_id==import_id)\
					.filter(Citizens.citizen_id.in_(change_citizen_obj['relatives']))\
					.scalar()

				if res != len(change_citizen_obj['relatives']):
					raise ValidationError('Some of relatives does not exists')

				# Определяем горожан, для доторых дополнительно нужно обновить родственников
				rel_to_del = list(set(old_rel) - set(change_citizen_obj['relatives']))
				rel_to_add = list(set(change_citizen_obj['relatives']) - set(old_rel))

				# Обновляем
				if rel_to_del:
					db.session.execute(
						"update citizens set relatives = array_remove(relatives,:citizen_id) where import_id = :import_id and citizen_id = any(:rel_to_del)",
						{"import_id": import_id,"citizen_id":int(citizen_id), "rel_to_del": rel_to_del}
					)
				if rel_to_add:
					db.session.execute(
						"update citizens set relatives = array_append(relatives,:citizen_id) where import_id = :import_id and citizen_id = any(:rel_to_add)",
						{"import_id": import_id, "citizen_id": int(citizen_id), "rel_to_add": rel_to_add}
					)

		# Обновляем
		Citizens.query.filter_by(citizen_id=citizen_id, import_id=import_id).update(change_citizen_obj)
		db.session.commit()
	except ValidationError as e:
		return jsonify(error=e.messages), 400
	except Exception as e:
		return failed_response(e)
	return success_response(citizen_schema.dump(Citizens.query.filter_by(citizen_id=citizen_id, import_id=import_id).first())), 200

@app.route('/imports/<import_id>/citizens', methods=['GET'])
def get_citizens(import_id):
	res = Citizens.query.filter_by(import_id=int(import_id)).all()
	if not res:
		return failed_response('Import id does not exists')
	return success_response(citizen_schema.dump(res, many=True))

@app.route('/imports/<import_id>/citizens/birthdays', methods=['GET'])
def citizens_birthdays(import_id):
	try:
		res = db.session.query(func.public.citizens_birthdays(int(import_id))).scalar()
	except Exception as e:
		return failed_response(e)
	return success_response(res['data'])

@app.route('/imports/<import_id>/towns/stat/percentile/age', methods=['GET'])
def towns_stat_percentile_age(import_id):
	try:
		# Получаем массив из возрастов жителей для каждого города
		res = db.session.query(func.public.towns_stat_percentile_age(int(import_id))).scalar()
		for r in res:
			r['p50'], r['p75'], r['p99'] = list(map(lambda x:round(x,2),np.percentile(r['years'],[50,75,99],interpolation='linear')))
			del r['years']
	except Exception as e:
		return failed_response(e)
	return success_response(res)


def success_response(data):
	return jsonify({"data":data})

def failed_response(error):
	return jsonify({"error":str(error).split('\n')[0]}), 400



