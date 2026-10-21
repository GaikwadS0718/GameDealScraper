import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Game Deal Scraper",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Game Deal Scraper")
st.write("Find video games at discounted prices.")

search = st.text_input(
    "Search for a game",
    placeholder="Enter a game name..."
)

if st.button("Find Deals") or search:
    with st.spinner("Fetching game deals..."):
        try:
            url = "https://www.cheapshark.com/api/1.0/deals"

            params = {
                "title": search.strip(),
            }

            response = requests.get(
                url,
                params=params,
                headers={
                    "User-Agent":"GameDealScraper/1.0(student project)"
                },
                timeout=20
            )

            if response.status_code != 200:
                st.error(f"API Error: {response.status_code}")
                st.code(response.text)
                st.stop()

            deals = response.json()
            st.write("API Response:", deals)

        except Exception as e:
            st.error(f"Could not fetch deals: {e}")
            st.stop()

            if deals:
                df = pd.DataFrame(deals)

                df["salePrice"] = pd.to_numeric(
                    df["salePrice"], errors="coerce"
                )
                df["normalPrice"] = pd.to_numeric(
                    df["normalPrice"], errors="coerce"
                )
                df["savings"] = pd.to_numeric(
                    df["savings"], errors="coerce"
                )

                df = df.dropna(subset=["salePrice"])
                df = df.sort_values("salePrice")

                st.success(f"Found {len(df)} game deals!")

                df["deal_url"] = (
                    "https://www.cheapshark.com/redirect?dealID="
                    + df["dealID"].astype(str)
                )

                display_df = df[[
                    "title",
                    "storeID",
                    "salePrice",
                    "normalPrice",
                    "savings",
                    "deal_url"
                ]].rename(columns={
                    "title": "Game",
                    "storeID": "Store ID",
                    "salePrice": "Sale Price ($)",
                    "normalPrice": "Original Price ($)",
                    "savings": "Discount (%)",
                    "deal_url": "Deal Link"
                })

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Deal Link": st.column_config.LinkColumn(
                            "Buy / View Deal",
                            display_text="Open Deal"
                        ),
                        "Discount (%)": st.column_config.NumberColumn(
                            "Discount (%)",
                            format="%.1f%%"
                        ),
                        "Sale Price ($)": st.column_config.NumberColumn(
                            "Sale Price ($)",
                            format="$%.2f"
                        ),
                        "Original Price ($)": st.column_config.NumberColumn(
                            "Original Price ($)",
                            format="$%.2f"
                        )
                    }
                )
                st.caption(
                    "Prices are displayed in USD. "
                   "Check the store for the final price."
                )

            else:
                st.info(
                    "No deals found. Try another game name."
                )

        except requests.RequestException as error:
            st.error(f"Could not fetch deals: {error}")

        except (ValueError, KeyError) as error:
            st.error(f"Could not process the deal data: {error}")