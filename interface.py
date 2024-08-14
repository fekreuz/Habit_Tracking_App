from habit import Habit

def user_interface():
    print("Welcome to the Habit Tracker!")
    
    while True:
        print("\nMenu:")
        print("1. Add a new habit")
        print("2. Check off a habit")
        print("3. View habit analysis")
        print("4. Delete a habit")
        print("5. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter the habit name: ")
            period = input("Enter the period (daily/weekly): ")

            # Check if the habit already exists in the database
            habit_exists = Habit.check_habit_exists(name, period)

            if not habit_exists:
                habit = Habit(name, period)
                habit.save_to_db()
                print(f"Habit '{name}' added successfully.")
            else:
                print(f"Habit '{name}' already exists in the database.")
        
        elif choice == "2":
            name = input("Enter the habit name: ")
            period = input("Enter the period (daily/weekly): ")
            habit = Habit(name, period)
            habit.load_from_db()
            habit.check_off()
            print(f"Habit '{name}' checked off.")
        
        elif choice == "3":
            print("\nAnalysis Menu:")
            print("1. View all tracked habits")
            print("2. View habits with the same periodicity")
            print("3. View the longest streak of all habits")
            print("4. View the longest streak for a specific habit")

            analysis_choice = input("Enter your choice: ")

            if analysis_choice == "1":
                habits = Habit.get_all_habits()
                print(f"All tracked habits: {habits}")
            
            elif analysis_choice == "2":
                period = input("Enter the period to filter by (daily/weekly): ")
                habits = Habit.get_habits_by_period(period)
                print(f"Habits with {period} periodicity: {habits}")
            
            elif analysis_choice == "3":
                habit_streaks = Habit.get_longest_run_streak_all()
                print("Longest streaks of all habits:")
                for habit, streak in habit_streaks:
                    print(f"Habit '{habit}' has a longest streak of {streak}.")
            
            elif analysis_choice == "4":
                name = input("Enter the habit name: ")
                period = input("Enter the period (daily/weekly): ")
                max_streak = Habit.get_longest_run_streak(name, period)
                print(f"The longest streak for the habit '{name}' during the {period} period is {max_streak}.")

            else:
                print("Invalid choice. Please try again.")
        
        elif choice == "4":
            name = input("Enter the habit name: ")
            period = input("Enter the period (daily/weekly): ")
            habit_to_delete = Habit(name, period)  # Create an instance of the Habit class
            habit_to_delete.delete_habit()  # Call the delete_habit method
            print(f"The habit '{name}' during the {period} period has been deleted.")
        
        elif choice == "5":
            print("Exiting the Habit Tracker. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    user_interface()

