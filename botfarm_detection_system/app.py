import streamlit as st
import pandas as pd

from modules.data_loader import load_data
from modules.preprocessing import clean_text
from modules.feature_extraction import aggregate_texts_by_account, build_text_features
from modules.ml_analysis import cluster_accounts
from modules.explanation import explain_cluster, mark_suspicious


st.set_page_config(
    page_title="Виявлення підозрілих акаунтів",
    layout="wide"
)

st.title("Система формування множини підозрілих акаунтів")
st.write(
    "Програмний засіб аналізує текстові повідомлення акаунтів "
    "та формує групи профілів, які мають ознаки схожої інформаційної активності."
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
                # Очищення тексту
                data["clean_text"] = data["text"].apply(clean_text)

                # Об'єднання повідомлень за акаунтами
                account_texts = aggregate_texts_by_account(data)

                # Формування TF-IDF ознак
                features, vectorizer = build_text_features(
                    account_texts["clean_text"]
                )

                # Кластеризація
                clusters = cluster_accounts(features)

                # Формування результатів
                account_texts["cluster"] = clusters
                account_texts["is_suspicious"] = account_texts["cluster"].apply(
                    mark_suspicious
                )
                account_texts["explanation"] = account_texts["cluster"].apply(
                    explain_cluster
                )

                # Підрахунок кількості повідомлень для кожного акаунта
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
                        "is_suspicious",
                        "explanation",
                        "clean_text"
                    ]
                ]

            st.success("Аналіз завершено.")

            total_accounts = len(result)
            suspicious_accounts = result["is_suspicious"].sum()
            clusters_count = result[result["cluster"] != -1]["cluster"].nunique()

            col1, col2, col3 = st.columns(3)

            col1.metric("Проаналізовано акаунтів", total_accounts)
            col2.metric("Підозрілих акаунтів", int(suspicious_accounts))
            col3.metric("Виявлено груп", int(clusters_count))

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