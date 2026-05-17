import pandas as pd


def load_data(file):
    data = pd.read_csv(file)

    required_columns = ["account_id", "text"]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"У файлі відсутній обов'язковий стовпець: {column}"
            )

    if data.empty:
        raise ValueError("Файл не містить даних для аналізу.")

    return data
