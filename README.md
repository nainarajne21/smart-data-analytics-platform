# 📊 Smart Data Analytics Platform

An interactive Streamlit-based analytics platform that allows users to upload structured CSV or Excel datasets and automatically explore, analyze, visualize, and understand their data.

The application dynamically detects column types, identifies common business metrics, provides exploratory analysis, performs relationship and category analysis, evaluates data quality, and generates automated data-driven insights.

## 🚀 Live Demo

**Coming soon**

## 📌 Project Overview

Data analysis often requires repetitive steps such as understanding dataset structure, checking data quality, exploring distributions, identifying relationships, and creating visualizations.

This project provides an interactive solution that brings these tasks together into a single web application.

Users can upload a structured CSV/Excel dataset and explore the data without manually writing separate analysis code for every dataset.

The platform was initially developed around an iPhone product dataset and was then redesigned into a more general-purpose structured-data analytics application.

## ✨ Key Features

### 📁 Dataset Upload

* Upload CSV, XLSX, and XLS files
* Automatic column-name cleaning
* Supports different dataset structures

### 🔍 Automatic Dataset Profiling

The application automatically identifies:

* Number of rows and columns
* Missing values
* Duplicate records
* Numeric columns
* Categorical columns
* Date/time columns
* Text columns
* Boolean columns

### 📊 Exploratory Data Analysis

Users can perform:

* Descriptive statistics
* Mean, median, minimum and maximum analysis
* Histograms
* Box plots
* Frequency analysis
* Category-level comparisons

### 🔗 Relationship Analysis

Analyze relationships between numerical variables using:

* Pearson correlation
* Scatter plots
* Correlation matrix

> Correlation is used to identify relationships between variables and does not imply causation.

### 📈 Category Analysis

Explore categorical variables through:

* Category frequency analysis
* Top categories
* Numeric summaries by category
* Average metric comparisons

### 📅 Time Analysis

For datasets containing date/time information, the application can:

* Identify date columns
* Analyze records over time
* Analyze average numerical metrics over time
* Group data by month

### 🧹 Data Quality Analysis

The application checks for:

* Missing values
* Duplicate rows
* Numeric conversion issues
* Detected data types
* Dataset completeness

### 💡 Automated Insights

The platform generates responsible analytical observations based on the uploaded dataset, including:

* Dataset size
* Missing-data observations
* Duplicate records
* Numeric ranges and averages
* Dominant categories
* Rating/score statistics when available
* Potential analytical opportunities

### 🎛️ Interactive Filtering

Users can dynamically filter datasets using:

* Categorical filters
* Numeric range filters

All supported analysis updates based on the filtered dataset.

### 📥 Export

Users can download the currently filtered dataset as a CSV file.

---

## 🛠️ Technology Stack

| Technology | Purpose                               |
| ---------- | ------------------------------------- |
| Python     | Data processing and application logic |
| Pandas     | Data manipulation and analysis        |
| Streamlit  | Interactive web application           |
| Plotly     | Interactive data visualization        |
| OpenPyXL   | Excel file processing                 |

---

## 🏗️ Application Architecture

```text
User
  ↓
Upload CSV / Excel
  ↓
Data Loading
  ↓
Column Cleaning
  ↓
Automatic Data Type Detection
  ↓
Dataset Profiling
  ↓
Interactive Filtering
  ↓
 ┌───────────────────────────────┐
 │ Exploratory Analysis          │
 │ Relationship Analysis         │
 │ Category Analysis             │
 │ Time Analysis                 │
 │ Data Quality                  │
 │ Automated Insights            │
 └───────────────────────────────┘
  ↓
Interactive Visualizations
  ↓
Filtered Dataset Export
```

---

## 📂 Project Structure

```text
iphone-product-analytics/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── assets/
│   ├── overview.png
│   ├── data-explorer.png
│   ├── relationship.png
│   └── insights.png
│
└── data/
    └── README.md
```

> The `assets` and `data` folders can be added when preparing the final GitHub repository.

---

## ▶️ Run the Project Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the project

```bash
cd iphone-product-analytics
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 📊 Example Dataset

The application was initially developed and tested using an iPhone product dataset containing information such as:

* Product Name
* Brand
* Sale Price
* MRP
* Discount Percentage
* Number of Ratings
* Number of Reviews
* Star Rating
* RAM

The platform was subsequently generalized so that users can upload other structured CSV or Excel datasets.

---

## 🎯 Skills Demonstrated

This project demonstrates practical skills in:

* Python
* Pandas
* Exploratory Data Analysis
* Data Cleaning
* Data Profiling
* Data Visualization
* Statistical Analysis
* Correlation Analysis
* Feature/column type detection
* Interactive dashboards
* Streamlit application development
* Excel/CSV data handling
* Analytical thinking
* Data-driven insight generation
* Git/GitHub project management

---

## 🔮 Future Improvements

Possible future improvements include:

* Advanced statistical testing
* Additional visualization options
* More sophisticated anomaly detection
* Automated report generation
* Machine learning-based analysis
* Natural-language querying of datasets
* Database connectivity
* Authentication and multi-user support

These are potential extensions and are not required for the current version.

---

## 👩‍💻 Author

**Naira Rajne**

B.Tech Artificial Intelligence & Machine Learning

Interested in **Data Analytics, Artificial Intelligence, and Data-driven applications**.

### 🔗 Links

* GitHub: `https://github.com/nainarajne21`
* LinkedIn: *Add your LinkedIn profile here*

---

## ⭐ Project Status

**Completed — Portfolio Ready**

The current version focuses on providing a practical, reusable analytics workflow for structured CSV and Excel datasets.
