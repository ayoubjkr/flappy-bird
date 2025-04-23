import sqlite3
import os
from constants import DATABASE_PATH

def setup_database():
    """Initialize the database if it doesn't exist"""
    if not os.path.exists(DATABASE_PATH):
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE scores
                    (name TEXT, score INTEGER)''')
        conn.commit()
        conn.close()

def get_highest_score():
    """Get the highest score from the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(score) FROM scores")
    result = c.fetchone()[0]
    conn.close()
    if result is None:
        return 0
    return result

def update_player_score(name, new_score):
    """Update player score in the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    # Check if player exists
    c.execute("SELECT score FROM scores WHERE name = ?", (name,))
    result = c.fetchone()
    
    if result is None:
        # Player doesn't exist, create new record
        c.execute("INSERT INTO scores VALUES (?, ?)", (name, new_score))
    else:
        # Player exists, update if new score is higher
        if new_score > result[0]:
            c.execute("UPDATE scores SET score = ? WHERE name = ?", (new_score, name))
    
    conn.commit()
    conn.close()

def get_all_scores():
    """Get top 10 scores from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
    result = c.fetchall()
    conn.close()
    return result
