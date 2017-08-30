from django.core.exceptions import ValidationError
from django import forms
from django.forms import fields
from django.forms import widgets
from app01 import models

class Register(forms.Form):
    username = fields.CharField(
        required=True,
        widget=widgets.TextInput(attrs={'class': "form-control", 'placeholder': '用户名'}),
        min_length=3,
        max_length=12,
        error_messages={'required': '用户名不能为空',
                        'min_length': '用户名最少为6个字符',
                        'max_length': '用户名最不超过为20个字符'},
    )
    email = fields.EmailField(
        required=True,
        widget=widgets.TextInput(attrs={'class': "form-control", 'placeholder': '请输入邮箱'}),
        error_messages={
            'required': '邮箱不能为空',
            'invalid': '请输入正确的邮箱格式'
        },
    )
    password = fields.CharField(
        widget=widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': '请输入密码'}, render_value=True),
        required=True,
        min_length=6,
        max_length=12,
        error_messages={'required': '密码不能为空!',
                        'min_length': '密码最少为6个字符',
                        'max_length': '密码最多不超过为12个字符!', },
    )
    pwd_again = fields.CharField(
        widget=widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': '再次输入密码!'}, render_value=True),
        required=True,
        error_messages={'required': '请再次输入密码!', }
    )
    avatar = fields.ImageField(
        widget=widgets.FileInput(attrs={"id":"imgSelect"}),
        error_messages={
            "required": "请上传头像！！",
            "invalid": "请上传图片类型的图片！！",
        }

    )

    code = fields.CharField(
        widget=widgets.TextInput(attrs={'class': "form-control", 'placeholder': '验证码'}),
        min_length=4,
        required=True,
        error_messages={
            "required":"验证码不能为空！！",
            "invalid": "验证码错误！！",
        }
    )

    def __init__(self,request, *args, **kwargs):
        super(Register, self).__init__(*args, **kwargs)
        self.user=models.UserInfo.objects
        self.request=request

    def clean_code(self):
        code = self.cleaned_data.get("code")
        t_code = self.request.session.get("code","a")
        print(code)
        print(t_code)
        if code.upper() != t_code.upper():
            raise ValidationError('验证码错误！')
        return code


    def clean_username(self):
        # 查找用户是否已经存在
        username = self.cleaned_data.get('username')
        users = self.user.filter(username=username).count()
        if users:
            raise ValidationError('用户已经存在！')
        return username

    def clean_email(self):
        # 查找邮箱是否已经注册
        email = self.cleaned_data.get('email')
        email_count = self.user.filter(email=email).count()  # 从数据库中查找是否用户已经存在
        if email_count:
            raise ValidationError('该邮箱已经注册！')
        return email

    def _clean_new_password2(self):  # 查看两次密码是否一致
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('pwd_again')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('两次密码不匹配！')

    def clean(self):
        self._clean_new_password2()

class Login(forms.Form):
    username = fields.CharField(
        required=True,
        widget=widgets.TextInput(attrs={'class': "form-control", 'placeholder': '用户名'}),
        error_messages={'required': '用户名不能为空', }
    )

    password = fields.CharField(
        widget=widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': '密码'}),
        required=True,
        error_messages={
            'required': '密码不能为空!',
        }
    )
    code = fields.CharField(
        widget=widgets.TextInput(attrs={'class': "form-control", 'placeholder': '验证码'}),
        required=True,
        error_messages={
            "invalid": "验证码错误！！",
            'required': '请输入验证码! ！',
        }
    )

    def __init__(self,request, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        self.user=models.UserInfo.objects
        self.request=request

    def clean_code(self):
        code = self.cleaned_data.get("code")
        t_code = self.request.session.get("code","a")

        if code.upper() != t_code.upper():
            raise ValidationError('验证码错误！')
        return code

    def clean_password(self):
        username = self.cleaned_data.get('username')
        pwd = self.cleaned_data.get('password')
        user = self.user.filter(username=username,password=pwd).first()

        if not user:
            raise ValidationError('用户名或者密码错误！！')
        return user.nid
