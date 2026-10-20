"""Rock-Paper-Scissors Stair Game (Python 3)."""


def get_player_choice():
    """0(종료), 1(바위), 2(보), 3(가위) 중 올바른 입력을 반환한다."""
    while True:
        choice = int(input("Rock (1), Paper (2), Scissors (3), Quit (0): "))
        if 0 <= choice <= 3:
            return choice
        print("Invalid input!")
        print()


def get_computer_choice():
    """컴퓨터가 고른 가위바위보를 1, 2, 3 중 하나로 반환한다."""
    # 함수 안에서 모듈을 불러와 전역 변수 없이 난수를 사용한다.
    import random

    return random.randint(1, 3)


def print_stairs(total_steps, player_pos, computer_pos):
    """전체 계단과 두 참가자의 현재 위치를 출력한다."""
    print("○-Player ●-Computer ◐-Player & Computer")
    print()

    for step in range(total_steps, -1, -1):
        # 계단을 내려갈수록 계단 블록의 개수가 하나씩 늘어난다.
        stairs = "▨" * (total_steps - step)
        marker = ""
        if step == player_pos and step == computer_pos:
            marker = "◐"
        elif step == player_pos:
            marker = "○"
        elif step == computer_pos:
            marker = "●"
        print(f"[{step:2}]{stairs}{marker}")

    print()
    print(f"Player = {player_pos}, Computer = {computer_pos}")


def determine_winner(player_choice, computer_choice):
    """라운드 결과를 'player', 'computer', 'tie' 중 하나로 반환한다."""
    if player_choice == computer_choice:
        return "tie"

    # 바위는 가위, 보는 바위, 가위는 보를 이긴다.
    if ((player_choice == 1 and computer_choice == 3)
            or (player_choice == 2 and computer_choice == 1)
            or (player_choice == 3 and computer_choice == 2)):
        return "player"
    return "computer"


def update_position(current_pos, move_steps):
    """승자가 이동한 위치를 계산하며, 0 아래로 내려가지 않도록 한다."""
    new_pos = current_pos - move_steps
    if new_pos < 0:
        return 0
    return new_pos


def play_game():
    """입력, 라운드 진행, 위치 갱신, 종료를 순서대로 관리한다."""
    print("=== Rock-Paper-Scissors Stair Game ===")
    print()

    # 과제 조건에 따라 계단 수와 가위바위보 입력은 정수라고 가정한다.
    while True:
        total_steps = int(input("Enter the number of steps (5–20): "))
        if 5 <= total_steps <= 20:
            break
        print("Invalid input!")
        print()

    player_pos = total_steps
    computer_pos = total_steps
    choice_names = ["", "Rock", "Paper", "Scissors"]
    print()
    print_stairs(total_steps, player_pos, computer_pos)

    while player_pos > 0 and computer_pos > 0:
        player_choice = get_player_choice()

        if player_choice == 0:
            # 종료를 취소한 뒤 다시 0을 입력해도 매번 확인한다.
            print()
            while True:
                answer = input("Are you sure you want to quit? (yes/no): ").lower()
                if answer == "yes" or answer == "no":
                    break
                print("Invalid input!")
                print()

            print()
            if answer == "yes":
                print("Game Over!")
                return
            continue

        # 유효한 대결 선택이 있을 때만 컴퓨터의 선택을 생성한다.
        computer_choice = get_computer_choice()
        winner = determine_winner(player_choice, computer_choice)
        print()
        print(f"Player: {choice_names[player_choice]}")
        print(f"Computer: {choice_names[computer_choice]}")
        if winner == "player":
            print("Player wins!")
        elif winner == "computer":
            print("Computer wins!")
        else:
            print("Tie!")

        print()
        input("Press ENTER to continue...")

        # 결과를 확인한 후 승자 자신의 선택 값만큼 이동한다.
        if winner == "player":
            player_pos = update_position(player_pos, player_choice)
        elif winner == "computer":
            computer_pos = update_position(computer_pos, computer_choice)

        print()
        print_stairs(total_steps, player_pos, computer_pos)

    # 마지막 라운드의 계단과 위치를 먼저 보여 준 뒤 최종 승자를 출력한다.
    print()
    if player_pos == 0:
        print("Finished! PLAYER WINS!")
    else:
        print("Finished! COMPUTER WINS!")


if __name__ == "__main__":
    play_game()
