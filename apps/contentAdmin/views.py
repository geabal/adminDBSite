from django.shortcuts import render
import csv, json
import io
from django.http import JsonResponse, HttpResponseBadRequest, Http404,FileResponse
from django.conf import settings
import pandas as pd
from base.MongoClass.MongoContent import MongoContent
import asyncio, os
from datetime import datetime
from urllib.parse import unquote
from django.contrib.auth.decorators import login_required

CSV_DIR = os.path.join(settings.MEDIA_PATH, 'tmp')
@login_required(login_url='main:login')
def upload_index(request):
    #업로드 html 폼 렌더링
    return render(request, 'contentAdmin/upload.html')
def get_mongo_db_collection(collection_name):
    mc = MongoContent(collection_name)
    mc.login(userid=settings.DB_ID, pw=settings.DB_PASSWORD)
    return mc
@login_required(login_url='main:login')
def upload_csv_api(request):
    """
    비동기 POST 요청을 받아 CSV 파일을 처리하고 MongoDB에 저장하는 API 엔드포인트.
    """
    if request.method != 'POST':
        # POST 요청만 허용
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    # 컬렉션 이름과 파일 확인
    collection_name = request.POST.get('collection_name')
    if not collection_name:
        return JsonResponse({'status': 'error', 'message': '컬렉션 이름이 지정되지 않았습니다.'}, status=400)

    if 'csv_file' not in request.FILES:
        # 파일 선택 여부 확인
        return JsonResponse({'status': 'error', 'message': '업로드된 파일이 없습니다.'}, status=400)
    csv_file = request.FILES['csv_file']

    # 데이터 타입 확인
    data = []
    try:
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'status': 'error', 'message': 'CSV 파일만 지원됩니다.'}, status=400)
        #파일 dict 타입으로 변환
        file_data = csv_file.read().decode('utf-8')
        csv_data = io.StringIO(file_data)
        reader = csv.DictReader(csv_data)

        for row in reader:
            data.append(row)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'파일 처리 중 오류 발생: {e}'}, status=500)

    # 데이터 정합성 확인 및 MongoDB 업로드
    try:
        client = get_mongo_db_collection(collection_name)
        asyncio.run(client.insert(data))

        # 성공 응답 (JSON)
        return JsonResponse({
            'status': 'success',
            'message': f'총 {len(data)}개의 레코드가 "{collection_name}" 컬렉션에 성공적으로 업로드되었습니다.'
        }, status=200)

    except Exception as e:
        # DB 연결 또는 삽입 오류
        return JsonResponse({'status': 'error', 'message': f'MongoDB 업로드 중 오류 발생: {e}'}, status=500)

@login_required(login_url='main:login')
def download_index(request):
    return render(request, 'contentAdmin/download.html')

#POST 요청을 받아 DB 쿼리를 실행하고 CSV 파일 생성
@login_required(login_url='main:login')
def create_csv_file(request):
    if request.method != 'POST':
        # POST 요청만 허용
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
    # 컬렉션 이름 및 쿼리 확인
    query = request.POST.get('query')
    if not query:
        return JsonResponse({'status': 'error', 'message': '쿼리를 입력해주세요.'}, status=400)
    collection_name = request.POST.get('collection_name')
    if not collection_name:
        return JsonResponse({'status': 'error', 'message': '컬렉션 이름이 지정되지 않았습니다.'}, status=400)

    # 쿼리 실행 및 결과 가져오기
    try:
        client = get_mongo_db_collection(collection_name)
        query_filter = json.loads(unquote(query))  # 텍스트 형식 쿼리 필터 dictionary 형으로 변환
    except Exception as e:
        return JsonResponse({'status':'error', 'message':f'쿼리 변환 중 오류가 발생했습니다.: {e} {query}'}, status=500)
    try:
        data = asyncio.run(client.find(query_filter=query_filter, n=-1))
        result = pd.DataFrame(data)
    except Exception as e:
        # 쿼리 실행 중 오류 발생 시
        return JsonResponse({'status': 'error', 'message': f'DB 쿼리 실행 중 오류가 발생했습니다: {e}'}, status=500)

    # CSV 파일 생성
    try:
        # 디렉토리가 없으면 생성
        os.makedirs(CSV_DIR, exist_ok=True)
        # 파일 이름 설정
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = f'query_result{now}.csv'
        file_path = os.path.join(CSV_DIR, file_name)
        #파일 저장
        result.to_csv(file_path, encoding='utf-8', index=False)

        # 성공 응답
        return JsonResponse({
            'status': 'success',
            'message': f'CSV 파일이 서버에 생성되었습니다: {file_name}',
            'file_name': file_name  # 다운로드 뷰에 전달할 파일 이름
        })

    except Exception as e:
        # 파일 생성 중 오류 발생 시
        return JsonResponse({'status': 'error', 'message': f'CSV 파일 생성 중 오류가 발생했습니다: {e}'}, status=500)


#GET 요청을 받아 서버에 있는 CSV 파일을 다운로드
@login_required(login_url='main:login')
def download_csv_file(request, file_name):
    file_path = os.path.join(CSV_DIR, file_name)
    #  파일 존재 여부 확인
    if not os.path.exists(file_path):
        raise Http404("파일을 찾을 수 없습니다.")

    # FileResponse를 사용하여 파일 다운로드
    try:
        response = FileResponse(open(file_path, 'rb'), content_type='text/csv')
        # Content-Disposition 헤더 설정: 'attachment'로 설정해야 다운로드됨
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    except Exception as e:
        raise Http404(f"파일 다운로드 중 오류 발생: {e}")