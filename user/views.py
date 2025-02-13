from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from common.views import CommonMixin
from products.models import Baskets
from user.forms import UserLoginForm, UserProfile, UserRegisterForm
from user.models import EmailVerification, User


class UserLoginView(CommonMixin, LoginView):
    template_name = 'user/login.html'
    form_class = UserLoginForm
    title = 'Авторизация'


class UserRegisterView(CommonMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'user/register.html'
    success_url = reverse_lazy('user:login')
    success_message = 'Новый пользователь успешно зарегистрирован'
    title = 'Регистрация'


class UserProfileView(CommonMixin, UpdateView):
    model = User
    form_class = UserProfile
    template_name = 'user/profile.html'
    title = 'Профиль'

    def get_success_url(self):
        return reverse_lazy('user:profile', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data()
        context['baskets'] = Baskets.objects.filter(user=self.request.user)
        return context


class EmailVerificationView(CommonMixin, TemplateView):
    template_name = 'user/email_verification.html'
    title = 'Верификация пользователя'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.filter(email=kwargs['email'])[:1].get()
        email_verification = EmailVerification.objects.filter(user=user, code=code)
        if email_verification.exists() and email_verification.last().is_valid_check():
            user.is_verified = True
            user.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('index'))


# def logout(request):
#     auth.logout(request)
#     return HttpResponseRedirect(reverse('user:login'))


# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = form.data['username']
#             password = form.data['password']
#             user = auth.authenticate(username=username, password=password)
#             if user:
#                 auth.login(request, user)
#                 return HttpResponseRedirect(reverse('index'))
#
#     else:
#         form = UserLoginForm()
#     context = {'form': form}
#     return render(request, 'user/login.html', context)


# def registration(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(data=request.post)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data['username']
#             messages.success(request, f'Новый пользователь {username} успешно зарегистрирован')
#             return HttpResponseRedirect(reverse('user:login'))
#     else:
#         form = UserRegisterForm()
#     context = {'form': form}
#     return render(request, 'user/register.html', context)
