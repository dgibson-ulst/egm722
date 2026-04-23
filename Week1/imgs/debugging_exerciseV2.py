import random

def get_valid_guess():
    while True:
        try:
            guess = int(input("Enter your guess (1–20): "))
            if 1 <= guess <= 20:
                return guess
            else:
                print("Please enter a number between 1 and 20.")
        except ValueError:
            print("Please enter a valid number.")

def play_game():
    rand = random.randint(1, 20)
    guesses = 0

    print("\n🎯 Guess the Number Game")
    print("I'm thinking of a number between 1 and 20.")

    # DEBUG (remove after testing)
    # print(f"[DEBUG] Number is {rand}")

    while True:
        guess = get_valid_guess()
        guesses += 1

        if guess > rand:
            print("Too high.")
        elif guess < rand:
            print("Too low.")
        else:
            print(f"\n🎉 You got it! The number was {rand}.")
            print(f"It took you {guesses} guesses.")
            break

while True:
    play_game()
    again = input("\nPlay again? (y/n): ").lower()
    if again not in ['y', 'yes']:
        print("Thanks for playing! 👋")
        break