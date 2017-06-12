from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
	username = forms.CharField(
		required = False,
		label = u'',
		error_messages = {'required': u'Please input username'},
		widget = forms.TextInput(
			attrs = {
				'placeholder':'昵称/手机号',
				'class':'form-control',
				'autocomplete': 'off',
			}
		),
	)
	password = forms.CharField(
		required = False,
		label = u'',
		error_messages = {'required': u'Please input password'},
		widget = forms.PasswordInput(
			attrs = {
				'placeholder':'密码',
				'class':'form-control',
				'onPaste':'return false',
				'ondrop':'return false',
				'autocomplete': 'off',
			}
		),
	)

	def clean(self):
		if not self.is_valid():
			raise forms.ValidationError(u'Input info error, please check')
		else:
			cleaned_data = super(LoginForm, self).clean()

class RegisterForm(forms.Form):
	username = forms.CharField(
		required = False,
		label = u'',
		error_messages = {'required': u'Please input username'},
		widget = forms.TextInput(
			attrs = {
				'placeholder':'昵称',
				'class':'form-control',
			}
		),
	)
	phone = forms.CharField(
		required = False,
		label = u'',
		error_messages = {'required': u'Please input your phone number'},
		widget = forms.TextInput(
			attrs = {
				'placeholder':'手机号',
				'class':'form-control',
				'onKeypress':'var k=event.keyCode; return k>=48&&k<=57',
				'onPaste':'return false',
				'ondrop':'return false',
				'maxlength':'11',
				'type': 'tel'
			}
		),
	)
	password = forms.CharField(
		required = False,
		label = u'',
		error_messages = {'required': u'Please input password'},
		widget = forms.PasswordInput(
			attrs = {
				'placeholder':'设置密码',
				'class':'form-control',
				'onPaste':'return false',
				'ondrop':'return false',
				'maxlength':'20',
			}
		),
	)
	password_repeat = forms.CharField(
		required = False,
		label = u'',
		error_messages = {'required': u'Please input password again'},
		widget = forms.PasswordInput(
			attrs = {
				'placeholder':'再次确认密码',
				'class':'form-control',
				'onPaste':'return false',
				'ondrop':'return false',
				'maxlength':'20',
			}
		),
	)
	# email = forms.CharField(
	# 	required = True,
	# 	label = u'',
	# 	error_messages = {'required': u'Please input your email'},
	# 	widget = forms.EmailInput(
	# 		attrs = {
	# 			'placeholder':u'email',
	# 			'class':'form-control',
	# 		}
	# 	),
	# )

	def clean(self):
		if not self.is_valid():
			raise forms.ValidationError(u'Input info error, please check')
		else:
			cleaned_data = super(RegisterForm, self).clean()