import libtorrent as lt
import tkinter as tk
from tkinter import ttk
import load
import generate as gen

class TorrentGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("800x600")
        self.resizable(False, False)
        self.title("Торрент 2-исп11-30ВБ")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # фолдеры
        self.download_tab = load.TorrentDownloadTab(self.notebook)
        self.generate_tab = gen.GenerateTab(self.notebook)

        self.notebook.add(self.download_tab, text='Загрузка или Раздача')
        self.notebook.add(self.generate_tab, text='Создание .torrent')
        
#классы из импортрованных модулей
load.TorrentDownloadTab
gen.GenerateTab

# Запуск основного окна
if __name__ == "__main__":
    app = TorrentGUI()
    app.mainloop()