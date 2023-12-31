import libtorrent as lt
import tkinter as tk
from tkinter import filedialog, ttk
import os

class GenerateTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        title_label = tk.Label(self, text="")
        title_label.pack(pady=30)

        self.link_entry = tk.Entry(self, state=tk.DISABLED, width=40)
        self.link_entry.pack(pady=20)

        self.browse_button = tk.Button(self, text="Выбрать директорию для генерации .torrent", command=self.browse_directory)
        self.browse_button.pack(pady=10)

        self.save_path_var = tk.StringVar()
        self.save_path_var.set("")

        self.save_path_entry = tk.Entry(self, textvariable=self.save_path_var, state=tk.DISABLED, width=40)
        self.save_path_entry.pack(pady=10)

        self.choose_path_button = tk.Button(self, text="Выберите директорию для сохранения .torrent", command=self.choose_save_path)
        self.choose_path_button.pack(pady=10)

        self.start_button = tk.Button(self, text="Сгенерировать .torrent", command=self.start_generate)
        self.start_button.pack(pady=20)

        self.progress_text = tk.Text(self, height=2, width=100)
        self.progress_text.pack(pady=10)
        self.progress_text.config(state=tk.DISABLED)

    def start_generate(self):
        file_path = self.link_entry.get()
        save_path = self.save_path_var.get()

        print(f'Directory Path: {file_path}')
        print(f'Save Path: {save_path}')

        if not file_path:
            self.update_progress(f'Ошибка генерации торрента: Путь к директории не указан')
            return

        if not os.path.exists(file_path):
            self.update_progress(f'Ошибка генерации торрента: Директория не существует - {file_path}')
            return

        if not save_path:
            chosen_path = filedialog.askdirectory(title="Выберите папку для сохранения")
            if not chosen_path:
                return
            self.save_path_var.set(chosen_path)

        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path)
            except Exception as e:
                self.update_progress(f'Ошибка генерации торрента: Невозможно создать директорию - {save_path}')
                return

        try:
            fs = lt.add_files(file_path)
            create_torrent = lt.create_torrent(fs)
            create_torrent.set_priv(False)

            trackers = ["udp://tracker.openbittorrent.com:6969/announce",
                        "udp://tracker.openbittorrent.com:80/announce",
                        "udp://tracker.opentrackr.org:1337/announce",
                        "udp://opentracker.i2p.rocks:6969/announce"]

            for tracker in trackers:
                create_torrent.add_tracker(tracker)

            lt.set_piece_hashes(create_torrent, save_path)

            base_name = os.path.basename(file_path)

            torrent_file_path = os.path.join(save_path, f'{base_name}.torrent')
            with open(torrent_file_path, 'wb') as torrent_file:
                torrent_file.write(lt.bencode(create_torrent.generate()))

            self.update_progress(f'Торрент файл создан успешно: {torrent_file_path}')
        except Exception as e:
            self.update_progress(f'Ошибка генерации торрента: {e}')

    def browse_directory(self):
        directory_path = filedialog.askdirectory(title="Выберите директорию для генерации .torrent")

        if directory_path:
            self.link_entry.config(state=tk.NORMAL)
            self.link_entry.delete(0, tk.END)
            self.link_entry.insert(0, directory_path)
            self.link_entry.config(state=tk.DISABLED)
        else:
            self.link_entry.config(state=tk.NORMAL)
            self.link_entry.delete(0, tk.END)
            self.link_entry.insert(0, "")
            self.link_entry.config(state=tk.DISABLED)

    def choose_save_path(self):
        chosen_path = filedialog.askdirectory(title="Выберите папку для сохранения .torrent")

        if chosen_path:
            self.save_path_var.set(chosen_path)
        else:
            self.save_path_var.set("")

    def update_progress(self, text):
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.insert(tk.END, str(text) + "\n")
        self.progress_text.config(state=tk.DISABLED)
        self.progress_text.yview(tk.END)
        self.after(1, self.progress_text.yview, tk.END)
