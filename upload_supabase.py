import pandas as pd
from sqlalchemy import create_engine

PASSWORD = "saadarain0987"

DATABASE_URL = f"postgresql+psycopg2://postgres:{PASSWORD}@db.kafdpcecqismaehlroeo.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)

print("Reading CSV...")
df = pd.read_csv("clean_movies_fixed.csv")

print("Uploading...")
df.to_sql(
    "clean_movies",
    engine,
    if_exists="append",
    index=False,
    chunksize=500,
    method="multi"
)

print("Done!")