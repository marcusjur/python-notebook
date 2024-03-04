import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
import os

import cryptography.fernet
from cryptography.fernet import Fernet
import uuid
from PIL import ImageTk
from handlers import *

key_file = 'secret.key'
if not os.path.exists(key_file):
    key = Fernet.generate_key()
    with open(key_file, 'wb') as file_key:
        file_key.write(key)
else:
    with open(key_file, 'rb') as file_key:
        key = file_key.read()

cipher = Fernet(key)


class NotesApp:
    def __init__(self, root):
        self.root = root
        root.title("Notes")

        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TButton', font=('Calibri Bold', 12), borderwidth='4')
        style.configure('TLabel', font=('Calibri Italic', 12), background='light grey', foreground='black')
        style.configure('TEntry', font=('Calibri Light', 12), borderwidth='2')
        style.map('TButton', background=[('active', 'blue')])

        self.notes = {}
        self.current_note_id = None

        image = Image.open("logo.jpg")
        image = image.resize((100, 100))
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(root, image=photo)
        label.image = photo
        label.grid(row=0, column=0)

        ttk.Label(root, text="Заголовок:").grid(row=0, column=1)
        self.entry_title = ttk.Entry(root)
        self.entry_title.grid(row=0, column=2)

        ttk.Label(root, text="<-- Ключ | Текст заметки:").grid(row=1, column=1)
        self.entry_body = scrolledtext.ScrolledText(root, height=5, width=40)
        self.entry_body.grid(row=1, column=2)

        ttk.Button(root, text="Сохранить изменения", command=self.save_note).grid(row=2, column=2)
        ttk.Button(root, text="Создать новую заметку", command=self.create_new_note).grid(row=3, column=2)
        ttk.Button(root, text="Удалить заметку", command=self.delete_note).grid(row=4, column=2)

        self.listbox_notes = tk.Listbox(root, height=10)
        self.listbox_notes.grid(row=2, column=0, rowspan=4, sticky='nsew')
        self.listbox_notes.bind('<<ListboxSelect>>', self.load_selected_note)

        self.scrollbar_notes = ttk.Scrollbar(root, orient='vertical', command=self.listbox_notes.yview)
        self.scrollbar_notes.grid(row=2, column=1, rowspan=4, sticky='nsew')
        self.listbox_notes['yscrollcommand'] = self.scrollbar_notes.set

        self.img_label = ttk.Label(root)
        self.img_label.grid(row=0, column=0, rowspan=4)

        self.image_files = [f for f in os.listdir('.') if f.lower().endswith('.png')]
        self.image_selector = ttk.Combobox(root, values=self.image_files)
        self.image_selector.grid(row=1, column=0)
        self.image_selector.bind("<<ComboboxSelected>>", self.change_image)

        self.load_notes()

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=0)
        root.grid_columnconfigure(2, weight=1)

        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=0)
        root.grid_rowconfigure(4, weight=1)
        self.load_notes()

    def load_notes(self):
        if os.path.exists("notes.json"):
            with open("notes.json", "r") as file:
                self.notes = json.load(file)
                self.update_notes_list()

    def save_notes(self):
        with open("notes.json", "w") as file:
            json.dump(self.notes, file, indent=4)

    def update_notes_list(self):
        self.listbox_notes.delete(0, tk.END)
        for note_id, note_info in self.notes.items():
            self.listbox_notes.insert(tk.END, f"{note_id}: {note_info['title']}")

    def load_selected_note(self):
        selection = self.listbox_notes.curselection()
        if selection:
            index = selection[0]
            note_id = list(self.notes)[index]
            self.current_note_id = note_id
            note_info = self.notes[note_id]
            note_file_path = note_info['file']
            with open(note_file_path, 'rb') as note_file:
                encrypted_body = note_file.read()
                try:
                    decrypted_body = cipher.decrypt(encrypted_body).decode()
                except cryptography.fernet.InvalidToken:
                    messagebox.showerror("Ошибка", "Неверный ключ.")
                    raise InvalidKeyError("Неверный ключ.")
            self.entry_title.delete(0, tk.END)
            self.entry_title.insert(0, note_info['title'] + note_info['timestamp'])
            self.entry_body.delete('1.0', tk.END)
            self.entry_body.insert(tk.END, decrypted_body)

    def save_note(self):
        if self.current_note_id:
            title = self.entry_title.get()
            body = self.entry_body.get("1.0", tk.END)
            note_info = self.notes[self.current_note_id]
            encrypted_body = cipher.encrypt(body.encode())
            with open(note_info['file'], 'wb') as note_file:
                note_file.write(encrypted_body)
            self.notes[self.current_note_id]['title'] = title
            self.save_notes()
            self.update_notes_list()
            messagebox.showinfo("OK", "Заметка сохранена.")
        else:
            messagebox.showwarning("Ошибка", "Нет выбранной заметки для записи.")

    def delete_note(self):
        if self.current_note_id and self.current_note_id in self.notes:
            note_info = self.notes.pop(self.current_note_id)
            os.remove(note_info['file'])
            self.save_notes()
            self.update_notes_list()
            self.entry_title.delete(0, tk.END)
            self.entry_body.delete('1.0', tk.END)
            messagebox.showinfo("Информация", "Заметка удалена.")
            self.current_note_id = None
        else:
            messagebox.showwarning("Предупреждение", "Нет выбранной заметки для удаления.")

    def create_new_note(self):
        title = self.entry_title.get()
        body = self.entry_body.get("1.0", tk.END).strip()
        if title and body:
            if self.notes:
                note_num = str(max([int(id) for id in self.notes.keys()]) + 1)
            else:
                note_num = '1'

            note_id = str(uuid.uuid4())
            encrypted_body = cipher.encrypt(body.encode())
            note_filename = f"{note_id}.privatenote"
            with open(note_filename, 'wb') as note_file:
                note_file.write(encrypted_body)
            self.notes[note_num] = {'title': title, 'file': note_filename,
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            self.save_notes()
            self.update_notes_list()
            messagebox.showinfo("Информация", "Заметка добавлена")
            self.entry_title.delete(0, tk.END)
            self.entry_body.delete('1.0', tk.END)
            self.current_note_id = None
            self.entry_title.delete(0, tk.END)
            self.entry_body.delete('1.0', tk.END)
            self.listbox_notes.selection_clear(0, tk.END)
        else:
            messagebox.showwarning("Ошибка", "Заголовок и тело заметки не должны быть пустыми")

    def change_image(self):
        global key
        global cipher

        image_path = self.image_selector.get()
        key = read_key(image_path)
        cipher = Fernet(key)


if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
