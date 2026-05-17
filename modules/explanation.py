def explain_result(cluster_id, found_in_database=False, database_reason=""):
    if found_in_database:
        return (
            "Акаунт знайдено в SQL-базі підозрілих акаунтів. "
            f"Причина: {database_reason}"
        )

    if cluster_id == -1:
        return (
            "Акаунт не увійшов до вираженої підозрілої групи "
            "за текстовою схожістю."
        )

    return (
        "Акаунт має текстову схожість з іншими профілями цієї групи "
        "та потребує додаткової перевірки."
    )


def mark_suspicious(cluster_id, found_in_database=False):
    return found_in_database or cluster_id != -1
