import pandas as pd
import streamlit as st
import pickle
import requests

# TMDb API Key
API_KEY = "348822c7cc39730b4d9b091cae246ae9"

# Load Data
movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Ensure movies DataFrame has a 'title' column
if isinstance(movies_df, pd.DataFrame):
    movies = movies_df
else:
    movies = pd.DataFrame(movies_df, columns=['title'])


# Function to fetch movie poster using TMDb API
def fetch_poster(movie_name):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}"
    response = requests.get(search_url)
    data = response.json()

    if data['results']:  # Check if any results found
        movie_id = data['results'][0]['id']
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        details_response = requests.get(details_url)
        details_data = details_response.json()

        poster_path = details_data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"  # TMDb image URL
    return "https://via.placeholder.com/200"  # Placeholder if no poster found


# Recommendation Function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index
    if len(movie_index) == 0:
        return [], []

    movie_index = movie_index[0]
    distance = similarity[movie_index]
    movies_list = sorted(enumerate(distance), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_title))  # Fetch poster

    return recommended_movies, recommended_posters


# Streamlit UI
st.title('🎬 Movie Recommendation System')

# Dropdown to select a movie
selected_movie = st.selectbox('Choose a movie:', movies['title'].values)

if st.button('Recommend'):
    recommendations, posters = recommend(selected_movie)

    cols = st.columns(5)  # Create 5 columns for displaying images
    for i in range(len(recommendations)):
        with cols[i]:  # Assign each movie to a column
            st.image(posters[i], caption=recommendations[i], use_container_width=True)


