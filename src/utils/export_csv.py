
import pandas as pd

def to_csv_bytes(rows):
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")
