from dash import Dash, html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

class Order:
    def __init__(self, seq_id, side, price, qty, action='N'):
        self.seq_id = seq_id
        self.side = side
        self.price = float(price)
        self.qty = int(qty)
        self.action = action

class OrderBook:
    def __init__(self, initial_orders=None):
        self.buy_orders = []
        self.sell_orders = []
        self.trade_messages = []
        if initial_orders:
            for order in initial_orders:
                self.addOrder(order)

    def addOrder(self, order):
        if order.side == 'B':
            existing_order = next((o for o in self.buy_orders if o.price == order.price), None)
            if existing_order:
                existing_order.qty += order.qty
            else:
                self.buy_orders.append(order)
            matched_prices = sorted(self.sell_orders, key=lambda x: x.price)
            for i in matched_prices:
                if order.price >= i.price:
                    self.process_trade(order, i)
                    if order.qty == 0:
                        break
        elif order.side == "S":
            existing_order = next((o for o in self.sell_orders if o.price == order.price), None)
            if existing_order:
                existing_order.qty += order.qty
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
            "messages": self.trade_messages
        }

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
order_book = OrderBook(initial_orders)

app = Dash(external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = html.Div(children=[
    html.H2("Order Book Visualiser", style={"text-align": "center", "margin-top": "20px"}),
    html.Div(""" 
    This is a visualiser for a simple custom-made order book. It matches according to top of the book and size. 
    There is no FIFO element as each order is added once at a time by the user (you). Any trades (crosses in the order book) that occur will be printed below.
    """, style={"margin-top": "10px", "text-align": "center"}),
    html.Div(id="trade-messages", style={"margin-top": "5px", "text-align": "center", "font-weight": "bold"}),

    html.Div(children=[
        html.Div(children=[
            dash_table.DataTable(
                id="ask_table",
                columns=[{"name": "Price", "id": "price"}, {"name": "Quantity", "id": "quantity"}],
                style_header={"display": "none"},
                style_cell={"minWidth": "140px", "maxWidth": "140px", "width": "140px", "text-align": "right"},
                style_data_conditional=[
                    {'if': {'column_id': 'price'}, 'backgroundColor': 'red', 'color': 'white'},
                    {'if': {'column_id': 'quantity'}, 'backgroundColor': 'red', 'color': 'white'}
                ]
            ),
            html.H2(id="mid-price", style={"padding-top": "30px", "text-align": "center"}),
            dash_table.DataTable(
                id="bid_table",
                columns=[{"name": "Price", "id": "price"}, {"name": "Quantity", "id": "quantity"}],
                style_header={"display": "none"},
                style_cell={"minWidth": "140px", "maxWidth": "140px", "width": "140px", "text-align": "right"},
                style_data_conditional=[
                    {'if': {'column_id': 'price'}, 'backgroundColor': 'green', 'color': 'white'},
                    {'if': {'column_id': 'quantity'}, 'backgroundColor': 'green', 'color': 'white'}
                ]
            ),
        ], style={"width": "300px"}),

        html.Div(children=[
            dbc.Row([
                dbc.Col(html.Label("Order Side (B/S):"), width=4),
                dbc.Col(dcc.Input(id='side-input', type='text', value='B', maxLength=1), width=8),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(html.Label("Price:"), width=4),
                dbc.Col(dcc.Input(id='price-input', type='number', value=100.50), width=8),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(html.Label("Quantity:"), width=4),
                dbc.Col(dcc.Input(id='qty-input', type='number', value=100), width=8),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(dbc.Button("Submit Order", id='submit-button', n_clicks=0, style={"width": "100%"}), width=12),
            ]),
        ], style={"padding-left": "100px"}),
    ], style={"display": "flex", "justify-content": "center", "align-items": "center", "height": "100vh"}),
    
    dcc.Interval(id="timer", interval=3000),
])

@app.callback(
    [Output("bid_table", "data"),
     Output("ask_table", "data"),
     Output("mid-price", "children"),
     Output("trade-messages", "children")],
    [Input('submit-button', 'n_clicks')],
    [State('side-input', 'value'),
     State('price-input', 'value'),
     State('qty-input', 'value')]
)
def update_orderbook(n_clicks, side, price, qty):
    if n_clicks > 0 and price is not None and qty is not None:
        seq_id = n_clicks + len(order_book.buy_orders) + len(order_book.sell_orders)
        new_order = Order(seq_id, side.upper(), price, qty)
        order_book.addOrder(new_order)

    orders = order_book.get_orders()
    bid_df = pd.DataFrame(orders['bids'], columns=["price", "quantity"])
    ask_df = pd.DataFrame(orders['asks'], columns=["price", "quantity"])
    ask_df = ask_df.sort_values(by="price", ascending=False)

    if len(bid_df) > 0 and len(ask_df) > 0:
        mid_price = (bid_df['price'].iloc[0] + ask_df['price'].iloc[0]) / 2
        mid_price_display = f"{mid_price:.2f}"
    else:
        mid_price_display = "N/A"

    trade_messages = "<br>".join(orders['messages'])
    return bid_df.to_dict("records"), ask_df.to_dict("records"), mid_price_display, trade_messages

