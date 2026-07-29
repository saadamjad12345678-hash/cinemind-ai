import pandas as pd

df = pd.read_csv("clean_movies.csv")

df["id"] = df["id"].fillna(0).astype(int)

df.to_csv("clean_movies_fixed.csv", index=False)

print("Done!")