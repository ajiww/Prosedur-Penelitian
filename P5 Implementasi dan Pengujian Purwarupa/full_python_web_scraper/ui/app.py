# ui/app.py
import tkinter as tk
from tkinter import ttk, messagebox
from scraper.fetcher import fetch_page
from scraper.parser import parse_html
from scraper.storage import save_data
from utils.logger import logger

class WebScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Modular Web Scraper")
        self.geometry("600x400")

        # Input URL
        self.url_label = ttk.Label(self, text="Target URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ttk.Entry(self, width=50)
        self.url_entry.pack(pady=5)

        # Button
        self.scrape_button = ttk.Button(self, text="Scrape", command=self.scrape)
        self.scrape_button.pack(pady=10)

        # Output
        self.output_text = tk.Text(self, wrap="word", height=15)
        self.output_text.pack(pady=10, fill="both", expand=True)

    def scrape(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Masukkan URL terlebih dahulu!")
            return

        try:
            logger.info("Fetching page...")
            html = fetch_page(url)

            logger.info("Parsing content...")
            data = parse_html(html)

            logger.info("Saving data...")
            save_data(data)

            self.output_text.delete("1.0", tk.END)
            for item in data:
                self.output_text.insert(tk.END, f"{item['title']} - {item['link']}\n")

            messagebox.showinfo("Success", "Scraping selesai dan data disimpan!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

