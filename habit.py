import sqlite3
import datetime

class Habit:
    db_file = 'habits.db'  # SQLite database file name

    def __init__(self, name, period):
        """
        Initialize a new Habit object.

        Parameters:
        - name: str, the name of the habit.
        - period: str, the frequency of the habit, either 'daily' or 'weekly'.
        """
        self.name = name
        self.period = period
        self.created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.completed_at = []  # List to store timestamps of habit completions
        self.streak = 0  # Current streak of the habit
        self.longest_streak = 0  # Longest streak recorded for the habit
        self.missed_periods = 0  # Count of missed periods

        # Create the database table if it doesn't exist yet
        self.create_table()

    @staticmethod
    def create_table():
        """
        Create the database table for storing habits if it doesn't exist.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS habits
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, period TEXT, created_at TEXT,
                          completed_at TEXT, streak INTEGER,
                          longest_streak INTEGER, missed_periods INTEGER)''')
            conn.commit()

    def save_to_db(self):
        """
        Save the current state of the habit to the database.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            # Convert the list of completed_at timestamps to a string of comma-separated timestamps
            completed_at_str = ','.join([dt.strftime("%Y-%m-%d %H:%M:%S") for dt in self.completed_at])
            c.execute('''REPLACE INTO habits (name, period, created_at, completed_at, streak, 
                                              longest_streak, missed_periods)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (self.name, self.period, str(self.created_at), completed_at_str,
                       self.streak, self.longest_streak, self.missed_periods))
            conn.commit()

    def delete_habit(self):
        """
        Delete the habit from the database.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            c.execute('''DELETE FROM habits WHERE name=? AND period=?''', (self.name, self.period))
            conn.commit()

    def load_from_db(self):
        """
        Load the habit data from the database based on its name and period.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            # Select the most recent entry based on the 'id' column
            c.execute('''
                SELECT * FROM habits WHERE name=? AND period=? ORDER BY id DESC LIMIT 1
            ''', (self.name, self.period))
            row = c.fetchone()
            if row:
                self.name = row[1]
                self.period = row[2]
                self.created_at = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                if row[4]:  # Check if the completed_at field is not empty
                    self.completed_at = [datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S") for dt_str in row[4].split(',')]
                else:
                    self.completed_at = []
                self.streak = row[5]
                self.longest_streak = row[6]
                self.missed_periods = row[7]

    def check_off(self):
        """
        Mark the habit as completed for the current time period.
        """
        now = datetime.datetime.now()
        self.completed_at.append(now)
        self.calculate_streak()  # Update streak and missed periods based on the current check-off
        self.save_to_db()  # Save immediately after checking off

    def calculate_streak(self):
        """
        Calculate the current streak and update missed periods.
        """
        if not self.completed_at:
            self.streak = 0
            return

        created_at = self.created_at
        now = self.completed_at[-1]  # The current check-off time

        if self.period == 'daily':
            # Calculate the difference in days between the check-off and the last habit creation/check-off
            delta = (now.date() - created_at.date()).days

            if delta <= 1:
                self.streak += 1
            elif delta > 1:
                self.missed_periods += delta - 1
                self.streak = 1  # Reset streak since a day was missed

        elif self.period == 'weekly':
            # Calculate the difference in weeks between the check-off and the last habit creation/check-off
            delta = (now.date() - created_at.date()).days // 7

            if delta <= 1:
                self.streak += 1
            elif delta > 1:
                self.missed_periods += delta - 1
                self.streak = 1  # Reset streak since a week was missed

        # Update the longest streak if the current streak is the highest
        if self.streak > self.longest_streak:
            self.longest_streak = self.streak

    def get_longest_streak(self):
        """
        Get the longest streak of the habit.

        Returns:
        - int: The longest streak recorded.
        """
        return self.longest_streak

    def get_completion_history(self):
        """
        Get the completion history of the habit.

        Returns:
        - list: A list of datetime objects representing when the habit was completed.
        """
        return self.completed_at

    def get_missed_periods(self):
        """
        Get the number of periods missed for the habit.

        Returns:
        - int: The number of missed periods.
        """
        return self.missed_periods

    def analyze_habits(self):
        """
        Analyze the habit and return a summary of its details.

        Returns:
        - dict: A dictionary containing the habit's name, period, creation date,
                completion history, current streak, longest streak, and missed periods.
        """
        analysis = {
            "name": self.name,
            "period": self.period,
            "created_at": self.created_at,
            "completion_history": self.get_completion_history(),
            "streak": self.streak,
            "longest_streak": self.get_longest_streak(),
            "missed_periods": self.get_missed_periods()
        }
        return analysis

    @staticmethod
    def check_habit_exists(name, period):
        """
        Check if a habit with the specified name and period already exists in the database.

        Parameters:
        - name: str, the name of the habit.
        - period: str, the frequency of the habit.

        Returns:
        - bool: True if the habit exists, False otherwise.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT EXISTS(SELECT 1 FROM habits WHERE name=? AND period=?)
            ''', (name, period))
            result = c.fetchone()[0]
        return result

    @staticmethod
    def get_all_habits():
        """
        Get a list of all unique habits stored in the database.

        Returns:
        - list: A list of unique habit names.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            c.execute('''SELECT DISTINCT name FROM habits''')
            habits = [row[0] for row in c.fetchall()]
        return list(set(habits))  # Ensure uniqueness using set

    @staticmethod
    def get_habits_by_period(period):
        """
        Get a list of habits filtered by their period (e.g., 'daily', 'weekly').

        Parameters:
        - period: str, the frequency of the habits to filter by.

        Returns:
        - list: A list of unique habit names that match the specified period.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            c.execute('''SELECT DISTINCT name FROM habits WHERE period=?''', (period,))
            habits = [row[0] for row in c.fetchall()]
        return list(set(habits))  # Ensure uniqueness using set

    @staticmethod
    def get_longest_run_streak_all():
        """
        Get the longest streak for each unique habit stored in the database.

        Returns:
        - list of tuples: A list where each tuple contains the habit name and its longest streak.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT name, MAX(longest_streak) AS max_streak
                FROM habits
                GROUP BY name
            ''')
            habit_streaks = c.fetchall()
        return habit_streaks

    @staticmethod
    def get_longest_run_streak(name, period):
        """
        Get the longest streak for a specific habit and period.

        Parameters:
        - name: str, the name of the habit.
        - period: str, the period of the habit.

        Returns:
        - int: The longest streak recorded for the habit with the specified name and period.
        """
        with sqlite3.connect(Habit.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT MAX(longest_streak) AS max_streak
                FROM habits
                WHERE name = ? AND period = ?
            ''', (name, period))
            max_streak = c.fetchone()[0]  # Get the max streak value
        return max_streak if max_streak is not None else 0  # Return 0 if no records are found

    def __del__(self):
        """
        Destructor for the Habit class. Currently, no explicit cleanup is required
        because context managers handle database connections.
        """
        pass  # No need to close the connection here since we are using context managers

    
