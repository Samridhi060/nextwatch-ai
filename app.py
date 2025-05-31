import streamlit as st
import pickle
import pandas as pd
import requests
import re
import os
import gdown


# Define file URLs and local paths
files = {
    "similarity.pkl": "https://drive.google.com/uc?id=1DhbxL-uXvalPlHKrY5co3lS1g11uEJy6",
    "movies.pkl": "https://drive.google.com/uc?id=108_pnIYX9_MRh6GzkcjS7lORbkQYBpJi"
}

# Download files if not already present
for filename, url in files.items():
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        gdown.download(url, filename, quiet=False)
    else:
        print(f"{filename} already exists. Skipping download.")



# 1. Load DataFrame
movies_df = pickle.load(open('movies.pkl', 'rb'))

# 2. Extract list of titles for the UI
movie_titles = sorted(
    movies_df['title'].values,
    key=lambda title: (not re.match("^[A-Za-z]", title), title.lower())
)



# 3. Load similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

# 4. Fetch poster using TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3030b800eb78c9b547046c0314241287&language=en-US"
    response = requests.get(url)
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']

# 5. Recommend movies and posters
def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_reco_list = sorted(
        enumerate(distances),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_reco_list:
        movie_id = movies_df.iloc[i[0]].movie_id  # Make sure your DataFrame has a column 'movie_id'
        recommended_movies.append(movies_df.iloc[i[0]].title)
        # fetch poster from API
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# 6. Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Enter your Movie Name',
    movie_titles
)

if st.button('Recommend Movie'):
    names, posters = recommend(selected_movie_name)
    # Layout in 5 columns
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], width=150)
            st.caption(names[i])
