# OrderBookVisualiser

https://orderbookvisualiserrk.streamlit.app/

This repository contains a Streamlit dashboard that visualizes a simple order book for trading. The dashboard allows users to place buy and sell orders, automatically matches them according to market rules, and displays the results in real-time.

## Usage
Input the order side (B for Buy, S for Sell), price, and quantity in the provided fields.
Click the "Submit Order" button to place the order.
View the order book and trade logs update in real-time as orders are matched and trades are executed.

## Features

- **Order Placement**: Users can submit buy (B) or sell (S) orders with a specified price and quantity.
- **Order Matching**: The dashboard matches orders based on market conditions, executing trades when appropriate.
- **Trade Logs**: A real-time log of trades is displayed, showing the details of each executed trade.
- **Order Book Display**: The order book is displayed in a ladder format, showing current buy and sell orders with their respective quantities.
- **Statistics**: Displays key order book statistics, including:
- **Mid Price**: The average of the best bid and ask prices.
- **Weighted Mid Price**: A price calculated based on the volume of the bids and asks.

## Technologies Used

- **Python**: Programming language used for the backend logic.
- **Streamlit**: Framework for creating the web app interface.
- **Pandas**: Library for data manipulation and analysis.
- 
