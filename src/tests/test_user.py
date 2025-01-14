import json
from unittest import TestCase
from unittest.mock import Mock, patch
from fastapi.responses import JSONResponse
from entities.User import User
import os
import secrets
import string

class TestConstants:
    TEST_EMAIL = "test@example.com"
    
    @staticmethod
    def generate_secure_password():
        """Generate a secure password that meets validation requirements"""
        # Ensure password has required character types
        uppercase = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(2))
        lowercase = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(2))
        digits = ''.join(secrets.choice(string.digits) for _ in range(2))
        special = ''.join(secrets.choice('!@#$%^&*') for _ in range(2))
        
        # Combine all parts and add some random chars to make it longer
        all_chars = uppercase + lowercase + digits + special
        extra = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(4))
        
        # Shuffle the combined password
        password_list = list(all_chars + extra)
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)
    
    @staticmethod
    def generate_test_token():
        """Generate a secure token that meets validation requirements"""
        # Generate a 32-character hex token
        return secrets.token_hex(32)

    # Use static values for tests but generate them securely
    TEST_PASSWORD = os.getenv('TEST_PASSWORD', 'Test@Password123!')  # Fallback that meets requirements
    TEST_HASHED_PASSWORD = os.getenv('TEST_HASHED_PASSWORD', 'hashed_' + secrets.token_hex(16))
    MASKED_PASSWORD = "*" * 16
    
    # Generate tokens that meet your validation requirements
    TEST_TOKEN = os.getenv('TEST_TOKEN', generate_test_token.__func__())
    TEST_VALID_TOKEN = os.getenv('TEST_VALID_TOKEN', generate_test_token.__func__())
    
    @classmethod
    def get_mock_user_data(cls):
        return {
            'email': 'MASKED_EMAIL@example.com',
            'password': cls.MASKED_PASSWORD,
            'registration_number': 'TEST123',
            'address': 'Test Address',
            'company_name': 'Test Company',
            'contact_info': '12345678'
        }

test_current_user = Mock()
test_current_user.id = 1
mock_db = Mock()
mock_bt = Mock()

class TestUser(TestCase):
    def setUp(self):
        self.constants = TestConstants()
        self.mock_user_data = self.constants.get_mock_user_data()
    
    def __init__(self, *args, **kwargs):
        super(TestUser, self).__init__(*args, **kwargs)

    @patch('entities.User.User.getUserByEmail')
    @patch('controllers.user.create_customer', side_effect = lambda x: {"id": "st_test"})
    @patch('controllers.user.create_gitlab_user', side_effect = None)
    @patch('controllers.user.send_confirmation_email', side_effect = None)
    @patch('entities.User.User.save')
    def test_user_signup(self, save_user, send_confirmation_email, create_gitlab_user, create_customer, getUserByEmail):
        getUserByEmail.return_value = None
        from controllers.user import create_user_account
        from schemas.User import UserRegisterSchema
        
        # Given
        payload = UserRegisterSchema(
            email = self.constants.TEST_EMAIL,
            password = self.constants.TEST_PASSWORD,  # Using the secure password that meets requirements
            registration_number = self.mock_user_data['registration_number'],
            address = self.mock_user_data['address'],
            company_name = self.mock_user_data['company_name'],
            contact_info = self.mock_user_data['contact_info']
        )

        # When
        result = create_user_account(payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 201)
        self.assertIsInstance(result, JSONResponse)
        result_body = json.loads(result.body.decode())
        result_body.pop('id', None)
        result_body_str = json.dumps(result_body)
        self.assertEqual(result_body_str, '{"status": "ok", "message": "user successfully created", "i18n_code": "user_created"}')
     
    @patch('entities.Instance.Instance.getActiveUserInstances', side_effect = lambda x,y:[])
    @patch('entities.Access.Access.getUserAccessesByType' , side_effect = lambda x,y,z:[])
    @patch('entities.Project.Project.getUserProjects' , side_effect = lambda x,y:[])
    @patch('entities.Bucket.Bucket.getAllUserBuckets', side_effect = lambda x,y:[])
    @patch('entities.Registry.Registry.getAllUserRegistries')
    def test_get_user_cloud_statistics(self, getActiveUserInstances, getUserAccessesByType, getUserProjects, getAllUserBuckets, getAllUserRegistries):
        # Given
        from controllers.user import get_user_cloud_statistics
        from entities.Instance import Instance
        from entities.Project import Project
        from entities.Bucket import Bucket
        from entities.Registry import Registry
        from entities.Access import Access
        getActiveUserInstances.return_value = [Instance(), Instance()]
        getUserAccessesByType.return_value = [Access(), Access()]
        getUserProjects.return_value = [Project(), Project()]
        getAllUserBuckets.return_value = [Bucket()]
        getAllUserRegistries.return_value = [Registry()]

        # When
        result = get_user_cloud_statistics(test_current_user, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)  
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"projects":0,"instances":0,"buckets":0,"registries":2}')

    @patch('entities.Instance.Instance.getActiveUserInstances', side_effect = lambda x,y:[])
    @patch('entities.Project.Project.getUserProjects', side_effect = lambda x,y:[])
    @patch('entities.Bucket.Bucket.getAllUserBuckets', side_effect = lambda x,y:[])
    @patch('entities.Registry.Registry.getAllUserRegistries', side_effect = lambda x,y:[])
    def test_get_user_cloud_resources(self, getAllUserRegistries, getAllUserBuckets, getActiveUserInstances, getUserProjects):
        # Given
        from controllers.user import get_user_cloud_resources
        from entities.Instance import Instance
        from entities.Project import Project
        from entities.Bucket import Bucket
        from entities.Registry import Registry
        instances = Instance()
        projects = Project()
        buckets = Bucket()
        registries = Registry()
        registries = Registry()
        instances.id = 1
        projects.id = 1
        buckets.id = 1
        registries.id = 1
        getActiveUserInstances.return_value = instances
        getUserProjects.return_value = projects
        getAllUserBuckets.return_value = buckets
        getAllUserRegistries.return_value = registries

        # When
        result = get_user_cloud_resources(test_current_user, mock_db)
        response_status_code = result.__dict__['status_code']
    
        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200) 
        self.assertIsInstance(result, JSONResponse)  
        self.assertEqual(result.body.decode(), '{"projects":[],"instances":[],"buckets":[],"registries":[]}')
  
    @patch('jose.jwt.encode')
    @patch('utils.mail.send_forget_password_email', side_effect = lambda x,y:[])
    @patch('entities.User.User.save')    
    @patch('entities.User.User.getUserByEmail')
    def test_forget_password_email(self, getUserByEmail, send_forget_password_email, encode, save):
        # Given
        from controllers.user import forget_password_email
        from schemas.User import UserEmailUpdateSchema
        from entities.User import User
        encode.return_value = {"email": "test@example.com"}
        payload = UserEmailUpdateSchema(
            email = "example@example.com"
        )
        getUserByEmail.return_value= User(email="test@example.com")

        # When
        result = forget_password_email(payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)  
        self.assertIsInstance(result, JSONResponse)  
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"successfully sent reset password email","i18n_code":"reset_password_success"}')
    
    @patch('controllers.user.User.getUserByEmail')
    @patch('controllers.user.User.updateUserPassword', side_effect = lambda x,y,z:[])    
    def test_user_reset_password(self, getUserByEmail, updateUserPassword): 
        # Given
        from controllers.user import user_reset_password
        from schemas.User import UserLoginSchema
        from entities.User import User
        
        payload = UserLoginSchema(
            email = self.constants.TEST_EMAIL,
            password = self.constants.TEST_PASSWORD  # Using the secure password that meets requirements
        )

        user = User()
        user.id = 1
        user.email = self.mock_user_data['email']
        user.password = self.constants.TEST_HASHED_PASSWORD
        getUserByEmail.return_value = user

        # When
        result = user_reset_password(payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"user successfully updated","i18n_code":"user_updated"}')
     
    @patch('jose.jwt.decode')
    @patch('controllers.user.send_confirmation_email', side_effect = None)
    @patch('entities.User.User.save', side_effect = lambda x,y:[])    
    @patch('entities.User.User.getUserByEmail')
    def test_verify_user_token(self, getUserByEmail, save, send_confirmation_email, decode):
        # Given
        from controllers.user import verify_user_token
        from entities.User import User

        token = self.constants.TEST_TOKEN
        decode.return_value = {"email": self.constants.TEST_EMAIL}
        user = User()
        user.id = 1
        user.email = self.constants.TEST_EMAIL
        getUserByEmail.return_value = User(email=self.constants.TEST_EMAIL)

        # When
        result = verify_user_token(token , mock_db)
        response_status_code = result.__dict__['status_code']
       
        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200) 
        self.assertIsInstance(result, JSONResponse)  
        self.assertEqual(result.body.decode(), '{"status":"ok","email":"test@example.com","message":"user verified","i18n_code":"user_verified"}')

    @patch('entities.User.User.getUserById',side_effect = lambda x,y: User(st_payment_method_id='some_id')  )  
    def test_update_user_autopayment(self , getUserById):
        #Given
        from controllers.user import update_user_autopayment
        from schemas.User import UserPaymentSchema
        from entities.User import User
        current_user = User(id=1)
        payload = UserPaymentSchema(
            status = True
        )
        userId = 1
        user = User()
        user.id = userId
        user.email = "test@example.com"
        user.is_admin = True
        user.confirmed = True
        user.confirmed = True
        getUserById.return_value = user

        # When
        result = update_user_autopayment(current_user, payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"successfully updated auto payment status"}')

    @patch('jose.jwt.decode')
    @patch('controllers.user.send_confirmation_email', side_effect = None)
    @patch('entities.User.User.save', side_effect = lambda x,y:[])  
    @patch('entities.User.User.getUserByEmail')
    def test_confirm_user_account(self, getUserByEmail, send_confirmation_email, save, decode):
        # Given
        from controllers.user import confirm_user_account
        from entities.User import User
        decode.return_value = {"email": "test@example.com"}
        getUserByEmail.return_value = User(confirmed=False, id=1)
        token = self.constants.TEST_VALID_TOKEN

        # When
        result = confirm_user_account(token, mock_db)
        response_status_code = result.__dict__['status_code']
       
        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","email":null,"message":"user successfully confirmed","i18n_code":"user_confirmed"}')

    @patch('jose.jwt.encode')
    @patch('controllers.user.send_confirmation_email', side_effect = None)
    @patch('entities.User.User.save', side_effect = lambda x,y:[])   
    @patch('entities.User.User.getUserByEmail')
    def test_confirmation_email(self, getUserByEmail, encode, send_confirmation_email, save):
        # Given
        from controllers.user import confirmation_email
        from schemas.User import UserEmailUpdateSchema
        from entities.User import User
        encode.return_value = {"email": "test@example.com"}
        payload = UserEmailUpdateSchema(
            email = "example@example.com"
        )
        user = User()
        user.id = 1
        user.email = "example@example.com"
        user.confirmed = False
        getUserByEmail.return_value = user

        # When
        result = confirmation_email(payload, mock_db)
        response_status_code = result.__dict__['status_code']
    
        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"successfully send email confirmation","i18n_code":"success_confirmation_email"}')

    @patch('controllers.user.listPaymentMethods', side_effect = lambda x: {"id": "1"})
    @patch('entities.User.User.getUserById',side_effect = lambda x,y: User(st_payment_method_id='1')  )  
    def test_get_payment_methods(self, listPaymentMethods, getUserById):
        # Given
        from controllers.user import get_payment_methods
        from entities.User import User

        user = User(id=1)
        user.email = self.constants.TEST_EMAIL
        user.is_admin = True
        user.st_customer_id = "1"
        user.confirmed = True
        getUserById.return_value = user

        # When
        result = get_payment_methods(user, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"payment_method":{"id":"1"}}')

    @patch('entities.User.User.updateUser',side_effect = None)    
    @patch('entities.User.User.getUserById', side_effect = lambda x,y: User(id=1))  
    def test_update_user_informations(self, getUserById, updateUser):
        # Given
        from controllers.user import update_user_informations
        from schemas.User import UserRegisterSchema
        from entities.User import User

        user = User()
        user.id = 1
        user.email = self.constants.TEST_EMAIL
        user.password = self.constants.TEST_HASHED_PASSWORD
        user.registration_number = self.mock_user_data['registration_number']
        user.address = self.mock_user_data['address']
        user.company_name = self.mock_user_data['company_name']
        user.contact_info = self.mock_user_data['contact_info']
        getUserById.return_value = user
        updateUser.return_value = user

        payload = UserRegisterSchema(
            email = self.constants.TEST_EMAIL,
            password = self.constants.TEST_PASSWORD,
            registration_number = self.mock_user_data['registration_number'],
            address = self.mock_user_data['address'],
            company_name = self.mock_user_data['company_name'],
            contact_info = self.mock_user_data['contact_info']
        )

        # When
        result = update_user_informations(test_current_user,payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"user successfully updated","i18n_code":"user_updated"}')

    @patch('controllers.user.retrievePaymentMethod')
    @patch('entities.User.User.getUserById',side_effect = None)
    @patch('controllers.user.attachPaymentMethodWithUser')    
    def test_add_payment_method(self, retrievePaymentMethod, getUserById, attachPaymentMethodWithUser):
         # Given
        from controllers.user import add_payment_method
        from schemas.User import UserPaymentMethodSchema
        from entities.User import User

        retrievePaymentMethod.return_value = True
        payload = UserPaymentMethodSchema(
            payment_method = "credit_card"
        )
        getUserById.return_value = User(id=1, st_payment_method_id="some_id")
        attachPaymentMethodWithUser.return_value = True

        # When
        result = add_payment_method(test_current_user,payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 204)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"payment method successfully added","i18n_code":"payment_method_added"}')

    @patch('controllers.user.retrievePaymentMethod')
    @patch('entities.User.User.getUserById',side_effect = None) 
    @patch('controllers.user.User.activateUserPayment')
    @patch('controllers.user.User.setUserStripePaymentMethodId')
    def test_update_payment_method(self, retrievePaymentMethod, getUserById, activateUserPayment, setUserStripePaymentMethodId):
        # Given
        from controllers.user import update_payment_method
        from entities.User import User
        retrievePaymentMethod.return_value = True
        payment_method_id = '1'
        user = User(id=1, st_payment_method_id=payment_method_id)
        getUserById.return_value = user

        # When
        result = update_payment_method (test_current_user,payment_method_id, mock_db)
        response_status_code = result.__dict__['status_code']
       
        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 204)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"payment method successfully updated","i18n_code":"payment_method_updated"}')

    @patch('controllers.user.PAYMENT_ADAPTER.retrieve_payment_method', side_effect = None)
    @patch('entities.User.User.getUserById',side_effect = lambda x,y: User(st_payment_method_id='some_id')  )  
    @patch('controllers.user.User.desactivateUserPayment')
    @patch('controllers.user.PAYMENT_ADAPTER.detach_payment_method', side_effect = None)      
    def test_remove_payment_method(self, getUserById, desactivateUserPayment , detach_payment_method, retrieve_payment_method):
        # Given
        from controllers.user import remove_payment_method
        from entities.User import User

        payment_method = 'some_id'
        user = User(id=1)
        getUserById.return_value= user
        retrieve_payment_method.return_value = payment_method
        detach_payment_method.return_value = False
        desactivateUserPayment.return_value = True
        test_current_user = User(id=1)

        # When
        result = remove_payment_method (test_current_user,payment_method , mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 204)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"payment method successfully removed","i18n_code":"payment_method_removed"}')
