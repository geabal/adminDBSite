from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
@login_required(login_url='main:login')
def main_index(request):
    return render(request, 'main/select_db.html')

def login_index(request):
    return render(request, 'main/login.html')

def user_login(request):
    if request.method == 'POST':
        # 1. 사용자 인증 (Credentials 검증)
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is not None:
            # 2. 세션 설정 (사용자를 '로그인' 상태로 만듦)
            # 이 함수가 auth_user_id를 세션에 저장하여 '로그인 상태'를 유지합니다.
            login(request, user)
            request.session['username'] = request.POST['username']

            return redirect('main:selectDB')  # 'home'은 login_required가 적용된 페이지여야 합니다.
        else:
            # 인증 실패 처리
            return render(request, 'login.html', {'error': 'Invalid credentials'})

def user_logout(request):
    logout(request)
    return redirect('main:login')