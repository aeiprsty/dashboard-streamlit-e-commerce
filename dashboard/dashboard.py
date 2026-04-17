import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style='whitegrid')
palette = sns.light_palette("#79C", n_colors=10, reverse=True)

all_df = pd.read_csv('dashboard/main_data.csv')
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

st.title("E-Commerce Data Analysis Dashboard")

min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

date_range = st.date_input(
    label="Date Filter",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    label_visibility="collapsed"
)

if len(date_range) != 2:
    st.info("Select start and end dates to view data")
    st.stop()

start_date, end_date = date_range

filtered_df = all_df[
    (all_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
    (all_df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
]


tab1, tab2, tab3 = st.tabs(["Customer Segmentation (RFM)", "Top 10 Product Categories", "Delivery Performance vs Customer Rating"])

with tab1:
    st.header("Customer Segmentation (RFM)")

    try:
        if filtered_df.empty:
            st.warning("There is no data in this date range")

        if filtered_df['customer_id'].nunique() < 5:
            st.warning("Too little customer data for RFM")

        reference_date = filtered_df['order_purchase_timestamp'].max()

        rfm = filtered_df.groupby('customer_id').agg({
            'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
            'order_id': 'count',
            'price': 'sum'
        }).reset_index()

        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        rfm = rfm.dropna(subset=['recency'])

        rfm['R_score'] = pd.qcut(rfm['recency'], 4, labels=[4,3,2,1], duplicates='drop')
        rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1,2,3,4], duplicates='drop')
        rfm['M_score'] = pd.qcut(rfm['monetary'], 4, labels=[1,2,3,4], duplicates='drop')

        rfm['RFM_score'] = rfm[['R_score','F_score','M_score']].astype(int).sum(axis=1)

        def segment(x):
            if x >= 9:
                return "Best Customer"
            elif x >= 7:
                return "Loyal Customer"
            elif x >= 5:
                return "Potential Customer"
            else:
                return "Low Value Customer"

        rfm['segment'] = rfm['RFM_score'].apply(segment)

        segment_counts = rfm['segment'].value_counts().reset_index()
        segment_counts.columns = ['segment', 'count']

        fig1, ax1 = plt.subplots()
        sns.barplot(data=segment_counts, x='count', y='segment', palette=palette, ax=ax1)

        ax1.set_xlabel("Number of Customers")
        ax1.set_ylabel("Customer Segment")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    except Exception as e:
        st.warning("Failed to display RFM, try changing the date range")

with tab2:
    st.header("Top 10 Product Categories")

    try:
        if filtered_df.empty:
            st.warning("There is no product data in this date range")

        if filtered_df['product_category_name_english'].nunique() < 10:
            st.warning("Too little product data")

        product_category = filtered_df.groupby(
            'product_category_name_english'
        )['order_item_id'].count().reset_index()

        product_category = product_category.sort_values(
            by='order_item_id',
            ascending=False
        ).head(10)

        fig2, ax2 = plt.subplots()
        sns.barplot(data=product_category, x='order_item_id', y='product_category_name_english', palette=palette, ax=ax2)

        ax2.set_xlabel("Total Orders")
        ax2.set_ylabel("Product Category")
        st.pyplot(fig2)

    except Exception as e:
        st.warning("Failed to display product data")

with tab3:
    st.header("Delivery Performance vs Customer Rating")

    try:
        delivery_review = filtered_df.groupby('delivery_status')['review_score'].mean()
        delivery_review = delivery_review.reindex(['Late', 'On Time'], fill_value=0).reset_index()

        if delivery_review.empty:
            st.warning("No delivery data")

        fig3, ax3 = plt.subplots()
        sns.barplot(data=delivery_review, x='delivery_status', y='review_score', palette=["#FF6B6B", "#79C"], ax=ax3)

        ax3.set_xlabel("Delivery Status")
        ax3.set_ylabel("Average Rating")
        ax3.set_ylim(0, 5)
        st.pyplot(fig3)

    except Exception as e:
        st.warning("Failed to display delivery data")