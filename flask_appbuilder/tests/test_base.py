from nose.tools import eq_, ok_, raises
import unittest
import os
import string
import random
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from flask_appbuilder import Model, SQLA
from flask_appbuilder.models.filters import FilterStartsWith, FilterEqual
from flask_appbuilder.models.mixins import FileColumn, ImageColumn
from flask_appbuilder.views import MasterDetailView, CompactCRUDMixin
from flask_appbuilder.charts.views import (ChartView, TimeChartView,
                                           DirectChartView, GroupByChartView,
                                           DirectByChartView)
from flask_appbuilder.models.group import aggregate_avg, aggregate_count, aggregate_sum

from flask_appbuilder.models.generic import PSSession
from flask_appbuilder.models.generic.interface import GenericInterface
from flask_appbuilder.models.generic import PSModel

import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)


"""
    Constant english display string from framework
"""
DEFAULT_INDEX_STRING = 'Welcome'
INVALID_LOGIN_STRING = 'Invalid login'
ACCESS_IS_DENIED = "Access is Denied"
UNIQUE_VALIDATION_STRING = 'Already exists'
NOTNULL_VALIDATION_STRING = 'This field is required'
DEFAULT_ADMIN_USER = 'admin'
DEFAULT_ADMIN_PASSWORD = 'general'

log = logging.getLogger(__name__)


class Model1(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    field_integer = Column(Integer())
    field_float = Column(Float())
    field_date = Column(Date())
    field_file = FileColumn()
    field_image = ImageColumn()

    def __repr__(self):
        return str(self.field_string)


class Model2(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    field_integer = Column(Integer())
    field_float = Column(Float())
    field_date = Column(Date())
    group_id = Column(Integer, ForeignKey('model1.id'), nullable=False)
    group = relationship("Model1")

    def __repr__(self):
        return str(self.field_string)

    def field_method(self):
       return "field_method_value"                                               

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder
        from flask_appbuilder.models.datamodel import SQLAModel
        from flask_appbuilder.views import ModelView

        self.app = Flask(__name__)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        self.app.config['CSRF_ENABLED'] = False
        self.app.config['SECRET_KEY'] = 'thisismyscretkey'
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        sess = PSSession()

        class PSView(ModelView):
            datamodel = GenericInterface(PSModel, sess)
            base_permissions = ['can_list', 'can_show']
            list_columns = ['UID', 'C', 'CMD', 'TIME']
            search_columns = ['UID', 'C', 'CMD']


        class Model2View(ModelView):
            datamodel = SQLAModel(Model2)
            list_columns = ['field_integer', 'field_float', 'field_string', 'field_method']

            edit_form_query_rel_fields = [('group',
                                   SQLAModel(Model1, self.db.session),
                                   [['field_string', FilterEqual, 'G2']]
                                  )
                                ]

            add_form_query_rel_fields = [('group',
                                   SQLAModel(Model1, self.db.session),
                                   [['field_string', FilterEqual, 'G1']]
                                  )
                                ]


        class Model1View(ModelView):
            datamodel = SQLAModel(Model1)
            related_views = [Model2View]
            list_columns = ['field_string','field_file']

        class Model1CompactView(CompactCRUDMixin, ModelView):
            datamodel = SQLAModel(Model1)


        class Model1Filtered1View(ModelView):
            datamodel = SQLAModel(Model1)
            base_filters = [['field_string', FilterStartsWith, 'a']]


        class Model1MasterView(MasterDetailView):
            datamodel = SQLAModel(Model1)
            related_views = [Model2View]


        class Model1Filtered2View(ModelView):
            datamodel = SQLAModel(Model1)
            base_filters = [['field_integer', FilterEqual, 0]]


        class Model2ChartView(ChartView):
            datamodel = SQLAModel(Model2)
            chart_title = 'Test Model1 Chart'
            group_by_columns = ['field_string']


        class Model2GroupByChartView(GroupByChartView):
            datamodel = SQLAModel(Model2)
            chart_title = 'Test Model1 Chart'

            definitions = [
                {
                    'group':'field_string',
                    'series':[(aggregate_sum,'field_integer',
                               aggregate_avg, 'field_integer',
                               aggregate_count,'field_integer')
                            ]
                }
            ]
            
        class Model2DirectByChartView(DirectByChartView):
            datamodel = SQLAModel(Model2)
            chart_title = 'Test Model1 Chart'

            definitions = [
                {
                    'group':'field_string',
                    'series':['field_integer','field_float']
                }
            ]

        class Model2TimeChartView(TimeChartView):
            datamodel = SQLAModel(Model2)
            chart_title = 'Test Model1 Chart'
            group_by_columns = ['field_date']

        class Model2DirectChartView(DirectChartView):
            datamodel = SQLAModel(Model2)
            chart_title = 'Test Model1 Chart'
            direct_columns = {'stat1': ('group', 'field_integer')}

        class Model1MasterView(MasterDetailView):
            datamodel = SQLAModel(Model1)
            related_views = [Model2View]

        class Model1MasterChartView(MasterDetailView):
            datamodel = SQLAModel(Model1)
            related_views = [Model2DirectByChartView]


        self.appbuilder.add_view(Model1View, "Model1", category='Model1')
        self.appbuilder.add_view(Model1CompactView, "Model1Compact", category='Model1')
        self.appbuilder.add_view(Model1MasterView, "Model1Master", category='Model1')
        self.appbuilder.add_view(Model1MasterChartView, "Model1MasterChart", category='Model1')
        self.appbuilder.add_view(Model1Filtered1View, "Model1Filtered1", category='Model1')
        self.appbuilder.add_view(Model1Filtered2View, "Model1Filtered2", category='Model1')

        self.appbuilder.add_view(Model2View, "Model2")
        self.appbuilder.add_view(Model2View, "Model2 Add", href='/model2view/add')
        self.appbuilder.add_view(Model2ChartView, "Model2 Chart")
        self.appbuilder.add_view(Model2GroupByChartView, "Model2 Group By Chart")
        self.appbuilder.add_view(Model2DirectByChartView, "Model2 Direct By Chart")
        self.appbuilder.add_view(Model2TimeChartView, "Model2 Time Chart")
        self.appbuilder.add_view(Model2DirectChartView, "Model2 Direct Chart")

        self.appbuilder.add_view(PSView, "Generic DS PS View", category='PSView')


    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None
        log.debug("TEAR DOWN")


    """ ---------------------------------
            TEST HELPER FUNCTIONS
        ---------------------------------
    """

    def login(self, client, username, password):
        # Login with default admin
        return client.post('/login/', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self, client):
        return client.get('/logout/')

    def insert_data(self):
        for x, i in zip(string.ascii_letters[:23], range(23)):
            model = Model1(field_string="%stest" % (x), field_integer=i)
            self.db.session.add(model)
            self.db.session.commit()

    def insert_data2(self):
        models1 = [Model1(field_string='G1'),
                   Model1(field_string='G2'),
                   Model1(field_string='G3')]
        for model1 in models1:
            try:
                self.db.session.add(model1)
                self.db.session.commit()
                for x, i in zip(string.ascii_letters[:10], range(10)):
                    model = Model2(field_string="%stest" % (x),
                                   field_integer=random.randint(1, 10),
                                   field_float=random.uniform(0.0, 1.0),
                                   group=model1)
                    year = random.choice(range(1900, 2012))
                    month = random.choice(range(1, 12))
                    day = random.choice(range(1, 28))
                    model.field_date = datetime.datetime(year, month, day)

                    self.db.session.add(model)
                    self.db.session.commit()
            except Exception as e:
                print("ERROR {0}".format(str(e)))                                                      
                self.db.session.rollback()


    def test_fab_views(self):
        """
            Test views creation and registration
        """
        eq_(len(self.appbuilder.baseviews), 24)  # current minimal views are 11
        

    def test_model_creation(self):
        """
            Test Model creation
        """
        from sqlalchemy.engine.reflection import Inspector

        engine = self.db.session.get_bind(mapper=None, clause=None)
        inspector = Inspector.from_engine(engine)
        # Check if tables exist
        ok_('model1' in inspector.get_table_names())
        ok_('model2' in inspector.get_table_names())

    def test_index(self):
        """
            Test initial access and index message
        """
        client = self.app.test_client()

        # Check for Welcome Message
        rv = client.get('/')
        data = rv.data.decode('utf-8')
        ok_(DEFAULT_INDEX_STRING in data)

    def test_sec_login(self):
        """
            Test Security Login, Logout, invalid login, invalid access
        """
        client = self.app.test_client()

        # Try to List and Redirect to Login
        rv = client.get('/model1view/list/')
        eq_(rv.status_code, 302)
        rv = client.get('/model2view/list/')
        eq_(rv.status_code, 302)

        # Login and list with admin
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = client.get('/model1view/list/')
        eq_(rv.status_code, 200)
        rv = client.get('/model2view/list/')
        eq_(rv.status_code, 200)

        # Logout and and try to list
        self.logout(client)
        rv = client.get('/model1view/list/')
        eq_(rv.status_code, 302)
        rv = client.get('/model2view/list/')
        eq_(rv.status_code, 302)

        # Invalid Login
        rv = self.login(client, DEFAULT_ADMIN_USER, 'password')
        data = rv.data.decode('utf-8')
        ok_(INVALID_LOGIN_STRING in data)

    def test_sec_reset_password(self):
        """
            Test Security reset password
        """
        client = self.app.test_client()

        # Try Reset My password
        rv = client.get('/users/action/resetmypassword/1', follow_redirects=True)
        data = rv.data.decode('utf-8')
        ok_(ACCESS_IS_DENIED in data)

        #Reset My password
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = client.get('/users/action/resetmypassword/1', follow_redirects=True)
        data = rv.data.decode('utf-8')
        ok_("Reset Password Form" in data)
        rv = client.post('/resetmypassword/form',
                         data=dict(password='password', conf_password='password'), follow_redirects=True)
        eq_(rv.status_code, 200)
        self.logout(client)
        self.login(client, DEFAULT_ADMIN_USER, 'password')
        rv = client.post('/resetmypassword/form',
                         data=dict(password=DEFAULT_ADMIN_PASSWORD, conf_password=DEFAULT_ADMIN_PASSWORD),
                         follow_redirects=True)
        eq_(rv.status_code, 200)

        #Reset Password Admin
        rv = client.get('/users/action/resetpasswords/1', follow_redirects=True)
        data = rv.data.decode('utf-8')
        ok_("Reset Password Form" in data)
        rv = client.post('/resetmypassword/form',
                         data=dict(password=DEFAULT_ADMIN_PASSWORD, conf_password=DEFAULT_ADMIN_PASSWORD), 
                         follow_redirects=True)
        eq_(rv.status_code, 200)
        

    def test_generic_interface(self):
        """
            Test Generic Interface for generic-alter datasource
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        rv = client.get('/psview/list')
        data = rv.data.decode('utf-8')


    def test_model_crud(self):
        """
            Test Model add, delete, edit
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        #with open('test.txt', 'rb') as fp:
        rv = client.post('/model1view/add',
                             data=dict(field_string='test1', field_integer='1',
                                       field_float='0.12',
                                       field_date='2014-01-01'), follow_redirects=True)
        eq_(rv.status_code, 200)

        model = self.db.session.query(Model1).first()
        eq_(model.field_string, u'test1')
        eq_(model.field_integer, 1)

        rv = client.post('/model1view/edit/1',
                         data=dict(field_string='test2', field_integer='2'), follow_redirects=True)
        eq_(rv.status_code, 200)

        model = self.db.session.query(Model1).first()
        eq_(model.field_string, u'test2')
        eq_(model.field_integer, 2)

        rv = client.get('/model1view/delete/1', follow_redirects=True)
        eq_(rv.status_code, 200)
        model = self.db.session.query(Model1).first()
        eq_(model, None)


    def test_query_rel_fields(self):
        """
            Test add and edit form related fields filter
        """
        client = self.app.test_client()
        rv = self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()

        # Base filter string starts with
        rv = client.get('/model2view/add?next=%2Fmodel2view%2Flist%2F')
        data = rv.data.decode('utf-8')
        ok_('G1' in data)
        ok_('G2' not in data)

        # Base filter string starts with
        rv = client.get('/model2view/edit/1')
        data = rv.data.decode('utf-8')
        ok_('G2' in data)
        ok_('G1' not in data)


    def test_model_list_order(self):
        """
            Test Model order on lists
        """
        self.insert_data()

        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        rv = client.post('/model1view/list?_oc_Model1View=field_string&_od_Model1View=asc',
                        follow_redirects=True)
        eq_(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        # TODO
        # VALIDATE LIST IS ORDERED
        rv = client.post('/model1view/list?_oc_Model1View=field_string&_od_Model1View=desc',
                        follow_redirects=True)
        eq_(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        # TODO
        # VALIDATE LIST IS ORDERED



    def test_model_add_validation(self):
        """
            Test Model add validations
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        rv = client.post('/model1view/add',
                         data=dict(field_string='test1', field_integer='1'), follow_redirects=True)
        eq_(rv.status_code, 200)

        rv = client.post('/model1view/add',
                         data=dict(field_string='test1', field_integer='2'), follow_redirects=True)
        eq_(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        ok_(UNIQUE_VALIDATION_STRING in data)

        model = self.db.session.query(Model1).all()
        eq_(len(model), 1)

        rv = client.post('/model1view/add',
                         data=dict(field_string='', field_integer='1'), follow_redirects=True)
        eq_(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        ok_(NOTNULL_VALIDATION_STRING in data)

        model = self.db.session.query(Model1).all()
        eq_(len(model), 1)

    def test_model_edit_validation(self):
        """
            Test Model edit validations
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)

        client.post('/model1view/add',
                    data=dict(field_string='test1', field_integer='1'), follow_redirects=True)
        client.post('/model1view/add',
                    data=dict(field_string='test2', field_integer='1'), follow_redirects=True)
        rv = client.post('/model1view/edit/1',
                         data=dict(field_string='test2', field_integer='2'), follow_redirects=True)
        eq_(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        ok_(UNIQUE_VALIDATION_STRING in data)

        rv = client.post('/model1view/edit/1',
                         data=dict(field_string='', field_integer='2'), follow_redirects=True)
        eq_(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        ok_(NOTNULL_VALIDATION_STRING in data)

    def test_model_base_filter(self):
        """
            Test Model base filtered views
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data()
        models = self.db.session.query(Model1).all()
        eq_(len(models), 23)

        # Base filter string starts with
        rv = client.get('/model1filtered1view/list/')
        data = rv.data.decode('utf-8')
        ok_('atest' in data)
        ok_('btest' not in data)

        # Base filter integer equals
        rv = client.get('/model1filtered2view/list/')
        data = rv.data.decode('utf-8')
        ok_('atest' in data)
        ok_('btest' not in data)

    def test_model_list_method_field(self):
        """
            Tests a model's field has a method
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()                                               
        rv = client.get('/model2view/list/')
        eq_(rv.status_code, 200)
        data = rv.data.decode('utf-8')
        ok_('field_method_value' in data)


    def test_compactCRUDMixin(self):
        """
            Test CompactCRUD Mixin view
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()
        rv = client.get('/model1compactview/list/')
        eq_(rv.status_code, 200)


    def test_charts_view(self):
        """
            Test Various Chart views
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()
        log.info("CHART TEST")
        rv = client.get('/model2chartview/chart/')
        eq_(rv.status_code, 200)
        rv = client.get('/model2groupbychartview/chart/')
        eq_(rv.status_code, 200)
        rv = client.get('/model2directbychartview/chart/')
        eq_(rv.status_code, 200)
        rv = client.get('/model2timechartview/chart/')
        eq_(rv.status_code, 200)
        rv = client.get('/model2directchartview/chart/')
        #eq_(rv.status_code, 200)

    def test_master_detail_view(self):
        """
            Test Master detail view
        """
        client = self.app.test_client()
        self.login(client, DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASSWORD)
        self.insert_data2()
        rv = client.get('/model1masterview/list/')
        eq_(rv.status_code, 200)
        rv = client.get('/model1masterview/list/1')
        eq_(rv.status_code, 200)

        rv = client.get('/model1masterchartview/list/')
        eq_(rv.status_code, 200)
        rv = client.get('/model1masterchartview/list/1')
        eq_(rv.status_code, 200)
