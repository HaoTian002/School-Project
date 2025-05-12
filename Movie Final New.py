"""
Movie Finder & Rating Logger
Author: [Hao Tian]

Description:
This is a Python application with a GUI built using Tkinter.
Users can search for movies using the OMDb API, view movie information, enter their own ratings, 
and save this data to a local SQLite database. Users can also view all saved records.
"""

import tkinter as tk
from tkinter import messagebox
import requests
import sqlite3

API_KEY = "ff7e7b4"  

# ---------- Database Functions ----------
def create_db():
    """Create a SQLite database and the required table if not exists."""
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS movie_ratings (
            id INTEGER PRIMARY KEY,
            title TEXT,
            year TEXT,
            rating TEXT,
            user_rating TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_movie(title, year, rating, user_rating):
    """Insert a new movie record into the database."""
    try:
        conn = sqlite3.connect("movies.db")
        c = conn.cursor()
        c.execute("INSERT INTO movie_ratings (title, year, rating, user_rating) VALUES (?, ?, ?, ?)",
                  (title, year, rating, user_rating))
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to save movie: {e}")

def get_all_movies():
    """Retrieve all saved movie records from the database."""
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("SELECT title, year, rating, user_rating FROM movie_ratings")
    results = c.fetchall()
    conn.close()
    return results

# ---------- API Fetch Function ----------
def fetch_movie_data(title, api_key):
    """Fetch movie information from OMDb API."""
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        messagebox.showerror("API Error", f"Failed to fetch movie data: {e}")
        return None

# ---------- GUI Functions ----------
def search_movie():
    """Handle movie search action, update result labels."""
    title = entry.get()
    data = fetch_movie_data(title, API_KEY)
    if data and data.get("Response") == "True":
        result_label.config(text=f"{data['Title']} ({data['Year']})\n{data['Plot']}")
        rating_label.config(text=f"IMDb Rating: {data['imdbRating']}")
        save_button.config(state="normal")
        global current_movie
        current_movie = data
    else:
        result_label.config(text="Movie not found.")
        rating_label.config(text="")
        save_button.config(state="disabled")

def save_movie():
    """Save current movie and user rating to the database."""
    if not current_movie:
        messagebox.showwarning("Warning", "No movie selected.")
        return
    user_rating = user_rating_entry.get()
    insert_movie(current_movie["Title"], current_movie["Year"], current_movie["imdbRating"], user_rating)
    messagebox.showinfo("Saved", "Movie saved to database.")

def show_saved_movies():
    """Open a new window and display all saved movies."""
    records = get_all_movies()
    if not records:
        messagebox.showinfo("Saved Movies", "No movies saved yet.")
        return

    view_window = tk.Toplevel(window)
    view_window.title("Saved Movies")

    for idx, record in enumerate(records):
        title, year, rating, user_rating = record
        tk.Label(view_window, text=f"{idx+1}. {title} ({year}) - IMDb: {rating}, Your Rating: {user_rating}").pack(anchor='w')

# ---------- GUI Setup ----------
window = tk.Tk()
window.title("Movie Finder")

tk.Label(window, text="Enter Movie Title:").pack()
entry = tk.Entry(window)
entry.pack()

tk.Button(window, text="Search", command=search_movie).pack()
result_label = tk.Label(window, text="")
result_label.pack()
rating_label = tk.Label(window, text="")
rating_label.pack()

tk.Label(window, text="Your Rating:").pack()
user_rating_entry = tk.Entry(window)
user_rating_entry.pack()

save_button = tk.Button(window, text="Save", command=save_movie, state="disabled")
save_button.pack()

tk.Button(window, text="View Saved Movies", command=show_saved_movies).pack()

# ---------- Initialization ----------
current_movie = None
create_db()
window.mainloop()
