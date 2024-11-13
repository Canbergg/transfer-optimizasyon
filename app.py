import streamlit as st
import pandas as pd
import io

st.title("SKU Data Aggregation and Analysis Tool")

# Step 1: Upload cardproduct file
cardproduct_file = st.file_uploader("Upload Cardproduct File", type=["xlsx"])
if cardproduct_file:
    cardproduct_df = pd.read_excel(cardproduct_file)
    
    # Check if the cardproduct file has the expected number of columns
    expected_columns = ['Ürün Kodu', 'Ürün Adı', 'ARTICLE_FAMILY', 'ARTICLE_CATEGORY']
    if len(cardproduct_df.columns) == len(expected_columns):
        # Rename columns to match expected names
        cardproduct_df.columns = expected_columns
        cardproduct_df = cardproduct_df.rename(columns={'Ürün Kodu': 'ARTICLE_CODE'})
    else:
        st.error(f"Cardproduct dosyasında beklenmeyen bir sütun sayısı var. Beklenen sütun sayısı {len(expected_columns)}, "
                 f"ama dosyada {len(cardproduct_df.columns)} sütun bulundu. Lütfen dosyayı kontrol edin.")
        st.stop()  # Stop the app if columns are incorrect

# Step 2: Upload multiple data files
uploaded_files = st.file_uploader("Upload Data Files to Merge", type=["xlsx"], accept_multiple_files=True)
if uploaded_files and cardproduct_file:
    combined_data = []
    for uploaded_file in uploaded_files:
        df = pd.read_excel(uploaded_file).iloc[1:]  # Skip the header row
        combined_data.append(df)

    combined_df = pd.concat(combined_data, ignore_index=True)

    # Define the final columns order
    final_columns = [
        "SIPARIS_KAYIT_TARIHI", "ALOKE_TARIHI", "OUTER_GROUP_ID", "OUTER_GROUP_TYPE", 
        "WORK_ORDER_NO", "DESCRIPTION", "ARTICLE_CODE", "ARTICLE_DESCRIPTION", 
        "QTY_HOST", "QTY_GRANTED", "QTY_DEFFERENCE", "CUSTOMER NO", "COMPANY NAME", 
        "ARTICLE_CATEGORY", "ARTICLE_FAMILY"
    ]
    combined_df.columns = final_columns[:len(combined_df.columns)]

    # Perform VLOOKUP-like operation to add ARTICLE_CATEGORY and ARTICLE_FAMILY based on ARTICLE_CODE
    combined_df = combined_df.merge(cardproduct_df[['ARTICLE_CODE', 'ARTICLE_CATEGORY', 'ARTICLE_FAMILY']],
                                    on='ARTICLE_CODE', how='left')

    # Check if ARTICLE_CATEGORY and ARTICLE_FAMILY columns are present after merging
    missing_columns = [col for col in ['ARTICLE_CATEGORY', 'ARTICLE_FAMILY'] if col not in combined_df.columns]
    if missing_columns:
        st.error(f"Birleştirme işlemi sonrasında şu sütunlar bulunamadı: {', '.join(missing_columns)}. "
                 "Lütfen 'cardproduct' dosyasındaki 'ARTICLE_CODE' değerlerinin doğruluğunu kontrol edin.")
        st.stop()

    # Display combined data
    st.write("Combined Data")
    st.dataframe(combined_df)

    # Summary for Article_Category
    category_summary = combined_df.groupby('ARTICLE_CATEGORY').agg({
        'QTY_HOST': 'sum',
        'QTY_GRANTED': 'sum',
        'QTY_DEFFERENCE': 'sum'
    }).reset_index()
    category_summary['GRANT_HOST_RATIO'] = category_summary['QTY_GRANTED'] / category_summary['QTY_HOST']

    st.write("Article Category Summary")
    st.dataframe(category_summary)

    # Summary for Article_Family
    family_summary = combined_df.groupby('ARTICLE_FAMILY').agg({
        'QTY_HOST': 'sum',
        'QTY_GRANTED': 'sum',
        'QTY_DEFFERENCE': 'sum'
    }).reset_index()
    family_summary['GRANT_HOST_RATIO'] = family_summary['QTY_GRANTED'] / family_summary['QTY_HOST']

    st.write("Article Family Summary")
    st.dataframe(family_summary)

    # Create a button to download summaries as Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        category_summary.to_excel(writer, sheet_name='Category Summary', index=False)
        family_summary.to_excel(writer, sheet_name='Family Summary', index=False)
        writer.save()
        processed_data = output.getvalue()

    st.download_button(
        label="Download Summary as Excel",
        data=processed_data,
        file_name="summary_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
