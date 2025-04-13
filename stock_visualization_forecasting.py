import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import warnings
warnings.filterwarnings('ignore')

class StockVisualizerApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Stock Visualizer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
      
        self.default_tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA']
        self.custom_ticker = tk.StringVar()
        
       
        self.data = {}  
        self.active_ticker = None 
       
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        start = datetime.now() - timedelta(days=365)
        self.start_date = start.strftime('%Y-%m-%d')
        
        
        self._create_ui()
        
       
        self._fetch_default_data()
    
    def _create_ui(self):
       
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.pack(fill=tk.X, pady=5)
        
        
        ttk.Label(control_frame, text="Select Ticker:").pack(side=tk.LEFT, padx=5)
        self.ticker_combo = ttk.Combobox(control_frame, values=self.default_tickers, width=10)
        self.ticker_combo.pack(side=tk.LEFT, padx=5)
        self.ticker_combo.bind("<<ComboboxSelected>>", self._on_ticker_selected)
        
        
        ttk.Label(control_frame, text="or Enter Ticker:").pack(side=tk.LEFT, padx=5)
        ticker_entry = ttk.Entry(control_frame, textvariable=self.custom_ticker, width=10)
        ticker_entry.pack(side=tk.LEFT, padx=5)
        
        
        add_button = ttk.Button(control_frame, text="Add & Load", command=self._add_custom_ticker)
        add_button.pack(side=tk.LEFT, padx=5)
        
        
        ttk.Label(control_frame, text="Chart Type:").pack(side=tk.LEFT, padx=5)
        self.chart_type = tk.StringVar(value="Price")
        chart_options = ["Price", "Price with MA", "Volume", "Returns", "Technical", "Forecast"]
        chart_combo = ttk.Combobox(control_frame, values=chart_options, textvariable=self.chart_type, width=12)
        chart_combo.pack(side=tk.LEFT, padx=5)
        chart_combo.bind("<<ComboboxSelected>>", self._update_chart)
        
        
        date_frame = ttk.Frame(control_frame)
        date_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(date_frame, text="Period:").pack(side=tk.LEFT, padx=5)
        self.period = tk.StringVar(value="1y")
        period_options = ["1m", "3m", "6m", "1y", "2y", "5y", "max"]
        period_combo = ttk.Combobox(date_frame, values=period_options, textvariable=self.period, width=5)
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", self._update_period)
        
        self.chart_frame = ttk.Frame(main_frame, padding="5")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
     
        self.fig = plt.Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _fetch_default_data(self):
       
        self.status_var.set("Fetching data for default tickers...")
        
        
        threading.Thread(target=self._background_fetch, args=(self.default_tickers,), daemon=True).start()
    
    def _background_fetch(self, tickers):
      
        successful_tickers = []
        
        for ticker in tickers:
            try:
                self.status_var.set(f"Downloading data for {ticker}...")
                stock_data = yf.download(ticker, start=self.start_date, end=self.end_date, progress=False)
                
                if stock_data.empty:
                    print(f"No data found for {ticker}")
                else:
                    self.data[ticker] = stock_data
                    successful_tickers.append(ticker)
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
        
        
        self.root.after(0, lambda: self._update_after_fetch(successful_tickers))
    
    def _update_after_fetch(self, successful_tickers):
       
        if successful_tickers:
            
            all_tickers = sorted(list(self.data.keys()))
            self.ticker_combo['values'] = all_tickers
            self.ticker_combo.set(successful_tickers[0])
            
            self.active_ticker = successful_tickers[0]
            self._update_chart()
            
            self.status_var.set(f"Loaded {len(successful_tickers)} tickers successfully")
        else:
            self.status_var.set("Failed to load any ticker data. Check your connection.")
    
    def _add_custom_ticker(self):
        
        ticker = self.custom_ticker.get().strip().upper()
        
        if not ticker:
            messagebox.showwarning("Invalid Input", "Please enter a ticker symbol")
            return
            
        if ticker in self.data:
            
            self.ticker_combo.set(ticker)
            self.active_ticker = ticker
            self._update_chart()
            return
            
       
        self.status_var.set(f"Fetching data for {ticker}...")
        threading.Thread(target=self._background_fetch, args=([ticker],), daemon=True).start()
    
    def _on_ticker_selected(self, event=None):

        selected = self.ticker_combo.get()
        if selected and selected in self.data:
            self.active_ticker = selected
            self._update_chart()
            
    def _update_period(self, event=None):
       
        period = self.period.get()
        
        end_date = datetime.now()
        
        
        if period == "1m":
            start_date = end_date - timedelta(days=30)
        elif period == "3m":
            start_date = end_date - timedelta(days=90)
        elif period == "6m":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        elif period == "max":
            start_date = datetime(1970, 1, 1)  
        else:
            start_date = end_date - timedelta(days=365)  
        
        self.start_date = start_date.strftime('%Y-%m-%d')
        self.end_date = end_date.strftime('%Y-%m-%d')
        

        if self.active_ticker:
            self.status_var.set(f"Updating data for period: {period}...")
            threading.Thread(target=self._background_fetch, args=([self.active_ticker],), daemon=True).start()
    
    def _update_chart(self, event=None):
       
        if not self.active_ticker or self.active_ticker not in self.data:
            return
        
        chart_type = self.chart_type.get()
        ticker_data = self.data[self.active_ticker]
        
        
        self.fig.clear()
        
        try:
            if chart_type == "Price":
                self._plot_price(ticker_data)
            elif chart_type == "Price with MA":
                self._plot_price_with_ma(ticker_data)
            elif chart_type == "Volume":
                self._plot_volume(ticker_data)
            elif chart_type == "Returns":
                self._plot_returns(ticker_data)
            elif chart_type == "Technical":
                self._plot_technical(ticker_data)
            elif chart_type == "Forecast":
                self._plot_forecast(ticker_data)
            else:
                self._plot_price(ticker_data)  
                
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Chart Error", f"Error creating chart: {e}")
    
    def _plot_price(self, data):
        
        ax = self.fig.add_subplot(111)
        ax.plot(data['Close'], label=f'{self.active_ticker} Close Price', color='blue')
        
        ax.set_title(f'{self.active_ticker} Stock Price')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (USD)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_price_with_ma(self, data):
        
        ax = self.fig.add_subplot(111)
        ax.plot(data['Close'], label=f'{self.active_ticker} Close Price', color='blue')
        
        ma_periods = [20, 50, 200]
        ma_colors = ['green', 'red', 'purple']
        
        for period, color in zip(ma_periods, ma_colors):
            ma = data['Close'].rolling(window=period).mean()
            ax.plot(ma, label=f'{period}-day MA', color=color, linestyle='--')
        
        ax.set_title(f'{self.active_ticker} Stock Price with Moving Averages')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (USD)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_volume(self, data):
        
        ax = self.fig.add_subplot(111)
        ax.bar(data.index, data['Volume'], alpha=0.7, color='blue')
        
        ax.set_title(f'{self.active_ticker} Trading Volume')
        ax.set_xlabel('Date')
        ax.set_ylabel('Volume')
        ax.grid(True, alpha=0.3)
    
    def _plot_returns(self, data):
       
        data['Daily_Return'] = data['Close'].pct_change()
        data['Cumulative_Return'] = (1 + data['Daily_Return']).cumprod() - 1
        
        
        ax1 = self.fig.add_subplot(211)
        ax2 = self.fig.add_subplot(212, sharex=ax1)
        
       
        ax1.plot(data['Daily_Return'].dropna(), color='blue', alpha=0.7)
        ax1.set_title(f'{self.active_ticker} Daily Returns')
        ax1.set_ylabel('Return')
        ax1.grid(True, alpha=0.3)
        
        
        ax2.plot(data['Cumulative_Return'].dropna(), color='green', alpha=0.9)
        ax2.set_title(f'{self.active_ticker} Cumulative Returns')
        ax2.set_ylabel('Cumulative Return')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
    
    def _plot_technical(self, data):
        
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        
        sma20 = data['Close'].rolling(window=20).mean()
        upper_band = sma20 + (data['Close'].rolling(window=20).std() * 2)
        lower_band = sma20 - (data['Close'].rolling(window=20).std() * 2)
        
            
        ema12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal_line = macd.ewm(span=9, adjust=False).mean()
        
       
        ax1 = self.fig.add_subplot(411)
        ax2 = self.fig.add_subplot(412, sharex=ax1)
        ax3 = self.fig.add_subplot(413, sharex=ax1)
        ax4 = self.fig.add_subplot(414, sharex=ax1)
        
       
        ax1.plot(data['Close'], label='Close Price')
        ax1.plot(sma20, label='20-day SMA', linestyle='--')
        ax1.plot(upper_band, label='Upper Band', linestyle=':')
        ax1.plot(lower_band, label='Lower Band', linestyle=':')
        ax1.set_title(f'{self.active_ticker} Price and Bollinger Bands')
        ax1.set_ylabel('Price (USD)')
        ax1.legend(loc='upper left', fontsize='small')
        ax1.grid(True, alpha=0.3)
        
        
        ax2.bar(data.index, data['Volume'], color='blue', alpha=0.7)
        ax2.set_title(f'{self.active_ticker} Volume')
        ax2.set_ylabel('Volume')
        ax2.grid(True, alpha=0.3)
        
      
        ax3.plot(rsi, color='purple')
        ax3.axhline(y=70, color='r', linestyle='--', alpha=0.5)
        ax3.axhline(y=30, color='g', linestyle='--', alpha=0.5)
        ax3.set_title(f'{self.active_ticker} RSI')
        ax3.set_ylabel('RSI')
        ax3.grid(True, alpha=0.3)
        
       
        ax4.plot(macd, label='MACD', color='blue')
        ax4.plot(signal_line, label='Signal Line', color='red', linestyle='--')
        ax4.bar(data.index, macd - signal_line, color='grey', alpha=0.5)
        ax4.set_title(f'{self.active_ticker} MACD')
        ax4.set_ylabel('MACD')
        ax4.set_xlabel('Date')
        ax4.legend(loc='upper left', fontsize='small')
        ax4.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
    
    def _plot_forecast(self, data):
       
        try:
            self.status_var.set("Calculating forecast...")
            
            train_data = data['Close'].values
            days = 30  # Number of days to forecast
            
            model = ARIMA(train_data, order=(5,1,0))
            model_fit = model.fit()
            
            forecast = model_fit.forecast(steps=days)
            
            last_date = data.index[-1]
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)
            
            forecast_data = pd.DataFrame({
                'Date': forecast_dates,
                'Forecast': forecast
            })
            forecast_data.set_index('Date', inplace=True)
            
            
            ax = self.fig.add_subplot(111)
            ax.plot(data['Close'], label=f'{self.active_ticker} Historical Prices')
            ax.plot(forecast_data, color='red', linestyle='--', label=f'{self.active_ticker} Forecast')
            ax.set_title(f'{self.active_ticker} Price Forecast ({days} days)')
            ax.set_xlabel('Date')
            ax.set_ylabel('Price (USD)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            self.status_var.set("Forecast complete")
            
        except Exception as e:
            self.status_var.set(f"Error in forecasting: {e}")
            
          
            ax = self.fig.add_subplot(111)
            ax.plot(data['Close'], label=f'{self.active_ticker} Close Price')
            ax.set_title(f'{self.active_ticker} Stock Price (Forecast Failed)')
            ax.set_xlabel('Date')
            ax.set_ylabel('Price (USD)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            messagebox.showerror("Forecast Error", f"Could not generate forecast: {e}")


if __name__ == "__main__":
    
    root = tk.Tk()
    app = StockVisualizerApp(root)
    root.mainloop()