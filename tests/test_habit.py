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

# Test the Habit class
@pytest.fixture
def habit():
    """Fixture for a habit instance."""
    return Habit(name="Swim", period="daily")

def test_habit_creation(habit):
    """
    Test the `__init__` method of the Habit class.

    This test creates a new `Habit` instance and verifies that the name and period attributes
    are set correctly.

    Args:
        habit: The `Habit` instance to test.

    Returns:
        None
    """
    assert habit.name == "Swim"
    assert habit.period == "daily"

# Test the `save_to_db' method.
def test_save_to_db(db_connection, habit):
    """
    Test the `save_to_db` method of the Habit class.

    This test saves a `Habit` instance to the database and verifies that it was saved correctly.

    Args:
        db_connection: The database connection fixture.
        habit: The `Habit` instance to save.

    Returns:
        None
    """
    habit.save_to_db()

    with db_connection:
        c = db_connection.cursor()
        c.execute('SELECT * FROM habits WHERE name=? AND period=?', (habit.name, habit.period))
        result = c.fetchone()

    assert result is not None

# Test the `delete_habit' method.
def test_delete_habit(db_connection, habit):
    """
    Test the `delete_habit` method of the Habit class.

    This test saves a `Habit` instance to the database, deletes it, and verifies that it was deleted.

    Args:
        db_connection: The database connection fixture.
        habit: The `Habit` instance to delete.

    Returns:
        None
    """
    habit.save_to_db()
    habit.delete_habit()

    with db_connection:
        c = db_connection.cursor()
        c.execute('SELECT * FROM habits WHERE name=? AND period=?', (habit.name, habit.period))
        result = c.fetchone()

    assert result is None
