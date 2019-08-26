import unittest, json
from app import db, app
from app.models import Imports
from sqlalchemy.sql.expression import func
import copy, datetime, json


with open('tests/citizens.json','r') as f:
    citizens = f.read()

citizens_data_set = json.loads(citizens)['citizens'][0:4]

class BaseTestCase(unittest.TestCase):

    def get_max_import_id(self):
        max = db.session.query(func.max(Imports.id)).scalar()
        return max if max else 0

    @classmethod
    def setUpClass(cls):
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://analytics:password@localhost/tests"
        app.config['TESTING'] = True
        app.config['PORT'] = 4000
        app.testing = True
        cls.app = app.test_client()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

class ImportsTestCase(BaseTestCase):

    # Success create
    def test_imports(self):
        current_max_import_id = self.get_max_import_id()
        response = self.app.post("/imports", data=citizens,content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data())
        self.assertTrue(data.get('data', None).get('import_id',None))
        db.session.commit()


    # Dublicate citizen_id
    def test_dublicates_ids(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set)
        for c in citizens_data:
            c['citizen_id'] = 1
            c['relatives'] = []

        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

    # Not valid citizen_id
    def test_not_valid_citizen_id(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set)
        not_valid_values = [-1, 1.5, 'srt']
        for i in range(0,len(citizens_data)):
            citizens_data[i]['citizen_id'] = not_valid_values[(3+i)%3]
            citizens_data[i]['relatives'] = []

        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
            content_type='application/json')

        self.assertEqual(response.status_code, 400)

        must_be_greater_error = 'Value must be greater than 0'
        not_valid_int = 'Not a valid integer.'
        errors = json.loads(response.get_data())['error']['citizens']
        self.assertTrue(errors['0']['citizen_id'] == [must_be_greater_error])
        self.assertTrue(errors['1']['citizen_id'] == errors['2']['citizen_id'] == [not_valid_int])
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

        # Check valid town,street,building
    def test_valid_str_fields(self):
        valid_values = ['1','a','qwe/$3']
        citizens_data = copy.deepcopy(citizens_data_set)
        for i in range(0,len(citizens_data)):
            citizens_data[i]['town'] = valid_values[(3+i)%3]
            citizens_data[i]['street'] = valid_values[(3+i)%3]
            citizens_data[i]['building'] = valid_values[(3+i)%3]
            citizens_data[i]['relatives'] = []

        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data())
        self.assertTrue(data.get('data').get('import_id',False))
        db.session.commit()

        # Check not valid town,street,building
    def test_not_valid_str_fields(self):
        current_max_import_id = self.get_max_import_id()
        not_valid_values = ['','*','a'*257]
        citizens_data = copy.deepcopy(citizens_data_set)
        for i in range(0,len(citizens_data)):
            citizens_data[i]['town'] = not_valid_values[(3+i)%3]
            citizens_data[i]['street'] = not_valid_values[(3+i)%3]
            citizens_data[i]['building'] = not_valid_values[(3+i)%3]
            citizens_data[i]['relatives'] = []

        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.get_data())['error']['citizens']
        not_valid_str_text_error = 'The value should contains at least one letter or digit'
        too_long_str_text_error = 'The string length cannot be more than 256 characters'
        self.assertTrue(errors['0']['building'] == errors['0']['street'] == errors['0']['town'] == [not_valid_str_text_error])
        self.assertTrue(errors['1']['building'] == errors['1']['street'] == errors['1']['town'] == [not_valid_str_text_error])
        self.assertTrue(errors['2']['building'] == errors['2']['street'] == errors['2']['town'] == [too_long_str_text_error])
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

    # Check not valid apartment
    def test_not_valid_apartment(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set)
        citizens_data[0]['apartment'] = 'a'
        citizens_data[1]['apartment'] = 1.5
        citizens_data[2]['apartment'] = -1
        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.get_data())['error']['citizens']
        not_valid_int_error = 'Not a valid integer.'
        wrong_int_error = 'Value must be greater than 0'
        self.assertTrue(errors['0']['apartment'] == errors['1']['apartment'] == [not_valid_int_error])
        self.assertTrue(errors['2']['apartment'] == [wrong_int_error])
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

    # Check not valid name
    def test_not_valid_name(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set)
        citizens_data[0]['name'] = 1
        citizens_data[1]['name'] = 'a'*257
        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.get_data())['error']['citizens']
        self.assertTrue(errors['0']['name'] == ['Not a valid string.'])
        self.assertTrue(errors['1']['name'] == ['The string length cannot be more than 256 characters'])
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

    # Check not valid birth_date
    def test_not_valid_birth_date(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set)
        citizens_data[0]['birth_date'] = 1
        citizens_data[1]['birth_date'] = '10/02/1992'
        citizens_data[2]['birth_date'] = '31.02.1992'
        citizens_data[3]['birth_date'] = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%Y')
        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.get_data())['error']['citizens']
        self.assertTrue(errors['0']['birth_date'] == errors['1']['birth_date'] == errors['2']['birth_date'] == ['Not a valid datetime.'])
        self.assertTrue(errors['3']['birth_date'] == ['Date must be in past'])
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

    # Check not valid gender
    def test_not_valid_gender(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set[:1])
        citizens_data[0]['gender'] = 'table'
        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
             content_type='application/json')
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.get_data())['error']['citizens']
        self.assertTrue(errors['0']['gender'] == ['Must be one of: male, female.'])
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

    # Check not valid relatives
    def test_not_valid_relatives(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set[:2])
        citizens_data[0]['relatives'] = []
        citizens_data[1]['relatives'] = [citizens_data[0]['citizen_id']]
        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
             content_type='application/json')
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.get_data())['error']['citizens']
        self.assertTrue(errors == ['Some relatives is missing.'])
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

    # Check missing fields
    def test_missing_fields(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set[:2])
        required_keys = list(citizens_data[0].keys())
        citizens_data[0] = dict()
        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.get_data())['error']['citizens']
        error_keys = list(errors['0'].keys())
        error_values = list(set([v[0] for v in errors['0'].values()]))

        self.assertTrue(error_values == ['Missing data for required field.'])
        self.assertTrue(set(error_keys) == set(required_keys))
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

    # Check unknown fields
    def test_unknown_fields(self):
        current_max_import_id = self.get_max_import_id()
        citizens_data = copy.deepcopy(citizens_data_set[:1])
        citizens_data[0]['strange_things'] = 'smth strange'
        response = self.app.post("/imports", data=json.dumps(dict(citizens=citizens_data), ensure_ascii=False),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.get_data())['error']['citizens']
        self.assertTrue(errors['0']['strange_things'] == ['Unknown field.'])
        self.assertEqual(self.get_max_import_id(), current_max_import_id)

class ChangeCitizenTestCase(BaseTestCase):


    def create_import(self):
        current_max_import_id = self.get_max_import_id()
        response = self.app.post("/imports", data=citizens, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data())
        self.assertEqual(data, dict(data=dict(import_id=current_max_import_id + 1)))
        return data['data']['import_id']

    def test_valid_change(self):
        import_id = self.create_import()
        citizen_id = citizens_data_set[0]['citizen_id']
        method = 'imports/{}/citizens/{}'.format(import_id,citizen_id)
        citizen_change_data = dict(town="new town", street="new street", building="35b/2",
            apartment=223,name="new name", birth_date='31.01.1992', gender="male")

        response = self.app.patch(method, data=json.dumps(citizen_change_data, ensure_ascii=False),
            content_type='application/json')

        self.assertEqual(response.status_code, 200)
        citizen_change_data['citizen_id'] = citizen_id
        data = json.loads(response.get_data())
        del data['data']['relatives']
        self.assertEqual(citizen_change_data, data['data'])


if __name__ == '__main__':
    unittest.main()