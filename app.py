import gradio as gr
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from io import StringIO
import tempfile
import os



ratings_df = pd.read_csv("/Users/macbook/Desktop/Personlised recommender /My favourite Movie Survey for friends .csv")
imdb_df = pd.read_csv("/Users/macbook/Desktop/Personlised recommender /imdb movies.csv", encoding = 'ISO-8859-1')

ratings_df['genre_list'] = ratings_df['genre'].str.lower().str.replace(" ", "").str.split(';')
imdb_df['genre_list'] = imdb_df['genre'].str.lower().str.replace(" ", "").str.split(',')

user_profiles = defaultdict(lambda: defaultdict(int))
for _, row in ratings_df.iterrows():
    for genre in row['genre_list']:
        user_profiles[row['name']][genre] += row['ratings']

rated_movies = ratings_df.groupby('name')['title'].apply(set).to_dict()

all_genres = sorted(set(g for sublist in imdb_df['genre_list'] for g in sublist))

def plot_genre_chart(user_name):
    genre_data = user_profiles.get(user_name, {})
    if not genre_data:
        return None
    genres = list(genre_data.keys())
    scores = list(genre_data.values())
    fig, ax = plt.subplots()
    ax.barh(genres, scores, color='skyblue')
    ax.set_xlabel("Preference Score")
    ax.set_title(f"{user_name}'s Genre Preferences")
    plt.tight_layout()
    return fig

def recommend_for_user(user_name, num_recs, filter_genre):
    profile = user_profiles.get(user_name, {})
    recommendations = []
    for _, row in imdb_df.iterrows():
        if row['title'] in rated_movies.get(user_name, set()):
            continue
        genres = row['genre_list']
        if filter_genre and filter_genre not in genres:
            continue
        score = sum([profile.get(g, 0) for g in genres])
        recommendations.append((row['title'], ', '.join(genres), score))
    top = sorted(recommendations, key=lambda x: x[2], reverse=True)[:num_recs]
    result_df = pd.DataFrame(top, columns=['Title', 'Genre', 'Score'])
    tmp_dir = tempfile.gettempdir()
    file_path = os.path.join(tmp_dir, f"{user_name.lower().replace(' ', '_')}_recommendations.csv")
    result_df.to_csv(file_path, index=False)
    return plot_genre_chart(user_name), result_df, file_path

user_names = sorted(ratings_df['name'].unique().tolist())

interface = gr.Interface(
    fn=recommend_for_user,
    inputs=[
        gr.Dropdown(user_names, label="🎭 Select your name"),
        gr.Slider(3, 10, value=5, label="🎬 Number of recommendations"),
        gr.Dropdown([""] + all_genres, label="🎛 Filter by genre (optional)", info="Leave blank to show all")
    ],
    outputs=[
        gr.Plot(label="📊 Genre Preference Chart"),
        gr.Dataframe(label="📋 Recommended Movies"),
        gr.File(label="📁 Download CSV")
    ],
    title="🎬 Personalized Movie Recommender",
    description="Get custom movie suggestions based on your favorite genres. Filter and download your results."
)

interface.launch(share=True)