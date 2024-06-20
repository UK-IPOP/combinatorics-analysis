from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from rich.console import Console

st.set_page_config(
    page_title="Combinations Analysis",
    layout="centered",
)

console = Console()

st.header("Combinations", divider=True)


# TODO: make this "smartly" load files based on extension user uploads
# likely limited to excel, csv, and parquet... if the two former, data
# will need to be converted (dates, strings, etc)
# NOTE: cache loading for 1 hour if fpath is the same
@st.cache_data(ttl=3600, show_spinner=True, max_entries=2)
def load_data(fpath: Path) -> pd.DataFrame:
    """Load a table from file.

    Loads a data file with pyarrow backend.

    Args:
        fpath (Path): Path to load from

    Returns:
        pd.DataFrame: pandas dataframe of file.
    """
    # read this way for better dtypes
    # this also allows us, for now, to skip cleaning the data
    # since we assume it is clean, AND skip data type transfer
    # i.e. we do not need to call "pd.to_datetime()" now :)
    return pd.read_parquet(
        fpath,
        engine="pyarrow",
        dtype_backend="pyarrow",
    )


# NOTE: cache one-hot encoding
@st.cache_data(ttl=3600, show_spinner=True, max_entries=3)
def encode_table(
    table: pd.DataFrame,
    one_hot_column: str,
) -> pd.DataFrame:
    """One hot encode the column and add its resulting sparse table to the orginal table.

    Args:
        table (pd.DataFrame): Table to utilize
        one_hot_column (str): Column to one-hot encode

    Returns:
        pd.DataFrame: One hot encoded dataframe with `one_hot_column` removed.
    """
    dummy_data = pd.get_dummies(
        table[one_hot_column].str.upper(),
    )
    return pd.concat([table.drop(columns=[one_hot_column]), dummy_data], axis=1)


@st.cache_data(ttl=3600, show_spinner=True, max_entries=3)
def group_data(table: pd.DataFrame, groupby_cols: list[str]) -> pd.DataFrame:
    """Aggregate the table by groupby_cols and summing the remaining columns

    Expects you to have dropped the columns you do not want (or cannot be) summed.

    This leaves the `groupby_cols` as indices so that they are excluded from later
    row/column math.

    Args:
        table (pd.DataFrame): The table to aggregate
        groupby_cols (list[str]): The columns to aggregate on. All remaining columns will be summed.

    Returns:
        pd.DataFrame: Aggregated table data

    """
    g = table.groupby(groupby_cols).sum()
    return g > 0


# NOTE: do this way for now to allow user uploading later
hardcoded_path = Path().cwd() / "data" / "combinations-diagnoses.parquet"
df = load_data(fpath=hardcoded_path)

all_columns: list[str] = df.columns.tolist()

st.dataframe(df, use_container_width=True, hide_index=True)
st.caption("Sample table")


group_col = st.selectbox(
    label="Grouping Column",
    help="Column to aggregate on",
    options=all_columns,
    index=2,
)
value_col = st.selectbox(
    label="Value Column",
    help="Column to analyze",
    options=all_columns,
    index=0,
)
st.caption("Currently we ignore date column")
# TODO: we will also need a thing for the date aggreagtion method or something
date_col = st.selectbox(
    label="Date Column",
    options=list(df.columns),
    disabled=True,
    index=1,
)


with st.status(label="Processing data...", expanded=True) as status:
    st.write("Encoding data...")
    sparse_df = encode_table(table=df, one_hot_column=value_col)
    # Remove columns not in groupby that still exist from original table
    # In our example this is the `visit` and `timestamp` columns for now
    droppable: set[str] = set(all_columns)
    droppable.discard(group_col)
    droppable.discard(value_col)
    # after this `sparse_df` should only have the group columns and the one-hot encoded columns
    sparse_df = sparse_df.drop(columns=droppable)
    # Remove columns not in groupby that still exist from original table
    st.write("Aggregating data...")
    grouped = group_data(table=sparse_df, groupby_cols=[group_col])
    status.update(label="Processed data", expanded=False, state="complete")
st.success("Data encoded.")


with st.form("Predicates"):
    predicates = st.multiselect(
        label="Predicates",
        options=sorted(grouped.columns.tolist()),
        default=None,
        placeholder="Choose predicate term(s)",
    )
    submit = st.form_submit_button(
        "Submit",
        help="Submit this predicate query",
        type="primary",
    )

# form submitted / clicked
if submit:
    # filter where all of the predicates are true
    subset: pd.DataFrame = grouped.loc[(grouped[predicates] > 0).all(axis=1)]
    probabilities = subset.sum(axis=0) / subset.shape[0]
    non_zero_probabilities = probabilities.loc[probabilities > 0]
    tbl: pd.DataFrame = non_zero_probabilities.reset_index()
    tbl.columns = ["Label", "Probability"]
    tbl.sort_values("Probability", ascending=False, inplace=True)
    st.dataframe(
        tbl,
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Conditional Probabilities table")

    fig = px.bar(
        # top 20
        tbl.head(20),
        x="Probability",
        y="Label",
        orientation="h",
    )
    st.plotly_chart(fig, use_container_width=True)
