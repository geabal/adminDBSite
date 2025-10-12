document.addEventListener('DOMContentLoaded', function() {
    const createFileBtn = document.getElementById('create_file_button');
    const downloadFileBtn = document.getElementById('download_file_button');
    const mongoQuery = document.getElementById('mongo_query');
    const messageArea = document.getElementById('message_area');
    const downloadUrlInput = document.getElementById('download_url');

    // 초기 상태: 다운로드 버튼 비활성화
    downloadFileBtn.disabled = true;

    // '파일 생성' 버튼 클릭 이벤트

    createFileBtn.addEventListener('click', function() {
        const collectionName = document.querySelector('input[name="collection_name"]:checked');
        if (!collectionName) {
            displayMessage('error', 'MongoDB 컬렉션을 선택해야 합니다.');
            return;
        }
        const queryText = mongoQuery.value.trim();
        if (!queryText) {
            displayMessage('error', '쿼리를 입력해주세요');
            return;
        }

        displayMessage('info','...CSV 파일 생성 중...');
        createFileBtn.disabled = true; // 중복 클릭 방지
        downloadFileBtn.disabled = true; // 새로운 파일 생성 중이므로 다운로드 비활성화

        const formData = new FormData();
        formData.append('collection_name', collectionName.id);
        formData.append('query', encodeURIComponent(queryText))
        // CSRF 토큰 추가
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        // AJAX 요청 (Fetch API 사용)
        fetch("create/", {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
            if (status >= 200 && status < 300 && body.status === 'success') {
                // 성공적으로 파일이 생성되었을 경우
                displayMessage('success', body.message);
                downloadFileBtn.disabled = false; // 다운로드 버튼 활성화

                // 다운로드 URL을 input에 저장
                const downloadUrl = "file/PLACEHOLDER/".replace('PLACEHOLDER', body.file_name);
                downloadUrlInput.value = downloadUrl;

            } else {
                // 오류 발생 시
                displayMessage('error', "알 수 없는 오류가 발생했습니다.");
                console.error('File Creation Error:', body);
            }
        })
        .catch(error => {
            // 네트워크 오류 등
            displayMessage('error', '네트워크 오류가 발생했습니다.');
            console.error('Fetch Error:', error);
        })
        .finally(() => {
            // 작업이 끝나면 버튼 다시 활성화
            createFileBtn.disabled = false;
        });
    });

    // '다운로드' 버튼 클릭 이벤트
    downloadFileBtn.addEventListener('click', function() {
        const url = downloadUrlInput.value;

        if (url) {
            // 저장된 URL로 이동하여 파일 다운로드 시작
            window.location.href = url;
        } else {
            alert('먼저 파일을 생성해주세요.');
        }
    });

    function displayMessage(type, message) {
            messageArea.innerHTML = `<div style="padding: 10px; border: 1px solid; border-radius: 5px;
                                   background-color: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#fff3cd'};
                                   color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#856404'};">
                                   <strong>${type.toUpperCase()}:</strong> ${message}</div>`;
    }
});

