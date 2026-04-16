import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style='whitegrid')
palette = sns.light_palette("#79C", n_colors=10, reverse=True)

rfm_df = pd.read_csv('dashboard/rfm.csv')
product_df = pd.read_csv('dashboard/top_products.csv')
delivery_df = pd.read_csv('dashboard/delay_rating.csv')


st.title("E-Commerce Data Analysis Dashboard")
tab1, tab2, tab3 = st.tabs(["Customer Segmentation (RFM)", "Top 10 Product Categories", "Delivery Performance vs Customer Rating"])
 
with tab1:
    st.header("Customer Segmentation (RFM)")
    segment_counts = rfm_df['segment'].value_counts().reset_index()
    segment_counts.columns = ['segment', 'count']

    fig1, ax1 = plt.subplots()
    sns.barplot(
        data=segment_counts,
        x='count',
        y='segment',
        palette=palette,
        ax=ax1
    )

    ax1.set_xlabel("Number of Customers")
    ax1.set_ylabel("Customer Segment")
    ax1.set_xlim(0, 55000)
    ax1.set_xticks(range(0, 55001, 5000))
    plt.xticks(rotation=45)
    st.pyplot(fig1)
 
with tab2:
    st.header("Top 10 Product Categories")
    fig2, ax2 = plt.subplots()
    sns.barplot(
        data=product_df,
        x='order_item_id',
        y='product_category_name_english',
        palette=palette,
        ax=ax2
    )

    ax2.set_xlabel("Total Orders")
    ax2.set_ylabel("Product Category")
    ax2.set_xlim(0, 12000)
    ax2.set_xticks(range(0, 12001, 2000))
    st.pyplot(fig2)
    
with tab3:
    st.header("Delivery Performance vs Customer Rating")
    fig3, ax3 = plt.subplots()
    sns.barplot(
        data=delivery_df,
        x='delivery_status',
        y='review_score',
        palette=["#FF6B6B", "#79C"],
        ax=ax3
    )

    ax3.set_xlabel("Delivery Status")
    ax3.set_ylabel("Average Rating")
    ax3.set_ylim(0, 5)
    st.pyplot(fig3)