from flask import g
import pandas as pd
from data.common import sdb_connect
import jwt
from graphene import ObjectType, String, List, Field


class User:
    user_id = None
    user_setting = None
    user_value = None
    tac = []

    def __init__(self, user_id, setting, value, tac):
        self.user_id = user_id
        self.user_setting = setting
        self.user_value = value
        self.is_tac = tac


    @staticmethod
    def get_user_token(credentials):
        if credentials is None:
            return User._user_error(not_provided=True)
        try:

            username = credentials['credentials']['username']
            password = credentials['credentials']['password']
        except KeyError:
            return User._user_error(not_provided=True)

        user_id = User.query_id(username, password)

        if user_id is None:
            return User._user_error(not_found=True)
        return User.create_token(user_id)

    @staticmethod
    def basic_login(username, password):
        user_id = User.query_id(username, password)
        if user_id is None:
            return False
        User.current_user(user_id)
        return True

    @staticmethod
    def _user_error(not_provided=False, not_found=False):
        if not_provided:
            return {'errors': {'global': 'username or password not provide'}}

        if not_found:
            return {'errors': {'global': 'user not found'}}

    @staticmethod
    def query_id(username, password):
        """
        :param username: username
        :param password: password
        :return: PiptUser_Id or no if not found
        """
        sql = "SELECT PiptUser_Id From PiptUser where Username='{username}' AND Password=MD5('{password}')"\
            .format(username=username, password=password)

        conn = sdb_connect()
        try:
            result = pd.read_sql(sql, conn)
            conn.close()
            return result.iloc[0]['PiptUser_Id']
        except IndexError:
            return None

    @staticmethod
    def create_token(user_id):
        """
        Create a token containing the given user id.

        :param user_id:
        :return: the token
        """
        user = {
            'user_id': '{user_id}'.format(user_id=user_id)
        }
        token = jwt.encode(user, "SECRET-KEY", algorithm='HS256').decode('utf-8')

        return token

    @staticmethod
    def is_valid_token(token):
        try:
            user = jwt.decode(token, "SECRET-KEY", algorithm='HS256')

            if 'user_id' in user:
                User.current_user(user['user_id'])
                return True
            return False
        except:
            return False

    @staticmethod
    def user_if_from_token(token):
        try:
            user = jwt.decode(token, "SECRET-KEY", algorithm='HS256')

            if 'user_id' in user:
                User.current_user(user['user_id'])
                return True
            return False
        except:
            return False

    @staticmethod
    def current_user(user_id):
        if user_id is not None:
            sql = "SELECT * " \
                  "     FROM PiptUserSetting  " \
                  "         LEFT JOIN PiptUserTAC using (PiptUser_Id) " \
                  "     WHERE PiptSetting_Id = 20 " \
                  "         AND PiptUser_Id = {user_id}".format(user_id=user_id)
            conn = sdb_connect()
            result = pd.read_sql(sql, conn)
            conn.close()

            tac = []
            user = -1
            setting = -1
            value = 0
            for i, u in result.iterrows():

                user = u["PiptUser_Id"]
                setting = u["PiptSetting_Id"]
                value = u["Value"]
                if not pd.isnull(u["Partner_Id"]):
                    tac.append(
                        {
                            "is_chair": pd.isnull(u["Partner_Id"]),
                            "partner_id": u["Partner_Id"]
                        }
                    )
            g.user = User(user, setting, value, tac)


class Role(ObjectType):
    type = String()
    partners = Field(List(String))


class UserModel(ObjectType):
    first_name = String()
    last_name = String()
    email = String()
    username = String()
    role = Field(List(Role))
