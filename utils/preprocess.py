import pandas as pd
from sklearn.preprocessing import StandardScaler


def preprocess_input(file_path):
    df = pd.read_csv(file_path, header=None)
    if df.shape[1] != 3197:
        raise ValueError("File must contain 3197 flux columns.")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df.values)
    return X_scaled.reshape(-1, 3197, 1)
