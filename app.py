import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Data Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f8fa;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    h1 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h2 {
        font-weight: 650;
    }

    h3 {
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        padding: 16px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }

    div[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    .insight-box {
        padding: 16px 18px;
        border-radius: 12px;
        background-color: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
        line-height: 1.55;
    }

    .section-description {
        color: #666666;
        font-size: 0.95rem;
        margin-top: -8px;
        margin-bottom: 18px;
    }

    .status-box {
        padding: 12px 14px;
        border-radius: 10px;
        background-color: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }

    .footer {
        text-align: center;
        color: #777777;
        font-size: 0.85rem;
        padding-top: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_DATASET_URL = (
    "https://raw.githubusercontent.com/"
    "nethajinirmal13/Training-datasets/main/apple_products.csv"
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_default_data():
    return pd.read_csv(DEFAULT_DATASET_URL)


def load_uploaded_file(uploaded_file):

    try:

        file_name = uploaded_file.name.lower()

        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif file_name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)

        else:
            return None, "Unsupported file type."

        return df, None

    except Exception as e:
        return None, str(e)


# ============================================================
# BASIC DATA CLEANING
# ============================================================

def clean_column_names(df):

    df = df.copy()

    cleaned_columns = []

    for column in df.columns:

        column = str(column).strip()

        if column == "":
            column = "Unnamed Column"

        cleaned_columns.append(column)

    # Make duplicate column names unique
    seen = {}

    final_columns = []

    for column in cleaned_columns:

        if column not in seen:
            seen[column] = 0
            final_columns.append(column)

        else:
            seen[column] += 1
            final_columns.append(
                f"{column}_{seen[column]}"
            )

    df.columns = final_columns

    return df


# ============================================================
# DATA TYPE DETECTION
# ============================================================

def detect_column_types(df):

    numeric_columns = []
    categorical_columns = []
    datetime_columns = []
    text_columns = []
    boolean_columns = []

    for column in df.columns:

        series = df[column]

        # Boolean
        if pd.api.types.is_bool_dtype(series):

            boolean_columns.append(column)
            continue

        # Numeric
        if pd.api.types.is_numeric_dtype(series):

            numeric_columns.append(column)
            continue

        # Already datetime
        if pd.api.types.is_datetime64_any_dtype(series):

            datetime_columns.append(column)
            continue

        # Date detection
        column_name = str(column).lower()

        date_keywords = [
            "date",
            "time",
            "year",
            "month",
            "day",
            "timestamp"
        ]

        looks_like_date = any(
            keyword in column_name
            for keyword in date_keywords
        )

        if looks_like_date:

            converted = pd.to_datetime(
                series,
                errors="coerce"
            )

            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.70:

                datetime_columns.append(column)
                continue

        # Text / categorical detection
        unique_count = series.nunique(
            dropna=True
        )

        total_count = len(series)

        if total_count == 0:

            categorical_columns.append(column)

        elif unique_count <= min(
            50,
            max(10, int(total_count * 0.20))
        ):

            categorical_columns.append(column)

        else:

            text_columns.append(column)

    return {
        "numeric": numeric_columns,
        "categorical": categorical_columns,
        "datetime": datetime_columns,
        "text": text_columns,
        "boolean": boolean_columns
    }


# ============================================================
# DATE CONVERSION
# ============================================================

def convert_detected_dates(df, column_types):

    df = df.copy()

    for column in column_types["datetime"]:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    return df


# ============================================================
# DATASET PROFILING
# ============================================================

def profile_dataset(df, column_types):

    rows = len(df)
    columns = len(df.columns)

    missing_cells = int(
        df.isnull().sum().sum()
    )

    total_cells = rows * columns

    if total_cells > 0:

        missing_percentage = (
            missing_cells / total_cells
        ) * 100

    else:

        missing_percentage = 0

    duplicate_rows = int(
        df.duplicated().sum()
    )

    memory_usage = (
        df.memory_usage(deep=True).sum()
        / 1024
    )

    return {
        "rows": rows,
        "columns": columns,
        "missing_cells": missing_cells,
        "missing_percentage": missing_percentage,
        "duplicate_rows": duplicate_rows,
        "memory_kb": memory_usage,
        "numeric_count": len(
            column_types["numeric"]
        ),
        "categorical_count": len(
            column_types["categorical"]
        ),
        "datetime_count": len(
            column_types["datetime"]
        ),
        "text_count": len(
            column_types["text"]
        )
    }


# ============================================================
# SMART COLUMN ROLE DETECTION
# ============================================================

def find_column_by_keywords(columns, keywords):

    for column in columns:

        name = str(column).lower()

        for keyword in keywords:

            if keyword in name:
                return column

    return None


def detect_business_columns(df, column_types):

    numeric = column_types["numeric"]
    categorical = column_types["categorical"]

    possible_price = find_column_by_keywords(
        numeric,
        [
            "price",
            "amount",
            "cost",
            "salary",
            "revenue",
            "sales",
            "income",
            "profit",
            "value"
        ]
    )

    possible_rating = find_column_by_keywords(
        numeric,
        [
            "rating",
            "score",
            "rank"
        ]
    )

    possible_quantity = find_column_by_keywords(
        numeric,
        [
            "quantity",
            "qty",
            "units",
            "count",
            "number"
        ]
    )

    possible_discount = find_column_by_keywords(
        numeric,
        [
            "discount",
            "discount percentage",
            "discount_percent"
        ]
    )

    possible_category = find_column_by_keywords(
        categorical,
        [
            "category",
            "department",
            "segment",
            "type",
            "brand",
            "region",
            "city",
            "state",
            "country"
        ]
    )

    return {
        "price": possible_price,
        "rating": possible_rating,
        "quantity": possible_quantity,
        "discount": possible_discount,
        "category": possible_category
    }


# ============================================================
# FORMATTING FUNCTIONS
# ============================================================

def format_number(value):

    if pd.isna(value):
        return "N/A"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.2f}K"

    return f"{value:,.2f}"


def format_percentage(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


# ============================================================
# INSIGHT GENERATION
# ============================================================

def generate_insights(
    df,
    column_types,
    business_columns
):

    insights = []

    numeric_columns = column_types["numeric"]
    categorical_columns = column_types["categorical"]

    # Dataset size
    insights.append(
        f"The dataset contains **{len(df):,} rows** "
        f"and **{len(df.columns):,} columns**."
    )

    # Missing values
    missing = int(
        df.isnull().sum().sum()
    )

    if missing == 0:

        insights.append(
            "There are **no missing cells**, so the "
            "dataset is complete with respect to null values."
        )

    else:

        insights.append(
            f"The dataset contains **{missing:,} missing cells**. "
            "Columns with high missingness should be reviewed "
            "before drawing conclusions."
        )

    # Duplicates
    duplicates = int(
        df.duplicated().sum()
    )

    if duplicates == 0:

        insights.append(
            "No completely duplicated rows were detected."
        )

    else:

        insights.append(
            f"**{duplicates:,} duplicate rows** were detected. "
            "These may require investigation before analysis."
        )

    # Numeric insights
    if numeric_columns:

        numeric_means = {}

        for column in numeric_columns:

            series = pd.to_numeric(
                df[column],
                errors="coerce"
            ).dropna()

            if len(series) > 0:

                numeric_means[column] = series.mean()

        if numeric_means:

            highest_mean_column = max(
                numeric_means,
                key=numeric_means.get
            )

            insights.append(
                f"Among numeric variables, "
                f"**{highest_mean_column}** has the highest "
                f"average value "
                f"({format_number(numeric_means[highest_mean_column])})."
            )

    # Category insight
    if categorical_columns:

        category = categorical_columns[0]

        counts = (
            df[category]
            .value_counts(dropna=True)
        )

        if len(counts) > 0:

            top_category = counts.index[0]
            top_count = counts.iloc[0]

            insights.append(
                f"For **{category}**, the most frequent "
                f"category is **{top_category}**, appearing "
                f"**{top_count:,} times**."
            )

    # Value insight
    price_column = business_columns.get(
        "price"
    )

    if price_column:

        series = pd.to_numeric(
            df[price_column],
            errors="coerce"
        ).dropna()

        if len(series) > 0:

            insights.append(
                f"**{price_column}** ranges from "
                f"**{format_number(series.min())}** "
                f"to **{format_number(series.max())}**, "
                f"with an average of "
                f"**{format_number(series.mean())}**."
            )

    # Rating insight
    rating_column = business_columns.get(
        "rating"
    )

    if rating_column:

        series = pd.to_numeric(
            df[rating_column],
            errors="coerce"
        ).dropna()

        if len(series) > 0:

            insights.append(
                f"The average **{rating_column}** is "
                f"**{series.mean():.2f}**."
            )

    return insights


# ============================================================
# DOWNLOAD FUNCTION
# ============================================================

def convert_df_to_csv(df):

    return df.to_csv(
        index=False
    ).encode("utf-8")


# ============================================================
# SAFE CHART HELPERS
# ============================================================

def show_chart(fig):

    if fig is not None:

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# APP HEADER
# ============================================================

st.title(
    "📊 Smart Data Analytics Platform"
)

st.markdown(
    """
    **Upload a structured CSV or Excel dataset and explore it
    through automated profiling, visualization and insights.**
    """
)

st.caption(
    "The application automatically adapts its analysis "
    "to the columns and data types detected in your dataset."
)


# ============================================================
# SIDEBAR — DATA SOURCE
# ============================================================

st.sidebar.title("📊 Smart Analytics")

st.sidebar.caption(
    "Explore, understand and analyze structured data."
)

st.sidebar.divider()

st.sidebar.subheader("📁 Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx", "xls"],
    help="Upload a structured tabular dataset."
)


# ============================================================
# LOAD DATA
# ============================================================

if uploaded_file is not None:

    data, error = load_uploaded_file(
        uploaded_file
    )

    if error:

        st.error(
            f"Could not read the uploaded file: {error}"
        )

        st.stop()

    dataset_name = uploaded_file.name

    st.sidebar.success(
        f"Loaded: {dataset_name}"
    )

else:

    try:

        data = load_default_data()

        dataset_name = "Apple iPhone Dataset"

        st.sidebar.info(
            "Using the default iPhone dataset"
        )

    except Exception as e:

        st.error(
            "The default dataset could not be loaded."
        )

        st.caption(
            f"Details: {e}"
        )

        st.stop()


# ============================================================
# VALIDATE DATA
# ============================================================

if data is None or data.empty:

    st.error(
        "The dataset is empty. Please upload a dataset "
        "containing at least one row."
    )

    st.stop()


if len(data.columns) == 0:

    st.error(
        "No columns were detected in this dataset."
    )

    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

data = clean_column_names(data)


# ============================================================
# DETECT TYPES
# ============================================================

column_types = detect_column_types(
    data
)

data = convert_detected_dates(
    data,
    column_types
)


# ============================================================
# PROFILE
# ============================================================

profile = profile_dataset(
    data,
    column_types
)


# ============================================================
# BUSINESS COLUMN DETECTION
# ============================================================

business_columns = detect_business_columns(
    data,
    column_types
)


# ============================================================
# SIDEBAR — NAVIGATION
# ============================================================

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Overview",
        "🔎 Data Explorer",
        "📊 Univariate Analysis",
        "🔗 Relationship Analysis",
        "📈 Category Analysis",
        "📅 Time Analysis",
        "🧹 Data Quality",
        "💡 Insights"
    ]
)


# ============================================================
# SIDEBAR — DATASET PROFILE
# ============================================================

st.sidebar.divider()

st.sidebar.subheader(
    "📋 Dataset Profile"
)

st.sidebar.write(
    f"**Rows:** {profile['rows']:,}"
)

st.sidebar.write(
    f"**Columns:** {profile['columns']:,}"
)

st.sidebar.write(
    f"**Numeric:** {profile['numeric_count']}"
)

st.sidebar.write(
    f"**Categorical:** {profile['categorical_count']}"
)

st.sidebar.write(
    f"**Date/Time:** {profile['datetime_count']}"
)

st.sidebar.write(
    f"**Text:** {profile['text_count']}"
)


# ============================================================
# SIDEBAR — FILTERS
# ============================================================

st.sidebar.divider()

st.sidebar.subheader(
    "🔧 Filters"
)

filtered_data = data.copy()


# ------------------------------------------------------------
# Categorical Filter
# ------------------------------------------------------------

if column_types["categorical"]:

    filter_column = st.sidebar.selectbox(
        "Filter by category",
        ["None"] + column_types["categorical"]
    )

    if filter_column != "None":

        available_values = (
            filtered_data[filter_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        available_values = sorted(
            available_values
        )

        selected_values = st.sidebar.multiselect(
            f"Select {filter_column}",
            available_values
        )

        if selected_values:

            filtered_data = filtered_data[
                filtered_data[
                    filter_column
                ]
                .astype(str)
                .isin(selected_values)
            ]


# ------------------------------------------------------------
# Numeric Filter
# ------------------------------------------------------------

if column_types["numeric"]:

    numeric_filter = st.sidebar.selectbox(
        "Numeric filter",
        ["None"] + column_types["numeric"]
    )

    if numeric_filter != "None":

        numeric_series = pd.to_numeric(
            filtered_data[numeric_filter],
            errors="coerce"
        ).dropna()

        if len(numeric_series) > 0:

            minimum = float(
                numeric_series.min()
            )

            maximum = float(
                numeric_series.max()
            )

            if minimum != maximum:

                selected_range = st.sidebar.slider(
                    f"{numeric_filter} range",
                    min_value=minimum,
                    max_value=maximum,
                    value=(minimum, maximum)
                )

                converted_numeric = pd.to_numeric(
                    filtered_data[numeric_filter],
                    errors="coerce"
                )

                filtered_data = filtered_data[
                    converted_numeric.between(
                        selected_range[0],
                        selected_range[1]
                    )
                ]


# ============================================================
# FILTER STATUS
# ============================================================

if len(filtered_data) != len(data):

    st.sidebar.success(
        f"Filter active: {len(filtered_data):,} "
        f"of {len(data):,} rows"
    )


# ============================================================
# EMPTY FILTER RESULT
# ============================================================

if filtered_data.empty:

    st.warning(
        "No rows match the selected filters."
    )

    st.info(
        "Try selecting different category values "
        "or expanding the numeric range."
    )

    st.stop()


# ============================================================
# OVERVIEW PAGE
# ============================================================

if page == "🏠 Overview":

    st.header(
        "Dataset Overview"
    )

    st.markdown(
        '<p class="section-description">'
        f"Currently analyzing <strong>{dataset_name}</strong>. "
        "Use the navigation panel to explore different analytical views."
        "</p>",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Main KPIs
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Rows",
            f"{len(filtered_data):,}"
        )

    with col2:

        st.metric(
            "Columns",
            f"{len(filtered_data.columns):,}"
        )

    with col3:

        missing_count = int(
            filtered_data.isnull().sum().sum()
        )

        st.metric(
            "Missing Cells",
            f"{missing_count:,}"
        )

    with col4:

        duplicate_count = int(
            filtered_data.duplicated().sum()
        )

        st.metric(
            "Duplicate Rows",
            f"{duplicate_count:,}"
        )

    st.divider()

    # --------------------------------------------------------
    # Detected Business Metrics
    # --------------------------------------------------------

    st.subheader(
        "🎯 Detected Business Metrics"
    )

    st.caption(
        "These metrics are automatically identified from "
        "common column naming patterns."
    )

    price_column = business_columns.get(
        "price"
    )

    rating_column = business_columns.get(
        "rating"
    )

    quantity_column = business_columns.get(
        "quantity"
    )

    discount_column = business_columns.get(
        "discount"
    )

    metric_columns = []

    if price_column:

        metric_columns.append(
            ("Average Value", price_column)
        )

    if rating_column:

        metric_columns.append(
            ("Average Rating", rating_column)
        )

    if quantity_column:

        metric_columns.append(
            ("Total Quantity", quantity_column)
        )

    if discount_column:

        metric_columns.append(
            ("Average Discount", discount_column)
        )

    if metric_columns:

        cols = st.columns(
            min(len(metric_columns), 4)
        )

        for index, (label, column) in enumerate(
            metric_columns[:4]
        ):

            series = pd.to_numeric(
                filtered_data[column],
                errors="coerce"
            ).dropna()

            if len(series) == 0:
                continue

            with cols[index]:

                if "Rating" in label:

                    value = (
                        f"{series.mean():.2f}"
                    )

                elif "Discount" in label:

                    value = (
                        f"{series.mean():.2f}%"
                    )

                elif "Quantity" in label:

                    value = format_number(
                        series.sum()
                    )

                else:

                    value = format_number(
                        series.mean()
                    )

                st.metric(
                    label,
                    value
                )

    else:

        st.info(
            "No common business metrics such as price, "
            "rating, quantity or discount were automatically detected."
        )

    st.divider()

    # --------------------------------------------------------
    # Detected Structure
    # --------------------------------------------------------

    st.subheader(
        "🧠 Detected Data Structure"
    )

    type_col1, type_col2, type_col3, type_col4 = (
        st.columns(4)
    )

    with type_col1:

        st.metric(
            "Numeric Columns",
            len(column_types["numeric"])
        )

    with type_col2:

        st.metric(
            "Categorical Columns",
            len(column_types["categorical"])
        )

    with type_col3:

        st.metric(
            "Date Columns",
            len(column_types["datetime"])
        )

    with type_col4:

        st.metric(
            "Text Columns",
            len(column_types["text"])
        )

    # --------------------------------------------------------
    # Preview
    # --------------------------------------------------------

    st.subheader(
        "👀 Dataset Preview"
    )

    st.dataframe(
        filtered_data.head(10),
        use_container_width=True,
        height=350
    )

    # --------------------------------------------------------
    # Quick Insights
    # --------------------------------------------------------

    st.subheader(
        "💡 Quick Insights"
    )

    insights = generate_insights(
        filtered_data,
        column_types,
        business_columns
    )

    if insights:

        for insight in insights[:6]:

            st.markdown(
                f"""
                <div class="insight-box">
                    {insight}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "No automated insights could be generated."
        )


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "🔎 Data Explorer":

    st.header(
        "🔎 Data Explorer"
    )

    st.markdown(
        '<p class="section-description">'
        "Inspect the dataset structure, column information "
        "and filtered records."
        "</p>",
        unsafe_allow_html=True
    )

    # Shape

    st.subheader(
        "Dataset Shape"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Rows",
            f"{len(filtered_data):,}"
        )

    with c2:

        st.metric(
            "Columns",
            f"{len(filtered_data.columns):,}"
        )

    # Column information

    st.subheader(
        "Column Information"
    )

    column_info = pd.DataFrame(
        {
            "Column": filtered_data.columns,
            "Data Type": [
                str(
                    filtered_data[col].dtype
                )
                for col in filtered_data.columns
            ],
            "Missing Values": [
                int(
                    filtered_data[col].isnull().sum()
                )
                for col in filtered_data.columns
            ],
            "Unique Values": [
                int(
                    filtered_data[col].nunique(
                        dropna=True
                    )
                )
                for col in filtered_data.columns
            ]
        }
    )

    st.dataframe(
        column_info,
        use_container_width=True,
        hide_index=True
    )

    # Complete dataset

    st.subheader(
        "Complete Dataset"
    )

    st.dataframe(
        filtered_data,
        use_container_width=True,
        height=500
    )

    # Download

    st.download_button(
        "⬇️ Download Filtered Dataset",
        data=convert_df_to_csv(
            filtered_data
        ),
        file_name="filtered_dataset.csv",
        mime="text/csv"
    )


# ============================================================
# UNIVARIATE ANALYSIS
# ============================================================

elif page == "📊 Univariate Analysis":

    st.header(
        "📊 Univariate Analysis"
    )

    st.markdown(
        '<p class="section-description">'
        "Understand the distribution and descriptive statistics "
        "of individual numeric variables."
        "</p>",
        unsafe_allow_html=True
    )

    if not column_types["numeric"]:

        st.info(
            "No numeric columns were detected for numerical analysis."
        )

    else:

        selected_numeric = st.selectbox(
            "Select a numeric column",
            column_types["numeric"]
        )

        series = pd.to_numeric(
            filtered_data[selected_numeric],
            errors="coerce"
        ).dropna()

        if len(series) == 0:

            st.warning(
                "This column does not contain usable numeric values."
            )

        else:

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "Mean",
                    format_number(
                        series.mean()
                    )
                )

            with c2:

                st.metric(
                    "Median",
                    format_number(
                        series.median()
                    )
                )

            with c3:

                st.metric(
                    "Minimum",
                    format_number(
                        series.min()
                    )
                )

            with c4:

                st.metric(
                    "Maximum",
                    format_number(
                        series.max()
                    )
                )

            st.divider()

            chart_type = st.radio(
                "Visualization",
                [
                    "Histogram",
                    "Box Plot"
                ],
                horizontal=True
            )

            if chart_type == "Histogram":

                chart_data = pd.DataFrame(
                    {
                        selected_numeric: series
                    }
                )

                fig = px.histogram(
                    chart_data,
                    x=selected_numeric,
                    nbins=30,
                    title=(
                        f"Distribution of "
                        f"{selected_numeric}"
                    )
                )

            else:

                chart_data = pd.DataFrame(
                    {
                        selected_numeric: series
                    }
                )

                fig = px.box(
                    chart_data,
                    y=selected_numeric,
                    title=(
                        f"Box Plot of "
                        f"{selected_numeric}"
                    )
                )

            show_chart(fig)

            st.subheader(
                "Descriptive Statistics"
            )

            stats = (
                series
                .describe()
                .to_frame(
                    name="Value"
                )
            )

            st.dataframe(
                stats,
                use_container_width=True
            )


# ============================================================
# RELATIONSHIP ANALYSIS
# ============================================================

elif page == "🔗 Relationship Analysis":

    st.header(
        "🔗 Relationship Analysis"
    )

    st.markdown(
        '<p class="section-description">'
        "Examine relationships between numeric variables "
        "using correlation and scatter plots."
        "</p>",
        unsafe_allow_html=True
    )

    if len(column_types["numeric"]) < 2:

        st.info(
            "At least two numeric columns are required "
            "for relationship analysis."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            x_column = st.selectbox(
                "X-axis",
                column_types["numeric"]
            )

        with col2:

            default_y = (
                column_types["numeric"][1]
                if len(column_types["numeric"]) > 1
                else column_types["numeric"][0]
            )

            y_column = st.selectbox(
                "Y-axis",
                column_types["numeric"],
                index=column_types["numeric"].index(
                    default_y
                )
            )

        relationship_data = (
            filtered_data[
                [x_column, y_column]
            ]
            .copy()
        )

        relationship_data[x_column] = pd.to_numeric(
            relationship_data[x_column],
            errors="coerce"
        )

        relationship_data[y_column] = pd.to_numeric(
            relationship_data[y_column],
            errors="coerce"
        )

        relationship_data = (
            relationship_data
            .dropna()
        )

        if len(relationship_data) < 2:

            st.warning(
                "Not enough valid observations "
                "for this comparison."
            )

        else:

            correlation = relationship_data[
                x_column
            ].corr(
                relationship_data[y_column]
            )

            st.metric(
                "Pearson Correlation",
                f"{correlation:.3f}"
            )

            st.caption(
                "Correlation indicates the strength and "
                "direction of a linear association. "
                "It does not prove causation."
            )

            # Scatter plot without external OLS dependency
            fig = px.scatter(
                relationship_data,
                x=x_column,
                y=y_column,
                title=(
                    f"{x_column} vs {y_column}"
                ),
                trendline=None
            )

            show_chart(fig)

            st.subheader(
                "Correlation Matrix"
            )

            correlation_matrix = (
                filtered_data[
                    column_types["numeric"]
                ]
                .apply(
                    pd.to_numeric,
                    errors="coerce"
                )
                .corr()
            )

            if not correlation_matrix.empty:

                fig_corr = px.imshow(
                    correlation_matrix,
                    text_auto=".2f",
                    aspect="auto",
                    title="Numeric Correlation Matrix"
                )

                show_chart(fig_corr)

            else:

                st.info(
                    "A correlation matrix could not be generated."
                )


# ============================================================
# CATEGORY ANALYSIS
# ============================================================

elif page == "📈 Category Analysis":

    st.header(
        "📈 Category Analysis"
    )

    st.markdown(
        '<p class="section-description">'
        "Compare category frequency and numeric metrics "
        "across groups."
        "</p>",
        unsafe_allow_html=True
    )

    if not column_types["categorical"]:

        st.info(
            "No suitable categorical columns were detected."
        )

    else:

        category_column = st.selectbox(
            "Select category column",
            column_types["categorical"]
        )

        counts = (
            filtered_data[
                category_column
            ]
            .fillna("Missing")
            .astype(str)
            .value_counts()
            .head(20)
            .reset_index()
        )

        counts.columns = [
            category_column,
            "Count"
        ]

        fig = px.bar(
            counts,
            x="Count",
            y=category_column,
            orientation="h",
            title=(
                f"Top Categories by "
                f"{category_column}"
            )
        )

        fig.update_layout(
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )

        show_chart(fig)

        st.subheader(
            "Category Summary"
        )

        if column_types["numeric"]:

            numeric_summary_column = (
                st.selectbox(
                    "Compare category using numeric column",
                    column_types["numeric"]
                )
            )

            category_summary = (
                filtered_data
                .assign(
                    _numeric_value=pd.to_numeric(
                        filtered_data[
                            numeric_summary_column
                        ],
                        errors="coerce"
                    )
                )
                .groupby(
                    category_column,
                    dropna=False
                )["_numeric_value"]
                .agg(
                    [
                        "count",
                        "mean",
                        "median",
                        "min",
                        "max"
                    ]
                )
                .reset_index()
                .sort_values(
                    "mean",
                    ascending=False
                )
            )

            category_summary = (
                category_summary
                .rename(
                    columns={
                        "_numeric_value":
                            numeric_summary_column
                    }
                )
            )

            st.dataframe(
                category_summary,
                use_container_width=True,
                hide_index=True
            )

            chart_summary = (
                category_summary
                .dropna(
                    subset=["mean"]
                )
                .head(15)
            )

            if not chart_summary.empty:

                fig2 = px.bar(
                    chart_summary,
                    x=category_column,
                    y="mean",
                    title=(
                        f"Average "
                        f"{numeric_summary_column} "
                        f"by {category_column}"
                    )
                )

                show_chart(fig2)

        else:

            st.info(
                "No numeric columns are available "
                "for category comparison."
            )


# ============================================================
# TIME ANALYSIS
# ============================================================

elif page == "📅 Time Analysis":

    st.header(
        "📅 Time Analysis"
    )

    st.markdown(
        '<p class="section-description">'
        "Explore record volume and numeric metrics over time "
        "when date/time information is available."
        "</p>",
        unsafe_allow_html=True
    )

    if not column_types["datetime"]:

        st.info(
            "No date/time column was automatically detected "
            "in this dataset."
        )

        st.caption(
            "If your dataset contains dates stored as ordinary "
            "text, use a clear date/time column name such as "
            "'Date', 'Order Date', 'Timestamp' or 'Year'."
        )

    else:

        date_column = st.selectbox(
            "Select date/time column",
            column_types["datetime"]
        )

        time_data = filtered_data.copy()

        time_data[date_column] = pd.to_datetime(
            time_data[date_column],
            errors="coerce"
        )

        time_data = time_data.dropna(
            subset=[date_column]
        )

        if time_data.empty:

            st.warning(
                "No valid dates were found."
            )

        else:

            time_data["Month"] = (
                time_data[date_column]
                .dt.to_period("M")
                .astype(str)
            )

            st.subheader(
                "Records Over Time"
            )

            time_counts = (
                time_data
                .groupby("Month")
                .size()
                .reset_index(
                    name="Records"
                )
            )

            fig = px.line(
                time_counts,
                x="Month",
                y="Records",
                markers=True,
                title="Number of Records Over Time"
            )

            show_chart(fig)

            if column_types["numeric"]:

                time_numeric = st.selectbox(
                    "Analyze numeric metric over time",
                    column_types["numeric"]
                )

                time_data[
                    time_numeric
                ] = pd.to_numeric(
                    time_data[time_numeric],
                    errors="coerce"
                )

                time_metric = (
                    time_data
                    .groupby("Month")[
                        time_numeric
                    ]
                    .mean()
                    .reset_index()
                )

                if not time_metric.empty:

                    fig2 = px.line(
                        time_metric,
                        x="Month",
                        y=time_numeric,
                        markers=True,
                        title=(
                            f"Average "
                            f"{time_numeric} "
                            f"Over Time"
                        )
                    )

                    show_chart(fig2)

            else:

                st.info(
                    "No numeric columns are available "
                    "for metric-over-time analysis."
                )


# ============================================================
# DATA QUALITY
# ============================================================

elif page == "🧹 Data Quality":

    st.header(
        "🧹 Data Quality"
    )

    st.markdown(
        '<p class="section-description">'
        "Assess missing values, duplicates, numeric validity "
        "and automatically detected data types."
        "</p>",
        unsafe_allow_html=True
    )

    quality_col1, quality_col2, quality_col3, quality_col4 = (
        st.columns(4)
    )

    with quality_col1:

        st.metric(
            "Rows",
            f"{len(data):,}"
        )

    with quality_col2:

        st.metric(
            "Columns",
            f"{len(data.columns):,}"
        )

    with quality_col3:

        st.metric(
            "Missing Cells",
            f"{int(data.isnull().sum().sum()):,}"
        )

    with quality_col4:

        st.metric(
            "Duplicate Rows",
            f"{int(data.duplicated().sum()):,}"
        )

    st.divider()

    # --------------------------------------------------------
    # Missing Values
    # --------------------------------------------------------

    st.subheader(
        "Missing Value Analysis"
    )

    missing_table = pd.DataFrame(
        {
            "Column": data.columns,
            "Missing Values": [
                int(
                    data[col].isnull().sum()
                )
                for col in data.columns
            ]
        }
    )

    missing_table["Missing %"] = (
        missing_table["Missing Values"]
        / len(data)
        * 100
    ).round(2)

    missing_table = (
        missing_table
        .sort_values(
            "Missing %",
            ascending=False
        )
    )

    st.dataframe(
        missing_table,
        use_container_width=True,
        hide_index=True
    )

    missing_nonzero = missing_table[
        missing_table["Missing Values"] > 0
    ]

    if not missing_nonzero.empty:

        fig = px.bar(
            missing_nonzero,
            x="Column",
            y="Missing Values",
            title="Missing Values by Column"
        )

        show_chart(fig)

    else:

        st.success(
            "✅ No missing values detected."
        )

    # --------------------------------------------------------
    # Duplicate Analysis
    # --------------------------------------------------------

    st.subheader(
        "Duplicate Analysis"
    )

    duplicates = int(
        data.duplicated().sum()
    )

    if duplicates == 0:

        st.success(
            "✅ No completely duplicated rows detected."
        )

    else:

        st.warning(
            f"{duplicates:,} duplicate rows detected."
        )

        duplicate_rows = data[
            data.duplicated(
                keep=False
            )
        ]

        st.dataframe(
            duplicate_rows,
            use_container_width=True
        )

    # --------------------------------------------------------
    # Numeric Validation
    # --------------------------------------------------------

    st.subheader(
        "Numeric Column Validation"
    )

    if column_types["numeric"]:

        numeric_quality = []

        for column in column_types["numeric"]:

            original_series = data[column]

            series = pd.to_numeric(
                original_series,
                errors="coerce"
            )

            invalid_count = int(
                series.isna().sum()
                - original_series.isna().sum()
            )

            numeric_quality.append(
                {
                    "Column": column,
                    "Min": series.min(),
                    "Max": series.max(),
                    "Mean": series.mean(),
                    "Median": series.median(),
                    "Invalid / Non-numeric":
                        max(0, invalid_count)
                }
            )

        numeric_quality_df = pd.DataFrame(
            numeric_quality
        )

        st.dataframe(
            numeric_quality_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No numeric columns detected."
        )

    # --------------------------------------------------------
    # Detected Types
    # --------------------------------------------------------

    st.subheader(
        "Detected Column Types"
    )

    detected_types = []

    for column in data.columns:

        if column in column_types["numeric"]:

            detected_type = "Numeric"

        elif column in column_types["categorical"]:

            detected_type = "Categorical"

        elif column in column_types["datetime"]:

            detected_type = "Date / Time"

        elif column in column_types["boolean"]:

            detected_type = "Boolean"

        else:

            detected_type = "Text"

        detected_types.append(
            {
                "Column": column,
                "Detected Type": detected_type
            }
        )

    st.dataframe(
        pd.DataFrame(detected_types),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# INSIGHTS PAGE
# ============================================================

elif page == "💡 Insights":

    st.header(
        "💡 Automated Data Insights"
    )

    st.markdown(
        '<p class="section-description">'
        "These observations are generated from the structure "
        "and values present in the current dataset."
        "</p>",
        unsafe_allow_html=True
    )

    insights = generate_insights(
        filtered_data,
        column_types,
        business_columns
    )

    if insights:

        for number, insight in enumerate(
            insights,
            start=1
        ):

            st.markdown(
                f"""
                <div class="insight-box">
                    <strong>Insight {number}</strong>
                    <br><br>
                    {insight}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "No automated insights could be generated "
            "for this dataset."
        )

    st.divider()

    st.subheader(
        "🎯 Detected Analytical Opportunities"
    )

    opportunities = []

    if column_types["numeric"]:

        opportunities.append(
            "Numerical distributions, summary statistics "
            "and relationships can be analyzed."
        )

    if column_types["categorical"]:

        opportunities.append(
            "Category-level comparisons and frequency "
            "analysis are available."
        )

    if column_types["datetime"]:

        opportunities.append(
            "Time-based trends can be explored."
        )

    if len(column_types["numeric"]) >= 2:

        opportunities.append(
            "Correlation and scatter-plot analysis are "
            "available between numeric variables."
        )

    if profile["missing_cells"] > 0:

        opportunities.append(
            "Data cleaning should be considered because "
            "missing values were detected."
        )

    if profile["duplicate_rows"] > 0:

        opportunities.append(
            "Duplicate records should be investigated."
        )

    if not opportunities:

        opportunities.append(
            "The dataset has limited automatically "
            "detected analytical structure."
        )

    for opportunity in opportunities:

        st.markdown(
            f"- {opportunity}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        📊 <strong>Smart Data Analytics Platform</strong>
        <br>
        Automated exploratory analysis for structured tabular data
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Note: Automated insights describe patterns in the dataset. "
    "They should be interpreted in the context of the dataset "
    "and do not establish causation."
)