import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from collections import Counter
from pathlib import Path

DATA_PATH = Path(r"C:\Users\19181\Desktop\realdonaldtrump.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["text_len"] = df["content"].astype(str).apply(len)
    df["retweets"] = pd.to_numeric(df["retweets"], errors="coerce").fillna(0).astype(int)
    df["favorites"] = pd.to_numeric(df["favorites"], errors="coerce").fillna(0).astype(int)
    df["engagement"] = df["retweets"] + df["favorites"]
    return df

df = load_data(DATA_PATH)

st.title("📊 Donald Trump Tweet Analysis Dashboard")
st.write("This Streamlit app analyzes the Twitter activity of Donald Trump.")


years = sorted(df["year"].dropna().unique())
selected_year = st.selectbox("Select a year to analyze:", years)
df_year = df[df["year"] == selected_year]


keyword = st.text_input("Search for a keyword in tweets:", "").lower()

if keyword:
    df_filtered = df_year[df_year["content"].astype(str).str.lower().str.contains(keyword)]
else:
    df_filtered = df_year

st.write(f"Showing {len(df_filtered)} tweets in {selected_year} containing '{keyword or 'ALL'}'")


tweets_per_year = df["year"].value_counts().sort_index()
fig1, ax1 = plt.subplots(figsize=(8, 3))
ax1.bar(tweets_per_year.index, tweets_per_year.values)
ax1.set_title("Number of Tweets per Year")
ax1.set_xlabel("Year")
ax1.set_ylabel("Count")
st.pyplot(fig1)

fig2, ax2 = plt.subplots(figsize=(8, 3))
ax2.hist(df["engagement"].clip(upper=np.percentile(df["engagement"], 99)))
ax2.set_title("Engagement Distribution (clipped 99th percentile)")
ax2.set_xlabel("Engagement (retweets + favorites)")
ax2.set_ylabel("Number of Tweets")
st.pyplot(fig2)

def tokenize(text):
    text = re.sub(r"http\S+", "", str(text))
    text = re.sub(r"[^A-Za-z\s#@]", " ", text)
    tokens = [t.lower() for t in text.split() if len(t) > 2]
    return tokens

all_tokens = []
for txt in df_filtered["content"].astype(str).fillna(""):
    all_tokens.extend(tokenize(txt))

top_words = Counter([t for t in all_tokens if not t.startswith("@") and not t.startswith("#")]).most_common(15)
if top_words:
    words, counts = zip(*top_words)
    fig3, ax3 = plt.subplots(figsize=(8, 3))
    ax3.bar(words, counts)
    ax3.set_title(f"Top Words in Tweets ({selected_year})")
    ax3.set_xticklabels(words, rotation=45, ha="right")
    st.pyplot(fig3)
else:
    st.info("No tweets found for this selection.")

st.subheader("Top 10 Most Engaging Tweets")
st.dataframe(
    df_filtered.sort_values("engagement", ascending=False).head(10)[
        ["date", "content", "retweets", "favorites", "engagement"]
    ]
)

st.caption("Developed for Data Analysis Project — Streamlit Dashboard Example.")





