# Rock-Paper-Scissors Stair Game

CSED101 2026학년도 가을학기 과제 1의 Python 게임과 한국어 보고서입니다.

## 실행

Python 3.x와 UTF-8 문자를 표시할 수 있는 터미널이 필요합니다. 게임은 표준 라이브러리만 사용하므로 별도 설치가 필요 없습니다.

```sh
cd /workspace/assn
python assn1.py
```

Windows에서도 파일이 있는 폴더에서 `python assn1.py`로 실행합니다. 계단 수는 5~20, 선택은 바위 1 / 보 2 / 가위 3 / 종료 0입니다. 결과를 확인한 뒤 ENTER를 누르면 이동합니다. 종료 확인에는 대소문자 구분 없이 `yes` 또는 `no`를 입력합니다. 과제의 가정에 따라 계단 수와 선택은 정수로 입력합니다.

## 파일

- `assn1.py`: 게임 소스
- `assn1.pdf`: 한국어 보고서
- `assn1.docx`: 편집 가능한 같은 보고서
- `tests/test_assn1.py`: 표준 라이브러리 기반 동작 검증
- `docs/report.html`, `docs/report.md`: 보고서 원본과 텍스트
- `docs/screenshots/`: 보고서에 삽입한 실제 실행 기록의 화면 캡처
- `docs/transcripts/`: 원본 PTY 실행 기록과 재현 조건

표지에는 제공받은 학과·학번·이름·POVIS ID를 반영했습니다. 코드 구현과 보고서 작성에 생성형 AI를 사용했으므로, 표지에는 그 사실을 기재했으며 AI 도움을 받지 않았다는 확인 문구는 넣지 않았습니다.

## 검증

```sh
python -m unittest discover -s tests -v
```

23개 테스트에서 승패 9가지 조합, 입력 범위와 재입력, 계단 표시, 무승부, 이동 하한, 반복 종료 확인, ENTER 이후 이동 순서 및 실제 CLI 시작·종료를 검증합니다. 세부 조합은 `subTest`로 검사하므로 조합 수와 테스트 메서드 수는 다릅니다.

## 문서 재생성 (선택)

게임 실행과 테스트에는 아래 도구가 필요하지 않습니다. 문서를 재생성할 때만 `pexpect`, `python-docx`, `playwright`와 Chromium, Noto CJK 글꼴을 사용합니다. 현재 클라우드 환경에는 설치되어 있습니다.

```sh
python tools/capture_examples.py
python tools/build_report.py
```

첫 명령은 수정하지 않은 게임을 실제 PTY에서 실행하고, 보고서 예시의 재현을 위해 해당 자식 프로세스에서만 컴퓨터 선택을 고정합니다. 두 번째 명령은 그 기록을 브라우저로 캡처하고 PDF·DOCX·HTML·Markdown을 생성합니다. 일반 게임에서는 컴퓨터 선택이 무작위입니다. 캡처와 보고서는 만들어낸 실행 결과가 아니라 `docs/transcripts/`에 보관된 출력에 근거합니다.
