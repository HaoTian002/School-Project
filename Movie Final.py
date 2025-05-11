# api_fetcher
import requests
def fetch_movie_data(title, api_key):
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# db_manager.py
import sqlite3
def create_db():
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movie_ratings (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    year TEXT,
                    rating TEXT,
                    user_rating TEXT
                )''')
    conn.commit()
    conn.close()

def insert_movie(title, year, rating, user_rating):
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("INSERT INTO movie_ratings (title, year, rating, user_rating) VALUES (?, ?, ?, ?)",
              (title, year, rating, user_rating))
    conn.commit()
    conn.close()

def get_all_movies():
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("SELECT title, year, rating, user_rating FROM movie_ratings")
    results = c.fetchall()
    conn.close()
    return results

# main.py
import tkinter as tk
from tkinter import messagebox
API_KEY = "ff7e7b4"

def search_movie():
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
        save_button.config(state="disabled")

def save_movie():
    user_rating = user_rating_entry.get()
    insert_movie(current_movie["Title"], current_movie["Year"], current_movie["imdbRating"], user_rating)
    messagebox.showinfo("Saved", "Movie saved to database.")

def show_saved_movies():
    records = get_all_movies()
    if not records:
        messagebox.showinfo("Saved Movies", "No movies saved yet.")
        return

    view_window = tk.Toplevel(window)
    view_window.title("Saved Movies")

    for idx, record in enumerate(records):
        title, year, rating, user_rating = record
        tk.Label(view_window, text=f"{idx+1}. {title} ({year}) - IMDb: {rating}, Your Rating: {user_rating}").pack(anchor='w')

# GUI
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

create_db()
window.mainloop()
