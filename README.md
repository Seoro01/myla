sss

## YouTube 오디오 다운로드

`scripts/download_youtube_audio.py`로 유튜브 영상의 오디오를 mp3로 추출합니다.

```
pip install yt-dlp
python3 scripts/download_youtube_audio.py <youtube-url> [output-dir]
```

ffmpeg가 설치되어 있어야 합니다.

Claude Code 클라우드 세션(웹/모바일 앱)에서 이 스크립트를 실행하려면, 세션이 쓰는
cloud environment의 네트워크 접근 정책이 기본값(Trusted)으로는 YouTube를 막고 있으므로
`Custom`으로 바꾸고 아래 도메인을 허용 목록에 추가해야 합니다:

```
youtube.com
*.youtube.com
*.googlevideo.com
*.ytimg.com
```

설정 방법: claude.ai/code 상단 메시지 입력창 위의 클라우드 아이콘(현재 environment 이름)을
탭 → 사용 중인 environment에 커서를 올리면 나오는 톱니바퀴(설정) 아이콘 탭 → **Network access**를
`Custom`으로 변경 → 위 도메인들을 한 줄씩 입력 → 저장. 이후 새로 시작하는 세션부터 적용됩니다.
