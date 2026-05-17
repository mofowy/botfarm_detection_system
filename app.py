import streamlit as st
import pandas as pd

from modules.data_loader import load_data
from modules.preprocessing import clean_text
from modules.feature_extraction import aggregate_texts_by_account, build_text_features
from modules.ml_analysis import cluster_accounts
from modules.explanation import explain_result, mark_suspicious
from modules.database import seed_database_if_empty, find_suspicious_account


st.set_page_config(
    page_title="Виявлення підозрілих акаунтів",
    layout="wide"
)

# База створюється і заповнюється автоматично під час запуску програми.
seed_database_if_empty()

st.title("Система формування множини підозрілих акаунтів")

st.write(
    "Програмний засіб аналізує текстові повідомлення акаунтів, "
    "виконує кластеризацію та перевіряє акаунти через локальну SQL-базу "
    "відомих підозрілих профілів."
)

uploaded_file = st.file_uploader(
    "Завантажте CSV-файл з даними акаунтів",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        data = load_data(uploaded_file)

        st.subheader("Початкові дані")
        st.dataframe(data.head(20), use_container_width=True)

        if st.button("Запустити аналіз"):
            with st.spinner("Виконується аналіз даних..."):
                data["clean_text"] = data["text"].apply(clean_text)

                account_texts = aggregate_texts_by_account(data)

                features, vectorizer = build_text_features(
                    account_texts["clean_text"]
                )

                clusters = cluster_accounts(features)
                account_texts["cluster"] = clusters

                database_flags = []
                database_risk_levels = []
                database_reasons = []

                for account_id in account_texts["account_id"]:
                    db_result = find_suspicious_account(account_id)

                    if db_result:
                        database_flags.append(True)
                        database_risk_levels.append(db_result[1])
                        database_reasons.append(db_result[2])
                    else:
                        database_flags.append(False)
                        database_risk_levels.append("not_found")
                        database_reasons.append("")

                account_texts["found_in_sql_database"] = database_flags
                account_texts["database_risk_level"] = database_risk_levels
                account_texts["database_reason"] = database_reasons

                account_texts["is_suspicious"] = account_texts.apply(
                    lambda row: mark_suspicious(
                        row["cluster"],
                        row["found_in_sql_database"]
                    ),
                    axis=1
                )

                account_texts["explanation"] = account_texts.apply(
                    lambda row: explain_result(
                        row["cluster"],
                        row["found_in_sql_database"],
                        row["database_reason"]
                    ),
                    axis=1
                )

                message_counts = (
                    data.groupby("account_id")
                    .size()
                    .reset_index(name="messages_count")
                )

                result = account_texts.merge(
                    message_counts,
                    on="account_id",
                    how="left"
                )

                result = result[
                    [
                        "account_id",
                        "messages_count",
                        "cluster",
                        "found_in_sql_database",
                        "database_risk_level",
                        "is_suspicious",
                        "explanation",
                        "clean_text"
                    ]
                ]

            st.success("Аналіз завершено.")

            total_accounts = len(result)
            suspicious_accounts = int(result["is_suspicious"].sum())
            database_matches = int(result["found_in_sql_database"].sum())
            clusters_count = result[result["cluster"] != -1]["cluster"].nunique()

            st.write(f"Проаналізовано акаунтів: {total_accounts}")
            st.write(f"Підозрілих акаунтів: {suspicious_accounts}")
            st.write(f"Акаунтів, знайдених у SQL-базі: {database_matches}")
            st.write(f"Виявлено груп за текстовою схожістю: {int(clusters_count)}")

            st.subheader("Результати аналізу")
            st.dataframe(result, use_container_width=True)

            csv = result.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                label="Завантажити результат CSV",
                data=csv,
                file_name="analysis_result.csv",
                mime="text/csv"
            )

    except Exception as error:
        st.error(f"Помилка: {error}")
else:
    st.info("Завантажте CSV-файл, щоб почати аналіз.")
