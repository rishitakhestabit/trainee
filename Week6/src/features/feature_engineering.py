import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def add_engineered_features_df(X: pd.DataFrame) -> pd.DataFrame:
    """
    PURE feature engineering for inference + training.
    Input: raw X dataframe (NO churn column needed)
    Output: X with engineered columns added.

    This function must be used BOTH:
    - Day-3/4 training pipeline (FunctionTransformer)
    - Day-5 inference pipeline
    """
    X = X.copy()
    X = clean_column_names(X)

    # totalcharges numeric safe (common telco issue)
    if "totalcharges" in X.columns:
        X["totalcharges"] = pd.to_numeric(X["totalcharges"], errors="coerce").fillna(0)

    # 1) tenure_years + tenure_bucket
    if "tenure" in X.columns:
        X["tenure"] = pd.to_numeric(X["tenure"], errors="coerce").fillna(0).astype(int)
        X["tenure_years"] = X["tenure"] / 12.0

        # Keep EXACT labels you used
        X["tenure_bucket"] = pd.cut(
            X["tenure"],
            bins=[-1, 12, 24, 48, 72, 10_000],
            labels=["0_1y", "1_2y", "2_4y", "4_6y", "6y_plus"],
        ).astype(str)

    # 2) avg_monthly_charge
    if all(col in X.columns for col in ["totalcharges", "tenure"]):
        # +1 prevents divide by 0; matches your original logic
        X["avg_monthly_charge"] = X["totalcharges"] / (X["tenure"] + 1)

    # 3) long-term contract
    if "contract" in X.columns:
        X["is_long_term_contract"] = X["contract"].isin(["One year", "Two year"]).astype(int)

    # 4) autopay
    if "paymentmethod" in X.columns:
        X["is_autopay"] = X["paymentmethod"].astype(str).str.contains("automatic", case=False, na=False).astype(int)

    # 5) has internet
    if "internetservice" in X.columns:
        X["has_internet"] = (X["internetservice"].astype(str).str.lower() != "no").astype(int)

    # 6) counts
    security_cols = ["onlinesecurity", "onlinebackup", "deviceprotection", "techsupport"]
    sec_exist = [c for c in security_cols if c in X.columns]
    if sec_exist:
        X["security_services_count"] = X[sec_exist].apply(lambda r: (r == "Yes").sum(), axis=1)

    ent_cols = ["streamingtv", "streamingmovies"]
    ent_exist = [c for c in ent_cols if c in X.columns]
    if ent_exist:
        X["entertainment_services_count"] = X[ent_exist].apply(lambda r: (r == "Yes").sum(), axis=1)

    service_cols = [
        "phoneservice", "multiplelines", "onlinesecurity", "onlinebackup",
        "deviceprotection", "techsupport", "streamingtv", "streamingmovies"
    ]
    svc_exist = [c for c in service_cols if c in X.columns]
    if svc_exist:
        X["total_services"] = X[svc_exist].apply(lambda r: (r == "Yes").sum(), axis=1)

    # 7) ratio
    if all(col in X.columns for col in ["totalcharges", "monthlycharges"]):
        X["monthlycharges"] = pd.to_numeric(X["monthlycharges"], errors="coerce").fillna(0.0)
        X["total_to_monthly_ratio"] = X["totalcharges"] / (X["monthlycharges"] + 1e-6)

    return X
