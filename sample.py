import streamlit as st
import pandas as pd

# Order and OrderBook classes
class Order():
    def __init__(self, seq_id, side, price, qty, action='N'):
        self.seq_id = seq_id
        self.side = side
        self.price = float(price)
        self.qty = int(qty)
        self.action = action

class OrderBook():
    def __init__(self, initial_orders=None):
        self.buy_orders = []
        self.sell_orders = []
        self.trade_messages = []  # Initialize trade messages
        
        # Add initial orders if provided
        if initial_orders:
            for order in initial_orders:
                self.addOrder(order)

    def addOrder(self, order):
        if order.side == 'B':
            # Check if there's an existing order with the same price
            existing_order = next((o for o in self.buy_orders if o.price == order.price), None)
            if existing_order:
                existing_order.qty += order.qty  # Update quantity of existing order
            else:
                self.buy_orders.append(order)
            matched_prices = sorted(self.sell_orders, key=lambda x: x.price)
            for i in matched_prices:
                if order.price >= i.price:
                    self.process_trade(order, i)
                    if order.qty == 0:
                        break
        elif order.side == "S":
            # Check if there's an existing order with the same price
            existing_order = next((o for o in self.sell_orders if o.price == order.price), None)
            if existing_order:
                existing_order.qty += order.qty  # Update quantity of existing order
            else:
                self.sell_orders.append(order)
            matched_prices = sorted(self.buy_orders, key=lambda x: -x.price)
            for i in matched_prices:
                if order.price <= i.price:
                    self.process_trade(order, i)
                    if order.qty == 0:
                        break

    def process_trade(self, aggressor, passive):
        while aggressor.qty > 0 and passive.qty > 0:
            qty_traded = min(aggressor.qty, passive.qty)
            aggressor.qty -= qty_traded
            passive.qty -= qty_traded
            
            # Append trade message to the list
            message = f"Trade: {'Buy' if aggressor.side == 'B' else 'Sell'} order {qty_traded} at {passive.price}"
            self.trade_messages.append(message)

            if passive.qty == 0:
                if passive in self.sell_orders:
                    self.sell_orders.remove(passive)
                elif passive in self.buy_orders:
                    self.buy_orders.remove(passive)
            if aggressor.qty == 0:
                if aggressor in self.sell_orders:
                    self.sell_orders.remove(aggressor)
                elif aggressor in self.buy_orders:
                    self.buy_orders.remove(aggressor)

    def get_orders(self):
        self.sell_orders = sorted(self.sell_orders, key=lambda x: x.price)
        self.buy_orders = sorted(self.buy_orders, key=lambda x: -x.price)
        return {
            "asks": [(item.price, item.qty) for item in self.sell_orders],
            "bids": [(item.price, item.qty) for item in self.buy_orders],
            "messages": self.trade_messages  # Return trade messages
        }

# Initialize Streamlit session state for order book
if 'order_book' not in st.session_state:
    initial_orders = [
        Order(seq_id=1, side='B', price=100.00, qty=50),
        Order(seq_id=2, side='S', price=101.00, qty=30),
        Order(seq_id=3, side='B', price=99.50, qty=20),
        Order(seq_id=4, side='S', price=102.50, qty=15),
        Order(seq_id=1, side='B', price=98.00, qty=50),
        Order(seq_id=2, side='S', price=104.00, qty=30),
        Order(seq_id=3, side='B', price=98.50, qty=20),
        Order(seq_id=4, side='S', price=103.50, qty=15)
    ]
    st.session_state.order_book = OrderBook(initial_orders)

# Access the order book from session state
order_book = st.session_state.order_book

# Streamlit app layout
st.title("Order Book Visualiser")
st.markdown("""
This is a visualiser for a simple custom-made order book. It matches according to top of the book and size. 
There is no FIFO element as each order is added once at a time by the user (you). Any trades (crosses in the order book) that occur will be printed below.
""")

st.subheader("Trade Logs:")
# Display trade messages
col1_, col2_ = st.columns(2)
with col1_:
    trade_messages = st.empty()  # Placeholder for trade messages


st.write("")
st.write("")
st.subheader("Order-Book Ladder")

st.markdown(
    """
    <style>
    div[role="form"] {
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important; /* Optional: Remove padding */
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Input section for new orders
with st.form(key='order_form'):
    col1, col2 = st.columns(2)

    with col1:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        side = st.text_input("Order Side (B/S):", value='B', max_chars=1)
        price = st.number_input("Price:", value=100.50)
        qty = st.number_input("Quantity:", value=100)
        submit_button = st.form_submit_button("Submit Order")

        # Add new order on submit
        if submit_button and price is not None and qty is not None:
            seq_id = len(order_book.buy_orders) + len(order_book.sell_orders) + 1  # Generate a unique ID
            new_order = Order(seq_id, side.upper(), price, qty)
            order_book.addOrder(new_order)

        # Get updated orders from order book
        orders = order_book.get_orders()

    # with col2:
    # Create DataFrames for bid and ask sides
    #     bid_df = pd.DataFrame(orders['bids'], columns=["Bids", "Quantity"])
    #     ask_df = pd.DataFrame(orders['asks'], columns=["Asks", "Quantity"]).sort_values(by="Asks", ascending=False)

    #     st.dataframe(ask_df.style.applymap(lambda x: 'background-color: #ffcccc; color: black;', subset=['Asks', 'Quantity']))

    #     if not bid_df.empty and not ask_df.empty:
    #         mid_price = (bid_df['Bids'].iloc[0] + ask_df['Asks'].iloc[-1]) / 2
    #         st.subheader(f"Mid Price: {mid_price:.2f}")
    #     else:
    #         st.subheader("Mid Price: N/A")
    #     st.dataframe(bid_df.style.applymap(lambda x: 'color: black; background-color: #ccffcc;', subset=['Bids', 'Quantity']))


    st.markdown(
    """
    <style>
    .dataframe-container {
        margin-bottom: -5px;  /* Adjust the value to control the gap */
    }
    </style>
    """, unsafe_allow_html=True
    )

    with col2:
        bid_df = pd.DataFrame(orders['bids'], columns=["Bids", "Quantity"])
        ask_df = pd.DataFrame(orders['asks'], columns=["Asks", "Quantity"]).sort_values(by="Asks", ascending=False)

        # Display asks table with lighter red background cells
        st.dataframe(ask_df.style.applymap(lambda x: 'background-color: #ffcccc; color: black;', subset=['Asks', 'Quantity']))
        
        # Add a small margin before the bids table
        st.markdown('<div class="dataframe-container"></div>', unsafe_allow_html=True)

        # Display bids table with lighter green background cells
        st.dataframe(bid_df.style.applymap(lambda x: 'background-color: #ccffcc; color: black;', subset=['Bids', 'Quantity']))

    # Get the mid-price (average of the best bid and ask)
    st.markdown(
        """
        <style>
        .dataframe-container {
            margin-bottom: -5px;  /* Adjust the value to control the gap */
        }
        .trade-messages {
            border: 1px solid #ccc;  /* Border color */
            padding: 10px;           /* Padding inside the border */
            border-radius: 5px;      /* Rounded corners */
            margin-top: 20px;        /* Space above the trade messages */
            text-align: left;
        }
        </style>
        """, unsafe_allow_html=True
    )
    # Create a message string from trade messages
    trade_message_str = "<div class='trade-messages'>" + "<br>".join(orders['messages']) + "</div>"
    trade_messages.markdown(trade_message_str, unsafe_allow_html=True)
