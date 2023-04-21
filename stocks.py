import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

def load_all_symbols():
    nasdaq_url = "https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download"
    nyse_url = "https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download"

    nasdaq_symbols = pd.read_csv(nasdaq_url, usecols=["Symbol"])["Symbol"].tolist()
    nyse_symbols = pd.read_csv(nyse_url, usecols=["Symbol"])["Symbol"].tolist()

    all_symbols = nasdaq_symbols + nyse_symbols
    return all_symbols

def fetch_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data

def preprocess_data(data):
    data['Date'] = data.index
    data.reset_index(drop=True, inplace=True)
    data['SMA'] = data['Close'].rolling(window=5).mean()
    data['Change'] = data['Close'].pct_change()
    data.dropna(inplace=True)

    X = data[['SMA', 'Change']].values
    y = data['Close'].values
    return X, y

def train_model(X_train, y_train):
    model = DecisionTreeRegressor(random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    return mse

def plot_data(symbol, start_date, end_date):
    data = fetch_data(symbol, start_date, end_date)
    X, y = preprocess_data(data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = train_model(X_train, y_train)
    mse = evaluate_model(model, X_test, y_test)
    y_pred = model.predict(X_test)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(y_test, label='Actual')
    ax.plot(y_pred, label='Predicted')
    ax.set(xlabel='Test Data Points', ylabel='Stock Price', title=f'{symbol} Stock Price Prediction (MSE: {mse:.2f})')
    ax.legend()

    return fig

def load_symbols_thread():
    global all_symbols
    all_symbols = load_all_symbols()

def on_search_entry_change(event):
    query = search_entry.get().strip().upper()
    search_results.delete(0, tk.END)

    if query:
        for symbol in all_symbols:
            if query in symbol:
                search_results.insert(tk.END, symbol)

def update_plot():
    try:
        symbol = search_results.get(search_results.curselection())
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        fig = plot_data(symbol, start_date, end_date)
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0, columnspan=4, padx=10, pady=10)
    except:
        pass

window = tk.Tk()
window.title("Stock Market Data and Analysis")

all_symbols = []

# Create input fields and labels
search_label = ttk.Label(window, text="Search Symbol:")
search_label.grid(row=0, column=0, padx=10, pady=10)

search_entry = ttk.Entry(window)
search_entry.grid(row=0, column=1, padx=10, pady=10)
search_entry.bind("<KeyRelease>", on_search_entry_change)

search_results = tk.Listbox(window)
search_results.grid(row=1, column=1, padx=10, pady=10)


start_date_label = ttk.Label(window, text="Start Date (YYYY-MM-DD):")
start_date_label.grid(row=0, column=2, padx=10, pady=10)
start_date_entry = ttk.Entry(window)
start_date_entry.grid(row=0, column=3, padx=10, pady=10)

end_date_label = ttk.Label(window, text="End Date (YYYY-MM-DD):")
end_date_label.grid(row=1, column=0, padx=10, pady=10)
end_date_entry = ttk.Entry(window)
end_date_entry.grid(row=1, column=1, padx=10, pady=10)

# Create a button to update the plot
plot_button = ttk.Button(window, text="Plot Data", command=update_plot)
plot_button.grid(row=1, column=2, padx=10, pady=10)

# Start a thread to load all symbols
symbols_thread = threading.Thread(target=load_symbols_thread)
symbols_thread.start()

# Start the GUI main loop
window.mainloop()
