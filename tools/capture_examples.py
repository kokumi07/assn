"""Capture repeatable, real game sessions through an echoing terminal.

Run with: python tools/capture_examples.py
This documentation helper needs pexpect; assn1.py itself uses only the stdlib.
"""

import io
from pathlib import Path
import sys

import pexpect


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "transcripts"
STEP_PROMPT = "Enter the number of steps (5–20): "
CHOICE_PROMPT = "Rock (1), Paper (2), Scissors (3), Quit (0): "
ENTER_PROMPT = "Press ENTER to continue..."
QUIT_PROMPT = "Are you sure you want to quit? (yes/no): "


def capture(name, computer_choices, interactions, ending, position):
    """Execute the unchanged game and record what an actual PTY displays."""
    child_code = (
        "from unittest.mock import patch\n"
        "import assn1\n"
        f"with patch('random.randint', side_effect={computer_choices!r}):\n"
        "    assn1.play_game()\n"
    )
    terminal = pexpect.spawn(
        sys.executable,
        ["-u", "-c", child_code],
        cwd=str(ROOT),
        encoding="utf-8",
        timeout=10,
        echo=True,
    )
    terminal.delaybeforesend = 0.01
    transcript = io.StringIO()
    # logfile_read records echoed input once; logfile would record sends twice.
    terminal.logfile_read = transcript
    try:
        for prompt, answer in interactions:
            terminal.expect_exact(prompt)
            terminal.sendline(answer)
        terminal.expect(pexpect.EOF)
        terminal.close()
        if terminal.exitstatus != 0 or terminal.signalstatus is not None:
            raise RuntimeError(
                f"{name}: child exit={terminal.exitstatus}, "
                f"signal={terminal.signalstatus}\n{transcript.getvalue()}"
            )
    finally:
        if terminal.isalive():
            terminal.close(force=True)

    content = transcript.getvalue().replace("\r\n", "\n").replace("\r", "\n")
    if not content.rstrip().endswith(ending):
        raise AssertionError(f"{name}: unexpected final message")
    if position not in content:
        raise AssertionError(f"{name}: expected positions not present")
    destination = OUTPUT / f"{name}.txt"
    destination.write_text(content, encoding="utf-8")
    print(f"{name}: exit 0; {ending}; {destination.relative_to(ROOT)}")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    capture(
        "validation", [],
        [(STEP_PROMPT, "3"), (STEP_PROMPT, "123"), (STEP_PROMPT, "5"),
         (CHOICE_PROMPT, "0"), (QUIT_PROMPT, "yes")],
        "Game Over!", "Player = 5, Computer = 5",
    )
    capture(
        "mixed", [3, 2, 2],
        [(STEP_PROMPT, "5"),
         (CHOICE_PROMPT, "1"), (ENTER_PROMPT, ""),
         (CHOICE_PROMPT, "1"), (ENTER_PROMPT, ""),
         (CHOICE_PROMPT, "2"), (ENTER_PROMPT, ""),
         (CHOICE_PROMPT, "0"), (QUIT_PROMPT, "yes")],
        "Game Over!", "Player = 4, Computer = 3",
    )
    capture(
        "player_win", [2, 2],
        [(STEP_PROMPT, "5"),
         (CHOICE_PROMPT, "3"), (ENTER_PROMPT, ""),
         (CHOICE_PROMPT, "3"), (ENTER_PROMPT, "")],
        "Finished! PLAYER WINS!", "Player = 0, Computer = 5",
    )
    capture(
        "computer_win", [2, 2, 3],
        [(STEP_PROMPT, "5"),
         (CHOICE_PROMPT, "1"), (ENTER_PROMPT, ""),
         (CHOICE_PROMPT, "1"), (ENTER_PROMPT, ""),
         (CHOICE_PROMPT, "2"), (ENTER_PROMPT, "")],
        "Finished! COMPUTER WINS!", "Player = 5, Computer = 0",
    )
    capture(
        "quit", [],
        [(STEP_PROMPT, "5"), (CHOICE_PROMPT, "0"), (QUIT_PROMPT, "NO"),
         (CHOICE_PROMPT, "0"), (QUIT_PROMPT, "yse"), (QUIT_PROMPT, "YES")],
        "Game Over!", "Player = 5, Computer = 5",
    )
    (OUTPUT / "README.md").write_text(
        "# 실제 터미널 실행 기록\n\n"
        "`python tools/capture_examples.py`가 수정하지 않은 `assn1.py`의 "
        "`play_game()`을 별도 Python 프로세스와 실제 PTY에서 실행한 결과다. "
        "PTY가 사용자 입력을 한 번씩 화면에 되비추며, 저장 시 CRLF만 LF로 정규화한다.\n\n"
        "재현 가능한 보고서 예시를 얻기 위해 테스트 실행 중에만 "
        "`unittest.mock.patch('random.randint', side_effect=...)`로 컴퓨터 선택을 "
        "아래 순서에 고정했다. 일반 실행(`python assn1.py`)에서는 이 패치를 "
        "사용하지 않으며, 컴퓨터가 매 라운드 무작위로 1~3을 선택한다. "
        "따라서 동일 입력의 일반 실행 결과가 아래 기록과 같다고 보장하지 않는다.\n\n"
        "| 기록 | 컴퓨터 선택 순서 | 검증 내용 |\n"
        "| --- | --- | --- |\n"
        "| validation.txt | 없음 | 계단 수 3·123 거부 후 5 허용 |\n"
        "| mixed.txt | 3, 2, 2 | 플레이어 승리·컴퓨터 승리·무승부 |\n"
        "| player_win.txt | 2, 2 | 플레이어 5→2→0, 초과 이동 보정 |\n"
        "| computer_win.txt | 2, 2, 3 | 컴퓨터 5→3→1→0, 초과 이동 보정 |\n"
        "| quit.txt | 없음 | NO 취소, 재확인, 오타 거부, YES 종료 |\n\n"
        "각 실행은 자식 프로세스 종료 코드 0과 최종 메시지·위치를 확인한다. "
        "프로그램 자체에는 외부 패키지가 필요 없고, 이 문서용 캡처 도구만 "
        "`pexpect`를 사용한다.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
