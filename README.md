# django_restful

用于编写django restful api,该包在[djangorestframework](http:://www.django-rest-framework.org/ 'djangorestframework')的基础上封装完成，提高了url导航的便捷性。

## 安装

    pip install django_restful
    
## 示例

### 生成api

    # -*- coding: utf-8 -*-

    from rest_framework import status

    from django_restful import RestfulApiView, RestfulApiError, DoesNotExistError, view_http_method
    from django_restful.response import ErrorResponse, Response

    from api.serializers.auth_user import AuthUserSerializer
    from api.models.auth_user import AuthUserModel


    class AuthUserList(RestfulApiView):

        def __init__(self):
            self._service = AuthUserModel()

        def get(self, request, format=None):
            users = self._service.get_all()
            serializer = AuthUserSerializer(users, many=True)
            return Response(serializer.data)
        
        # 配置URL： url(r'^user/authenticate/$', AuthUserList.as_view(), {'MIME_TYPE': 'authenticate'})
        
        @view_http_method(['POST'])
        def authenticate(self, request):
            login_name = request.POST.get('login_name', None)
            login_pwd = request.POST.get('login_pwd', None)
            if login_name and login_pwd:
                m = self._service.get_one_login_name(login_name)
                if m is None or m['login_password'] != login_pwd:
                    return ErrorResponse(u'用户名或密码错误。')

                serializer = AuthUserSerializer(m)
                return Response(serializer.data)
            return ErrorResponse(u'login_name和login_pwd参数不能为空。')


    class AuthUserDetail(RestfulApiView):

        def __init__(self):
            self._service = AuthUserModel()

        def get_object(self, pk):
            user = self._service.get_one(pk)
            if user is None:
                raise DoesNotExistError(u'未找到该用户.')
            return user

        def get(self, request, pk, format=None):
            try:
                user = self.get_object(pk)
                serializer = AuthUserSerializer(user)
                return Response(serializer.data)
            except DoesNotExistError as ex:
                return ErrorResponse(ex)

        @view_http_method(['POST', 'PUT'])
        def modify_pwd(self, request, pk, format=None):
            try:
                old_pwd = request.POST.get('old_pwd', None)
                new_pwd = request.POST.get('new_pwd', None)

                if old_pwd is None:
                    return ErrorResponse(u'旧密码未能为空。')
                if new_pwd is None:
                    return ErrorResponse(u'新密码未能为空。')

                user = self.get_object(pk)
                if user['login_password'] != old_pwd:
                    return ErrorResponse(u'旧密码错误。')

                self._service.modify_pwd(pk, new_pwd)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except DoesNotExistError as ex:
                return ErrorResponse(ex)
                
### api url 配置

    url(r'^user/$', AuthUserList.as_view()),
    url(r'^user/authenticate/$', AuthUserList.as_view(), {'MIME_TYPE': 'authenticate'}),
    url(r'^user/(?P<pk>.*)/modify_pwd/$',AuthUserDetail.as_view(), {'MIME_TYPE': 'modify_pwd'}),
    url(r'^user/(?P<pk>.*)/$', AuthUserDetail.as_view())
    
### 调用api示例
    # -*- coding: utf-8 -*-

    import requests

    from django_restful import RestfulApiError, parse_resp_json
    from django_restful.utils import build_url
    from django_restful.decorators import parse_resp_status


    class UserModel(object):

        def __init__(self):
            self.base_url = 'http://127.0.0.1:8000/api/user/'

        def get_user(self, user_id):
            return self.get_one(user_id)

        @parse_resp_json
        def get_one(self, user_id):
            url = build_url(self.base_url, user_id)
            return requests.get(url)

        @parse_resp_json
        def get_all(self):
            return requests.get(self.base_url)

        @parse_resp_json
        def authenticate(self, login_name, login_pwd):
            url = build_url(self.base_url, 'authenticate')
            data = {'login_name': login_name, 'login_pwd': login_pwd}
            return requests.post(url, data=data)

        @parse_resp_status
        def modify_pwd(self, user_id, old_pwd, new_pwd):
            url = build_url(self.base_url, [user_id, 'modify_pwd'])
            data = {'old_pwd': old_pwd, 'new_pwd': new_pwd}
            return requests.post(url, data=data)
