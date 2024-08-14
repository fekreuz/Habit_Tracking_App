# Run `setup.py` first to set up the `habits.db` environment

import sys
import os
import pytest
import sqlite3

# Add the parent directory of `habit.py` to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from habit import Habit

# Build connection with the database
@pytest.fixture(scope='session')
def db_connection():
    """
    Set up the database connection fixture.

    This fixture sets up a connection to the `habits.db` SQLite database file and yields the
    connection object for use in tests. After the test is complete, the connection is closed.

    Returns:
        sqlite3.Connection: The database connection object.
    """
    db_file = os.path.join(os.path.dirname(__file__), '..', 'habits.db')
    conn = sqlite3.connect(db_file)
    yield conn
    conn.close()

# Test the `get_all_habits` method of the Habit class
@pytest.fixture(scope='session')
def test_get_all_habits(db_connection):
    """
    Test the `get_all_habits` method of the Habit class.

    This fixture saves some habits to the database and retrieves all habits using the `get_all_habits`
    method. It then verifies that all habits were retrieved and that the list of habits is unique.

    Args:
        db_connection: The database connection fixture.

    Returns:
        None
    """
    with db_connection:
        all_habits = Habit.get_all_habits()

    # Verify that all habits were retrieved
    assert set(habit.name for habit in habits) == set(all_habits)

    # Verify that the list of habits is unique
    assert len(all_habits) == len(set(all_habits))

# Test the `get_habits_by_period` method of the Habit class
@pytest.fixture(scope='session')
def test_get_habits_by_period(db_connection):
    """
    Test the `get_habits_by_period` method of the Habit class.

    This fixture saves some habits to the database and retrieves habits filtered by their period using the
    `get_habits_by_period` method. It then verifies that the correct habits were retrieved for each period.

    Args:
        db_connection: The database connection fixture.

    Returns:
        None
    """
    with db_connection:
        daily_habits = Habit.get_habits_by_period('daily')
        weekly_habits = Habit.get_habits_by_period('weekly')

    # Verify that daily habits were retrieved
    daily_habit_names = set(habit.name for habit in habits if habit.period == 'daily')
    assert set(daily_habits) == daily_habit_names

    # Verify that weekly habits were retrieved
    weekly_habit_names = set(habit.name for habit in habits if habit.period == 'weekly')
    assert set(weekly_habits) == weekly_habit_names

#get_longest_run_streak_all
@staticmethod
def test_get_longest_run_streak_all(db_connection):
    """
    Test the `get_longest_run_streak_all` method of the Habit class.

    This test calls the `get_longest_run_streak_all` method to retrieve the longest streaks for each unique habit
    stored in the database. It then verifies that the result matches the expected streaks.

    Args:
        db_connection: The database connection fixture.

    Returns:
        None
    """
    # Call the static method to get the longest streaks
    with db_connection:
        habit_streaks = Habit.get_longest_run_streak_all()

    # Define the expected result
    expected_streaks = [
        ("Exercise", 31),  # Longest streak for Exercise 
        ("Read a Book", 31),
        ("Meditation", 31),
        ("Clean House", 4),
        ("Grocery Shopping", 4)     
    ]

    # Assert that the result matches the expected streaks
    assert sorted(habit_streaks) == sorted(expected_streaks), f"Expected {expected_streaks}, but got {habit_streaks}"


def test_get_longest_run_streak(db_connection):
    """
    Test the `get_longest_run_streak` method of the Habit class.
    """
    
    with db_connection:
        # Test getting the longest streak for a habit with a long streak
        longest_streak_exercise = Habit.get_longest_run_streak("Exercise", "daily")
        assert longest_streak_exercise == 31

        # Test getting the longest streak for a habit with a short streak
        longest_streak_clean_house = Habit.get_longest_run_streak("Clean House", "weekly")
        assert longest_streak_clean_house == 4

        # Test getting the longest streak for a habit with no records
        longest_streak_none = Habit.get_longest_run_streak("Sleep", "daily")
        assert longest_streak_none == 0
