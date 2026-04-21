import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.ticker import FuncFormatter

sns.set_theme(style='whitegrid')
palette = sns.light_palette("#79C", n_colors=10, reverse=True)

all_df = pd.read_csv('dashboard/main_data.csv')

date_cols = [
    'order_purchase_timestamp',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]

for col in date_cols:
    all_df[col] = pd.to_datetime(all_df[col], errors='coerce')

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
    st.info("Select start and end dates")
    st.stop()

start_date, end_date = date_range

filtered_df = all_df[
    (all_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
    (all_df['order_purchase_timestamp'] < pd.to_datetime(end_date) + pd.Timedelta(days=1))
]

formatter = FuncFormatter(lambda x, _: f'{int(x):,}'.replace(',', '.'))

tab1, tab2, tab3 = st.tabs([
    "Customer Segmentation (RFM)",
    "Top 10 Product Categories",
    "Delivery Performance vs Customer Rating"
])

with tab1:
    st.header("Customer Segmentation (RFM)")

    try:
        if filtered_df.empty:
            st.warning("No data available")

        if filtered_df['customer_id'].nunique() < 5:
            st.warning("Too little customer data for RFM")

        rfm_df = filtered_df.dropna(subset=['customer_unique_id'])

        order_level = rfm_df.groupby('order_id').agg({
            'customer_unique_id': 'first',
            'order_purchase_timestamp': 'first',
            'payment_value': 'sum'
        }).reset_index()

        reference_date = order_level['order_purchase_timestamp'].max()

        rfm = order_level.groupby('customer_unique_id').agg({
            'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
            'order_id': 'nunique',
            'payment_value': 'sum'
        }).reset_index()

        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        rfm = rfm.dropna()

        rfm['R_score'] = pd.qcut(rfm['recency'], 4, labels=[4,3,2,1], duplicates='drop')
        rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1,2,3,4], duplicates='drop')
        rfm['M_score'] = pd.qcut(rfm['monetary'], 4, labels=[1,2,3,4], duplicates='drop')

        rfm['RFM_score'] = rfm[['R_score','F_score','M_score']].astype(int).sum(axis=1)

        def segment(x):
            if x >= 9:
                return "Best Customer"
            elif x >= 6:
                return "Loyal Customer"
            elif x >= 4:
                return "Potential Customer"
            else:
                return "Low Value Customer"

        rfm['segment'] = rfm['RFM_score'].apply(segment)

        segment_counts = rfm['segment'].value_counts().reset_index()
        segment_counts.columns = ['segment', 'count']

        fig1, ax1 = plt.subplots()
        sns.barplot(data=segment_counts, x='count', y='segment', palette=palette, ax=ax1)

        for p in ax1.patches:
            width = p.get_width()
            ax1.annotate(
                f'{int(width):,}'.replace(',', '.'),
                (width, p.get_y() + p.get_height()/2),
                ha='left',
                va='center'
            )

        ax1.xaxis.set_major_formatter(formatter)

        max_val = segment_counts['count'].max()
        ax1.set_xlim(0, max_val * 1.1)

        ax1.set_xlabel("Number of Customers")
        ax1.set_ylabel("Customer Segment")
        ax1.grid(False)

        st.pyplot(fig1)

    except:
        st.warning("Failed to display RFM")

with tab2:
    st.header("Top 10 Product Categories")

    try:
        if filtered_df.empty:
            st.warning("No product data")

        product_df = filtered_df.dropna(subset=[
            'product_category_name_english',
            'order_item_id'
        ])

        product_category = product_df.groupby(
            'product_category_name_english'
        )['order_item_id'].count().reset_index()

        product_category = product_category.sort_values(
            by='order_item_id',
            ascending=False
        )

        total = product_category['order_item_id'].sum()
        product_category['percentage'] = (product_category['order_item_id'] / total) * 100

        top_10 = product_category.head(10)
       
        fig2, ax2 = plt.subplots()
        sns.barplot(data=top_10, x='order_item_id', y='product_category_name_english', palette=palette, ax=ax2)

        for i, p in enumerate(ax2.patches):
            width = p.get_width()
            percent = top_10['percentage'].iloc[i]

            ax2.text(
                width/2,
                p.get_y() + p.get_height()/2,
                f'{percent:.1f}%',
                ha='center',
                va='center',
                color='black'
            )

        ax2.xaxis.set_major_formatter(formatter)

        max_val = top_10['order_item_id'].max()
        ax2.set_xlim(0, max_val * 1.1)

        if max_val <= 10:
            ax2.set_xticks(range(0, int(max_val) + 1))
        else:
            ax2.xaxis.set_major_formatter(formatter)

        ax2.set_xlabel("Total Orders")
        ax2.set_ylabel("Product Category")
        ax2.grid(False)

        st.pyplot(fig2)

    except:
        st.warning("Failed to display product data")

with tab3:
    st.header("Delivery Performance vs Customer Rating")

    try:
        delivery_df = filtered_df.dropna(subset=['order_delivered_customer_date'])

        delivery_df['delay'] = (
            delivery_df['order_delivered_customer_date'] -
            delivery_df['order_estimated_delivery_date']
        ).dt.days

        delivery_df['delivery_status'] = delivery_df['delay'].apply(
            lambda x: 'Late' if x > 0 else 'On Time'
        )

        delivery_review = delivery_df.groupby('delivery_status')['review_score'].mean()
        delivery_review = delivery_review.reindex(['Late', 'On Time'], fill_value=0).reset_index()

        fig3, ax3 = plt.subplots()
        sns.barplot(data=delivery_review, x='delivery_status', y='review_score', palette=["#FF6B6B", "#79C"], ax=ax3)

        for p in ax3.patches:
            height = p.get_height()
            ax3.text(
                p.get_x() + p.get_width()/2,
                height + 0.05,  
                f'{height:.2f}',
                ha='center',
                va='bottom'
            )
            
        ax3.set_ylim(0, 5)
        ax3.set_xlabel("Delivery Status")
        ax3.set_ylabel("Average Rating")
        ax3.grid(False)

        st.pyplot(fig3)

    except:
        st.warning("Failed to display delivery data")