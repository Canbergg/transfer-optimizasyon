import pandas as pd
import streamlit as st

st.title("Transfer Optimization Tool")

# Load Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        data = pd.read_excel(uploaded_file)
        st.success("Excel file loaded successfully!")
        st.dataframe(data.head())

        if st.button("Optimize Transfers"):
            # Transfer optimization logic
            grouped_transfers = data.groupby(['Gönderen Depo', 'Alan Depo'])
            optimized_transfer_list = []

            for (sending_depot, receiving_depot), group in grouped_transfers:
                if group['Transfer Miktarı'].sum() >= 3:
                    optimized_transfer_list.append(group)

            optimized_transfer_df = pd.concat(optimized_transfer_list)

            st.success("Optimization complete!")
            st.dataframe(optimized_transfer_df)

            # Allow user to download the optimized transfer list
            @st.cache_data
            def convert_df(df):
                return df.to_excel("optimized_transfer_list.xlsx", index=False)

            convert_df(optimized_transfer_df)
            with open("optimized_transfer_list.xlsx", "rb") as file:
                st.download_button(
                    label="Download Optimized Transfer List",
                    data=file,
                    file_name='Optimized_Transfer_Listesi.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
    except Exception as e:
        st.error(f"Failed to load file: {e}")
