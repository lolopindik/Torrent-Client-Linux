import libtorrent as lt
import tkinter as tk
from tkinter import filedialog, ttk
import threading
import time
import datetime

class TorrentDownloadTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.ses = lt.session()
        self.is_running = False

        self.link_entry = tk.Entry(self, state=tk.DISABLED, width=40)
        self.link_entry.pack(pady=10)

        self.browse_button = tk.Button(self, text="Выбрать .torrent", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.save_path_var = tk.StringVar()
        self.save_path_var.set("")

        title_label = tk.Label(self, text="[+]Для загрузки .torrent выберите директорию для сохранения файлов")
        title_label.pack(pady=10)

        title_label = tk.Label(self, text="[+]Для раздачи .torrent выберите директорию с файлами, хранящимися в .torrent")
        title_label.pack(pady=10)

        self.save_path_entry = tk.Entry(self, textvariable=self.save_path_var, state=tk.DISABLED, width=40)
        self.save_path_entry.pack(pady=5)

        self.choose_path_button = tk.Button(self, text="Выбрать директорию", command=self.choose_save_path)
        self.choose_path_button.pack(pady=10)

        self.start_button = tk.Button(self, text="Начать загрузку / раздачу", command=self.start_download)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Прекратить действие", command=self.stop_download, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.progress_text = tk.Text(self, height=11, width=100)
        self.progress_text.pack(pady=10)
        self.progress_text.config(state=tk.DISABLED)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Выберите торрент файл", filetypes=[("Torrent files", "*.torrent")])

        if file_path:
            self.link_entry.config(state=tk.NORMAL)
            self.link_entry.delete(0, tk.END)
            self.link_entry.insert(0, file_path)
            self.link_entry.config(state=tk.DISABLED)
        else:
            self.link_entry.config(state=tk.NORMAL)
            self.link_entry.delete(0, tk.END)
            self.link_entry.insert(0, "")
            self.link_entry.config(state=tk.DISABLED)

    def choose_save_path(self):
        chosen_path = filedialog.askdirectory(title="Выберите папку для сохранения")

        if chosen_path:
            self.save_path_var.set(chosen_path)
        else:
            self.save_path_var.set("")

    def start_download(self):
        link = self.link_entry.get()

        if not link:
            return

        save_path = self.save_path_var.get()

        if not save_path:
            return

        if hasattr(self, 'ses') and self.ses:
            self.ses = True

        self.ses = lt.session()
        #изменен диапозон для поддержки большего числа треккеров
        self.ses.listen_on(6881, 6969)

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_path_entry.config(state=tk.DISABLED)

        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete("1.0", tk.END)

        #рассмотреть адекватность данного подхода
        threading.Thread(target=self.download_torrent, args=(link, save_path), daemon=True).start()

    def stop_download(self):
        if self.is_running:
            self.is_running = False

            if hasattr(self, 'ses') and self.ses:
                self.ses = None

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_path_entry.config(state=tk.NORMAL)

    def download_torrent(self, link, save_path):
        params = {
            'save_path': save_path,
            #нужно сделать услоную конструкцию для 1-го мода, для сидинга
            'storage_mode': lt.storage_mode_t(2)
        }

        try:
            info = lt.torrent_info(link)
        except Exception as e:
            self.update_progress(f"Информация об ошибке загрузки: {e}")
            return

        handle = self.ses.add_torrent({'ti': info, 'save_path': save_path, 'storage_mode': params['storage_mode']})
        self.ses.start_dht()

        begin = time.time()
        self.update_progress(datetime.datetime.now())
        self.update_progress('Загрузка метаданных...')

        while not handle.has_metadata():
            time.sleep(1)

        self.update_progress('Получение метаданных, Запуск действия')
        self.update_progress(f'Запуск {handle.name()}')

        while self.is_running:
            s = handle.status()
            state_str = ['Поставлен в очередь', 'Проверяется', 'Скачивание метаданных',
                        'Скачивается', 'Окончено', 'Раздается', 'Распределение']

            progress_text = f'{s.progress * 100:.2f} % завершено (скачивание: {s.download_rate / 1000:.1f} кБ/с ' \
                            f'отправка: {s.upload_rate / 1000:.1f} кБ/с пиры: {s.num_peers}) {state_str[s.state]} '

            self.update_progress(progress_text)
            time.sleep(1)

        end = time.time()
        self.update_progress(f'{handle.name()} Закончено!')
        self.update_progress(datetime.datetime.now())

        self.start_button.config(state=tk.NORMAL)
        self.save_path_entry.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_progress(self, text):
        self.progress_text.insert(tk.END, str(text) + "\n")
        self.progress_text.yview(tk.END)
        self.after(1, self.progress_text.yview, tk.END)