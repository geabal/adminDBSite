
  function checkFileSelection() {
        // 파일 input 요소
        const fileInput = document.getElementById('csv_file');
        // 업로드 버튼 요소
        const uploadButton = document.getElementById('upload_button');

        // 파일이 선택되었는지 (fileInput.files 배열에 파일이 하나 이상 있는지) 확인
        if (fileInput.files.length > 0) {
            uploadButton.disabled = false; // 버튼 활성화
        } else {
            uploadButton.disabled = true; // 버튼 비활성화
        }
 }

 document.addEventListener('DOMContentLoaded', (event) => {
        const fileInput = document.getElementById('csv_file');
        const uploadButton = document.getElementById('upload_button');
        const form = document.getElementById('upload_form_data');
        const messageArea = document.getElementById('message_area');

        // 파일 선택 시 버튼 활성화/비활성화 (기존 로직)
        fileInput.addEventListener('change', () => {
            uploadButton.disabled = fileInput.files.length === 0;
        });

        // 폼 제출 이벤트 핸들러 (API 호출)
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // 기본 폼 제출(페이지 이동) 방지

            // 1. 클라이언트 측 유효성 검사 (컬렉션 이름 및 파일)
            const collectionName = document.querySelector('input[name="collection_name"]:checked');
            if (!collectionName) {
                displayMessage('error', 'MongoDB 컬렉션을 선택해야 합니다.');
                return;
            }
            if (fileInput.files.length === 0) {
                displayMessage('error', 'CSV 파일을 선택해야 합니다.');
                return;
            }

            // 2. FormData 객체 생성 및 데이터 추가
            const formData = new FormData();
            formData.append('collection_name', collectionName.id);
            formData.append('csv_file', fileInput.files[0]);

            // CSRF 토큰 추가
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            uploadButton.disabled = true; // 업로드 중 버튼 비활성화
            displayMessage('info', '파일을 업로드 중입니다. 잠시 기다려주세요...');

            // 3. Fetch API를 사용하여 비동기적으로 API 엔드포인트에 전송
            fetch('upload-csv/', { // urls.py에 설정된 API URL 사용
                method: 'POST',
                body: formData,
                // 파일 업로드 시에는 Content-Type 헤더를 설정하지 않아야 브라우저가 자동으로 multipart/form-data를 처리합니다.
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(({ status, body }) => {
                if (status === 200) {
                    displayMessage('success', body.message);
                } else {
                    displayMessage('error', `업로드 실패 (${status}): ${body.message}`);
                }
            })
            .catch(error => {
                displayMessage('error', `네트워크 오류: ${error.message}`);
            })
            .finally(() => {
                // 업로드 완료 후 버튼 상태 복구
                uploadButton.disabled = fileInput.files.length === 0;
                // 파일 선택 초기화 (선택 사항)
                form.reset();
            });
        });


        function displayMessage(type, message) {
            messageArea.innerHTML = `<div style="padding: 10px; border: 1px solid; border-radius: 5px;
                                   background-color: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#fff3cd'};
                                   color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#856404'};">
                                   <strong>${type.toUpperCase()}:</strong> ${message}</div>`;
        }
    });

