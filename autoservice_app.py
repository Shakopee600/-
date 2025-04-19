import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = 'autoservice_data.json'

class AutoserviceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автосервис 'АвтоМир'")
        self.root.geometry("1000x600")
        
        # Инициализация данных
        self.data = self.init_data()
        self.selected_parts = []
        self.total_var = tk.StringVar(value="0 руб.")
        
        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Создаем все необходимые вкладки
        self.create_clients_tab()
        self.create_cars_tab()
        self.create_orders_tab()
        self.create_parts_tab()
        self.create_new_order_tab()
        
        self.update_all_tables()

    def init_data(self):
        """Инициализация данных"""
        if not os.path.exists(DATA_FILE):
            return {
                'clients': [],
                'cars': [],
                'orders': [],
                'parts': [],
                'next_ids': {
                    'client': 1,
                    'car': 1,
                    'order': 1,
                    'part': 1
                }
            }
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'clients': [],
                'cars': [],
                'orders': [],
                'parts': [],
                'next_ids': {
                    'client': 1,
                    'car': 1,
                    'order': 1,
                    'part': 1
                }
            }
    
    def save_data(self):
        """Сохранение данных в файл"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
    
    def get_next_id(self, entity_type):
        """Получение следующего ID"""
        next_id = self.data['next_ids'][entity_type]
        self.data['next_ids'][entity_type] += 1
        return next_id
    
    def update_all_tables(self):
        """Обновление всех таблиц"""
        self.update_clients_table()
        self.update_cars_table()
        self.update_orders_table()
        self.update_parts_table()

    # Методы для вкладки клиентов
    def create_clients_tab(self):
        """Вкладка клиентов"""
        self.clients_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_tab, text="Клиенты")
        
        toolbar = ttk.Frame(self.clients_tab)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        add_btn = ttk.Button(toolbar, text="Добавить", command=self.add_client)
        add_btn.pack(side='left', padx=2)
        
        edit_btn = ttk.Button(toolbar, text="Редактировать", command=self.edit_client)
        edit_btn.pack(side='left', padx=2)
        
        del_btn = ttk.Button(toolbar, text="Удалить", command=self.delete_client)
        del_btn.pack(side='left', padx=2)
        
        columns = ("id", "fio", "phone", "email")
        self.clients_table = ttk.Treeview(self.clients_tab, columns=columns, show="headings")
        
        self.clients_table.heading("id", text="ID")
        self.clients_table.heading("fio", text="ФИО")
        self.clients_table.heading("phone", text="Телефон")
        self.clients_table.heading("email", text="Email")
        
        scrollbar = ttk.Scrollbar(self.clients_tab, orient="vertical", command=self.clients_table.yview)
        self.clients_table.configure(yscrollcommand=scrollbar.set)
        
        self.clients_table.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')

    def update_clients_table(self):
        """Обновление таблицы клиентов"""
        for row in self.clients_table.get_children():
            self.clients_table.delete(row)
        
        for client in self.data['clients']:
            self.clients_table.insert("", "end", values=(
                client['id'],
                client['fio'],
                client['phone'],
                client['email']
            ))
    
    def add_client(self):
        """Добавление нового клиента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление клиента")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        fio_entry = ttk.Entry(dialog)
        fio_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Телефон:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        phone_entry = ttk.Entry(dialog)
        phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        email_entry = ttk.Entry(dialog)
        email_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        def save():
            if not fio_entry.get().strip():
                messagebox.showerror("Ошибка", "Введите ФИО клиента")
                return
                
            client = {
                'id': self.get_next_id('client'),
                'fio': fio_entry.get().strip(),
                'phone': phone_entry.get().strip(),
                'email': email_entry.get().strip()
            }
            self.data['clients'].append(client)
            self.save_data()
            self.update_clients_table()
            dialog.destroy()
            messagebox.showinfo("Успех", "Клиент успешно добавлен")
            return client  # Возвращаем созданного клиента
        
        save_btn = ttk.Button(dialog, text="Сохранить", command=lambda: [save(), self.add_car_dialog(save()['id'])])
        save_btn.grid(row=3, column=1, padx=5, pady=5, sticky='e')
    
    def edit_client(self):
        """Редактирование клиента"""
        selected = self.clients_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента для редактирования")
            return
        
        client_id = self.clients_table.item(selected)['values'][0]
        client = next(c for c in self.data['clients'] if c['id'] == client_id)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование клиента")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        fio_entry = ttk.Entry(dialog)
        fio_entry.insert(0, client['fio'])
        fio_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Телефон:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        phone_entry = ttk.Entry(dialog)
        phone_entry.insert(0, client['phone'])
        phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        email_entry = ttk.Entry(dialog)
        email_entry.insert(0, client['email'])
        email_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        def save():
            if not fio_entry.get().strip():
                messagebox.showerror("Ошибка", "Введите ФИО клиента")
                return
                
            client['fio'] = fio_entry.get().strip()
            client['phone'] = phone_entry.get().strip()
            client['email'] = email_entry.get().strip()
            self.save_data()
            self.update_clients_table()
            dialog.destroy()
            messagebox.showinfo("Успех", "Данные клиента обновлены")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(
            row=3, column=1, padx=5, pady=5, sticky='e'
        )
    
    def delete_client(self):
        """Удаление клиента"""
        selected = self.clients_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента для удаления")
            return
        
        client_id = self.clients_table.item(selected)['values'][0]
        
        # Проверка на связанные автомобили
        client_cars = [c for c in self.data['cars'] if c['client_id'] == client_id]
        if client_cars:
            messagebox.showwarning(
                "Ошибка", 
                "Нельзя удалить клиента с привязанными автомобилями!\n"
                f"У клиента {len(client_cars)} автомобилей."
            )
            return
        
        if messagebox.askyesno(
            "Подтверждение", 
            "Вы уверены, что хотите удалить этого клиента?"
        ):
            self.data['clients'] = [c for c in self.data['clients'] if c['id'] != client_id]
            self.save_data()
            self.update_clients_table()
            messagebox.showinfo("Успех", "Клиент удален")
    
    def create_cars_tab(self):
        """Вкладка автомобилей"""
        self.cars_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cars_tab, text="Автомобили")
        
        # Панель инструментов
        toolbar = ttk.Frame(self.cars_tab)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        add_btn = ttk.Button(toolbar, text="Добавить", command=self.add_car_dialog)
        add_btn.pack(side='left', padx=2)
        
        edit_btn = ttk.Button(toolbar, text="Редактировать", command=self.edit_car)
        edit_btn.pack(side='left', padx=2)
        
        del_btn = ttk.Button(toolbar, text="Удалить", command=self.delete_car)
        del_btn.pack(side='left', padx=2)
        
        # Таблица автомобилей
        columns = ("id", "vin", "brand", "model", "client_id", "client_fio")
        self.cars_table = ttk.Treeview(
            self.cars_tab, columns=columns, show="headings"
        )
        
        self.cars_table.heading("id", text="ID")
        self.cars_table.heading("vin", text="VIN")
        self.cars_table.heading("brand", text="Марка")
        self.cars_table.heading("model", text="Модель")
        self.cars_table.heading("client_id", text="ID клиента")
        self.cars_table.heading("client_fio", text="Владелец")
        
        self.cars_table.column("id", width=50)
        self.cars_table.column("vin", width=150)
        self.cars_table.column("brand", width=100)
        self.cars_table.column("model", width=100)
        self.cars_table.column("client_id", width=70)
        self.cars_table.column("client_fio", width=150)
        
        scrollbar = ttk.Scrollbar(
            self.cars_tab, orient="vertical", command=self.cars_table.yview
        )
        self.cars_table.configure(yscrollcommand=scrollbar.set)
        
        self.cars_table.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
    
    def update_cars_table(self):
        """Обновление таблицы автомобилей"""
        for row in self.cars_table.get_children():
            self.cars_table.delete(row)
        
        for car in self.data['cars']:
            client = next(
                (c for c in self.data['clients'] if c['id'] == car['client_id']), 
                {'fio': 'Неизвестно'}
            )
            self.cars_table.insert("", "end", values=(
                car['id'],
                car['vin'],
                car['brand'],
                car['model'],
                car['client_id'],
                client['fio']
            ))
    
    def add_car_dialog(self, client_id=None):
        """Диалог добавления автомобиля"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление автомобиля")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Если client_id не указан, показываем выбор клиента
        if client_id is None:
            if not self.data['clients']:
                messagebox.showerror("Ошибка", "Нет клиентов для привязки автомобиля")
                dialog.destroy()
                return
                
            tk.Label(dialog, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
            client_var = tk.StringVar()
            client_combobox = ttk.Combobox(
                dialog, textvariable=client_var,
                values=[f"{c['id']} - {c['fio']}" for c in self.data['clients']],
                state="readonly"
            )
            client_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='we')
            client_combobox.current(0)
        else:
            client = next((c for c in self.data['clients'] if c['id'] == client_id), None)
            if not client:
                messagebox.showerror("Ошибка", "Клиент не найден")
                dialog.destroy()
                return
                
            tk.Label(dialog, text=f"Клиент: {client['fio']}").grid(
                row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w'
            )
        
        tk.Label(dialog, text="VIN:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        vin_entry = ttk.Entry(dialog)
        vin_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Марка:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        brand_entry = ttk.Entry(dialog)
        brand_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Модель:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        model_entry = ttk.Entry(dialog)
        model_entry.grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        def save():
            if client_id is None:
                try:
                    selected_client = client_combobox.get().split(' - ')[0]
                    current_client_id = int(selected_client)
                except (ValueError, IndexError):
                    messagebox.showerror("Ошибка", "Выберите клиента")
                    return
            else:
                current_client_id = client_id
            
            vin = vin_entry.get().strip().upper()
            brand = brand_entry.get().strip()
            model = model_entry.get().strip()
            
            if not vin:
                messagebox.showerror("Ошибка", "Введите VIN автомобиля")
                return
            if not brand:
                messagebox.showerror("Ошибка", "Введите марку автомобиля")
                return
            if not model:
                messagebox.showerror("Ошибка", "Введите модель автомобиля")
                return
            
            # Проверка на уникальность VIN
            if any(c['vin'].upper() == vin for c in self.data['cars']):
                messagebox.showerror("Ошибка", "Автомобиль с таким VIN уже существует")
                return
            
            car = {
                'id': self.get_next_id('car'),
                'vin': vin,
                'brand': brand,
                'model': model,
                'client_id': current_client_id
            }
            self.data['cars'].append(car)
            self.save_data()
            self.update_cars_table()
            dialog.destroy()
            messagebox.showinfo("Успех", "Автомобиль успешно добавлен")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(
            row=4, column=1, padx=5, pady=5, sticky='e'
        )
    
    def edit_car(self):
        """Редактирование автомобиля"""
        selected = self.cars_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите автомобиль для редактирования")
            return
        
        car_id = self.cars_table.item(selected)['values'][0]
        car = next(c for c in self.data['cars'] if c['id'] == car_id)
        client = next(c for c in self.data['clients'] if c['id'] == car['client_id'])
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование автомобиля")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text=f"Клиент: {client['fio']}").grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w'
        )
        
        tk.Label(dialog, text="VIN:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        vin_entry = ttk.Entry(dialog)
        vin_entry.insert(0, car['vin'])
        vin_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Марка:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        brand_entry = ttk.Entry(dialog)
        brand_entry.insert(0, car['brand'])
        brand_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Модель:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        model_entry = ttk.Entry(dialog)
        model_entry.insert(0, car['model'])
        model_entry.grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        def save():
            vin = vin_entry.get().strip().upper()
            brand = brand_entry.get().strip()
            model = model_entry.get().strip()
            
            if not vin:
                messagebox.showerror("Ошибка", "Введите VIN автомобиля")
                return
            if not brand:
                messagebox.showerror("Ошибка", "Введите марку автомобиля")
                return
            if not model:
                messagebox.showerror("Ошибка", "Введите модель автомобиля")
                return
            
            # Проверка на уникальность VIN (кроме текущего автомобиля)
            if any(c['vin'].upper() == vin and c['id'] != car_id for c in self.data['cars']):
                messagebox.showerror("Ошибка", "Автомобиль с таким VIN уже существует")
                return
            
            car['vin'] = vin
            car['brand'] = brand
            car['model'] = model
            self.save_data()
            self.update_cars_table()
            dialog.destroy()
            messagebox.showinfo("Успех", "Данные автомобиля обновлены")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(
            row=4, column=1, padx=5, pady=5, sticky='e'
        )
    
    def delete_car(self):
        """Удаление автомобиля"""
        selected = self.cars_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите автомобиль для удаления")
            return
        
        car_id = self.cars_table.item(selected)['values'][0]
        
        # Проверка на связанные заказы
        car_orders = [o for o in self.data['orders'] if o.get('car_id') == car_id]
        if car_orders:
            messagebox.showwarning(
                "Ошибка", 
                "Нельзя удалить автомобиль с привязанными заказами!\n"
                f"У автомобиля {len(car_orders)} заказов."
            )
            return
        
        if messagebox.askyesno(
            "Подтверждение", 
            "Вы уверены, что хотите удалить этот автомобиль?"
        ):
            self.data['cars'] = [c for c in self.data['cars'] if c['id'] != car_id]
            self.save_data()
            self.update_cars_table()
            messagebox.showinfo("Успех", "Автомобиль удален")
    
    def create_orders_tab(self):
        """Вкладка заказов"""
        self.orders_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_tab, text="Заказы")
        
        # Панель инструментов
        toolbar = ttk.Frame(self.orders_tab)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        view_btn = ttk.Button(toolbar, text="Просмотреть", command=self.view_order)
        view_btn.pack(side='left', padx=2)
        
        status_btn = ttk.Button(toolbar, text="Изменить статус", command=self.change_order_status)
        status_btn.pack(side='left', padx=2)
        
        del_btn = ttk.Button(toolbar, text="Удалить", command=self.delete_order)
        del_btn.pack(side='left', padx=2)
        
        # Таблица заказов
        columns = ("id", "date", "client", "car", "status", "total")
        self.orders_table = ttk.Treeview(
            self.orders_tab, columns=columns, show="headings"
        )
        
        self.orders_table.heading("id", text="ID")
        self.orders_table.heading("date", text="Дата")
        self.orders_table.heading("client", text="Клиент")
        self.orders_table.heading("car", text="Автомобиль")
        self.orders_table.heading("status", text="Статус")
        self.orders_table.heading("total", text="Сумма")
        
        self.orders_table.column("id", width=50)
        self.orders_table.column("date", width=120)
        self.orders_table.column("client", width=150)
        self.orders_table.column("car", width=150)
        self.orders_table.column("status", width=100)
        self.orders_table.column("total", width=80)
        
        scrollbar = ttk.Scrollbar(
            self.orders_tab, orient="vertical", command=self.orders_table.yview
        )
        self.orders_table.configure(yscrollcommand=scrollbar.set)
        
        self.orders_table.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
    
    def update_orders_table(self):
        """Обновление таблицы заказов"""
        for row in self.orders_table.get_children():
            self.orders_table.delete(row)
        
        for order in self.data['orders']:
            client = next(
                (c for c in self.data['clients'] if c['id'] == order['client_id']), 
                {'fio': 'Неизвестно'}
            )
            car = next(
                (c for c in self.data['cars'] if c['id'] == order.get('car_id')), 
                {'brand': '?', 'model': '?', 'vin': '?'}
            )
            self.orders_table.insert("", "end", values=(
                order['id'],
                order['date'],
                client['fio'],
                f"{car['brand']} {car['model']} ({car['vin']})",
                order['status'],
                f"{order['total']} руб."
            ))
    
    def view_order(self):
        """Просмотр деталей заказа"""
        selected = self.orders_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для просмотра")
            return
        
        order_id = self.orders_table.item(selected)['values'][0]
        order = next(o for o in self.data['orders'] if o['id'] == order_id)
        client = next(c for c in self.data['clients'] if c['id'] == order['client_id'])
        car = next(c for c in self.data['cars'] if c['id'] == order.get('car_id'))
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Заказ №{order_id}")
        dialog.geometry("600x400")
        
        # Основная информация
        info_frame = ttk.LabelFrame(dialog, text="Информация о заказе")
        info_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(info_frame, text=f"Дата: {order['date']}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Клиент: {client['fio']}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Телефон: {client['phone']}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Автомобиль: {car['brand']} {car['model']}").pack(anchor='w')
        ttk.Label(info_frame, text=f"VIN: {car['vin']}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Статус: {order['status']}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Общая стоимость: {order['total']} руб.").pack(anchor='w')
        
        # Работы
        works_frame = ttk.LabelFrame(dialog, text="Выполненные работы")
        works_frame.pack(fill='x', padx=5, pady=5)
        
        works_text = "\n".join(order['works']) if order['works'] else "Нет работ"
        ttk.Label(works_frame, text=works_text).pack(anchor='w')
        
        # Запчасти
        parts_frame = ttk.LabelFrame(dialog, text="Использованные запчасти")
        parts_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        if order['parts']:
            columns = ("name", "price", "quantity", "total")
            parts_tree = ttk.Treeview(parts_frame, columns=columns, show="headings")
            
            parts_tree.heading("name", text="Название")
            parts_tree.heading("price", text="Цена")
            parts_tree.heading("quantity", text="Количество")
            parts_tree.heading("total", text="Сумма")
            
            for part in order['parts']:
                parts_tree.insert("", "end", values=(
                    part['name'],
                    f"{part['price']} руб.",
                    part['quantity'],
                    f"{part['price'] * part['quantity']} руб."
                ))
            
            scrollbar = ttk.Scrollbar(parts_frame, orient="vertical", command=parts_tree.yview)
            parts_tree.configure(yscrollcommand=scrollbar.set)
            
            parts_tree.pack(fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
        else:
            ttk.Label(parts_frame, text="Нет запчастей").pack(anchor='w')
    
    def change_order_status(self):
        """Изменение статуса заказа"""
        selected = self.orders_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для изменения статуса")
            return
        
        order_id = self.orders_table.item(selected)['values'][0]
        order = next(o for o in self.data['orders'] if o['id'] == order_id)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменение статуса заказа")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text=f"Заказ №{order_id}").pack(pady=5)
        ttk.Label(dialog, text=f"Текущий статус: {order['status']}").pack(pady=5)
        
        status_var = tk.StringVar(value=order['status'])
        ttk.Radiobutton(dialog, text="В работе", variable=status_var, value="в работе").pack(anchor='w')
        ttk.Radiobutton(dialog, text="Готово", variable=status_var, value="готово").pack(anchor='w')
        ttk.Radiobutton(dialog, text="Отменен", variable=status_var, value="отменен").pack(anchor='w')
        
        def save():
            order['status'] = status_var.get()
            self.save_data()
            self.update_orders_table()
            dialog.destroy()
            messagebox.showinfo("Успех", "Статус заказа обновлен")
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
    
    def delete_order(self):
        """Удаление заказа"""
        selected = self.orders_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для удаления")
            return
        
        order_id = self.orders_table.item(selected)['values'][0]
        
        if messagebox.askyesno(
            "Подтверждение", 
            "Вы уверены, что хотите удалить этот заказ?\n"
            "Это действие нельзя отменить."
        ):
            # Возвращаем запчасти на склад
            order = next(o for o in self.data['orders'] if o['id'] == order_id)
            for part_in_order in order.get('parts', []):
                part = next(
                    (p for p in self.data['parts'] if p['id'] == part_in_order['part_id']), 
                    None
                )
                if part:
                    part['quantity'] += part_in_order['quantity']
            
            self.data['orders'] = [o for o in self.data['orders'] if o['id'] != order_id]
            self.save_data()
            self.update_orders_table()
            self.update_parts_table()
            messagebox.showinfo("Успех", "Заказ удален")
    
    def create_parts_tab(self):
        """Вкладка запчастей"""
        self.parts_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.parts_tab, text="Запчасти")
        
        # Панель инструментов
        toolbar = ttk.Frame(self.parts_tab)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        add_btn = ttk.Button(toolbar, text="Добавить", command=self.add_part)
        add_btn.pack(side='left', padx=2)
        
        edit_btn = ttk.Button(toolbar, text="Редактировать", command=self.edit_part)
        edit_btn.pack(side='left', padx=2)
        
        del_btn = ttk.Button(toolbar, text="Удалить", command=self.delete_part)
        del_btn.pack(side='left', padx=2)
        
        # Таблица запчастей
        columns = ("id", "name", "price", "quantity")
        self.parts_table = ttk.Treeview(
            self.parts_tab, columns=columns, show="headings"
        )
        
        self.parts_table.heading("id", text="ID")
        self.parts_table.heading("name", text="Название")
        self.parts_table.heading("price", text="Цена")
        self.parts_table.heading("quantity", text="Количество")
        
        self.parts_table.column("id", width=50)
        self.parts_table.column("name", width=200)
        self.parts_table.column("price", width=100)
        self.parts_table.column("quantity", width=100)
        
        scrollbar = ttk.Scrollbar(
            self.parts_tab, orient="vertical", command=self.parts_table.yview
        )
        self.parts_table.configure(yscrollcommand=scrollbar.set)
        
        self.parts_table.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
    
    def update_parts_table(self):
        """Обновление таблицы запчастей"""
        for row in self.parts_table.get_children():
            self.parts_table.delete(row)
        
        for part in self.data['parts']:
            self.parts_table.insert("", "end", values=(
                part['id'],
                part['name'],
                f"{part['price']} руб.",
                part['quantity']
            ))
    
    def add_part(self):
        """Добавление запчасти"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление запчасти")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Цена:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Количество:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        quantity_entry = ttk.Entry(dialog)
        quantity_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        def save():
            try:
                name = name_entry.get().strip()
                price = float(price_entry.get())
                quantity = int(quantity_entry.get())
                
                if not name:
                    messagebox.showerror("Ошибка", "Введите название запчасти")
                    return
                if price <= 0:
                    messagebox.showerror("Ошибка", "Цена должна быть больше 0")
                    return
                if quantity < 0:
                    messagebox.showerror("Ошибка", "Количество не может быть отрицательным")
                    return
                
                part = {
                    'id': self.get_next_id('part'),
                    'name': name,
                    'price': price,
                    'quantity': quantity
                }
                self.data['parts'].append(part)
                self.save_data()
                self.update_parts_table()
                dialog.destroy()
                messagebox.showinfo("Успех", "Запчасть успешно добавлена")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения для цены и количества")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(
            row=3, column=1, padx=5, pady=5, sticky='e'
        )
    
    def edit_part(self):
        """Редактирование запчасти"""
        selected = self.parts_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запчасть для редактирования")
            return
        
        part_id = self.parts_table.item(selected)['values'][0]
        part = next(p for p in self.data['parts'] if p['id'] == part_id)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование запчасти")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = ttk.Entry(dialog)
        name_entry.insert(0, part['name'])
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Цена:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        price_entry = ttk.Entry(dialog)
        price_entry.insert(0, str(part['price']))
        price_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        tk.Label(dialog, text="Количество:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        quantity_entry = ttk.Entry(dialog)
        quantity_entry.insert(0, str(part['quantity']))
        quantity_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        def save():
            try:
                name = name_entry.get().strip()
                price = float(price_entry.get())
                quantity = int(quantity_entry.get())
                
                if not name:
                    messagebox.showerror("Ошибка", "Введите название запчасти")
                    return
                if price <= 0:
                    messagebox.showerror("Ошибка", "Цена должна быть больше 0")
                    return
                if quantity < 0:
                    messagebox.showerror("Ошибка", "Количество не может быть отрицательным")
                    return
                
                part['name'] = name
                part['price'] = price
                part['quantity'] = quantity
                self.save_data()
                self.update_parts_table()
                dialog.destroy()
                messagebox.showinfo("Успех", "Данные запчасти обновлены")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения для цены и количества")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(
            row=3, column=1, padx=5, pady=5, sticky='e'
        )
    
    def delete_part(self):
        """Удаление запчасти"""
        selected = self.parts_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запчасть для удаления")
            return
        
        part_id = self.parts_table.item(selected)['values'][0]
        
        # Проверка на использование в заказах
        part_in_orders = False
        for order in self.data['orders']:
            for part in order.get('parts', []):
                if part['part_id'] == part_id:
                    part_in_orders = True
                    break
            if part_in_orders:
                break
        
        if part_in_orders:
            messagebox.showwarning(
                "Ошибка", 
                "Нельзя удалить запчасть, которая используется в заказах!"
            )
            return
        
        if messagebox.askyesno(
            "Подтверждение", 
            "Вы уверены, что хотите удалить эту запчасть?"
        ):
            self.data['parts'] = [p for p in self.data['parts'] if p['id'] != part_id]
            self.save_data()
            self.update_parts_table()
            messagebox.showinfo("Успех", "Запчасть удалена")
    
    def create_new_order_tab(self):
        """Вкладка создания нового заказа"""
        self.new_order_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.new_order_tab, text="Новый заказ")
        
        main_frame = ttk.Frame(self.new_order_tab)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Выбор клиента
        ttk.Label(scrollable_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.client_var = tk.StringVar()
        self.client_combobox = ttk.Combobox(
            scrollable_frame, textvariable=self.client_var,
            values=[f"{c['id']} - {c['fio']}" for c in self.data['clients']],
            state="readonly"
        )
        self.client_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        if self.data['clients']:
            self.client_combobox.current(0)
        
        # Выбор автомобиля
        ttk.Label(scrollable_frame, text="Автомобиль:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.car_var = tk.StringVar()
        self.car_combobox = ttk.Combobox(scrollable_frame, textvariable=self.car_var, state="readonly")
        self.car_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        self.client_combobox.bind("<<ComboboxSelected>>", self.update_cars_combobox)
        
        # Работы
        ttk.Label(scrollable_frame, text="Работы:").grid(row=2, column=0, padx=5, pady=5, sticky='ne')
        self.works_text = tk.Text(scrollable_frame, height=5, width=40)
        self.works_text.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        # Запчасти
        ttk.Label(scrollable_frame, text="Запчасти:").grid(row=3, column=0, padx=5, pady=5, sticky='ne')
        
        self.parts_frame = ttk.Frame(scrollable_frame)
        self.parts_frame.grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        columns = ("name", "price", "quantity", "total")
        self.selected_parts_table = ttk.Treeview(self.parts_frame, columns=columns, show="headings", height=4)
        
        self.selected_parts_table.heading("name", text="Название")
        self.selected_parts_table.heading("price", text="Цена")
        self.selected_parts_table.heading("quantity", text="Количество")
        self.selected_parts_table.heading("total", text="Сумма")
        
        scrollbar = ttk.Scrollbar(self.parts_frame, orient="vertical", command=self.selected_parts_table.yview)
        self.selected_parts_table.configure(yscrollcommand=scrollbar.set)
        
        self.selected_parts_table.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Панель добавления запчастей
        parts_toolbar = ttk.Frame(scrollable_frame)
        parts_toolbar.grid(row=4, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(parts_toolbar, text="Добавить запчасть:").pack(side='left')
        
        self.part_var = tk.StringVar()
        self.part_combobox = ttk.Combobox(
            parts_toolbar, textvariable=self.part_var,
            values=[f"{p['id']} - {p['name']} ({p['price']} руб., {p['quantity']} шт.)" for p in self.data['parts']],
            width=30, state="readonly"
        )
        self.part_combobox.pack(side='left', padx=5)
        
        ttk.Label(parts_toolbar, text="Кол-во:").pack(side='left')
        self.part_quantity = ttk.Spinbox(parts_toolbar, from_=1, to=100, width=5)
        self.part_quantity.pack(side='left', padx=5)
        
        ttk.Button(parts_toolbar, text="Добавить", command=self.add_part_to_order).pack(side='left')
        
        # Кнопка удаления выбранной запчасти
        ttk.Button(scrollable_frame, text="Удалить выбранную запчасть", command=self.remove_selected_part).grid(
            row=5, column=1, padx=5, pady=5, sticky='w'
        )
        
        # Итоговая сумма
        self.total_var = tk.StringVar(value="0 руб.")
        ttk.Label(scrollable_frame, text="Итого:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(scrollable_frame, textvariable=self.total_var, font=('Arial', 10, 'bold')).grid(
            row=6, column=1, padx=5, pady=5, sticky='w'
        )
        
        ttk.Button(scrollable_frame, text="Создать заказ", command=self.save_new_order).grid(
            row=7, column=1, padx=5, pady=10, sticky='e'
        )
        
        self.selected_parts = []
        self.update_cars_combobox()
        self.update_parts_combobox()

    def update_cars_combobox(self, event=None):
        """Обновление списка автомобилей при выборе клиента"""
        selected_client = self.client_combobox.get().split(' - ')[0]
        if not selected_client.isdigit():
            return
        
        client_id = int(selected_client)
        client_cars = [c for c in self.data['cars'] if c['client_id'] == client_id]
        
        self.car_combobox['values'] = [f"{c['id']} - {c['brand']} {c['model']} ({c['vin']})" for c in client_cars]
        if client_cars:
            self.car_combobox.current(0)
        else:
            self.car_combobox.set('')
    
    def update_parts_combobox(self):
        """Обновление списка доступных запчастей"""
        available_parts = []
        for part in self.data['parts']:
            # Проверяем, сколько уже добавлено этой запчасти в заказ
            added_quantity = sum(p['quantity'] for p in self.selected_parts if p['part_id'] == part['id'])
            available_quantity = part['quantity'] - added_quantity
            
            if available_quantity > 0:
                available_parts.append(
                    f"{part['id']} - {part['name']} ({part['price']} руб., {available_quantity} шт.)"
                )
        
        self.part_combobox['values'] = available_parts
        if available_parts:
            self.part_combobox.current(0)
        else:
            self.part_combobox.set('')

    def add_part_to_order(self):
        """Добавление запчасти к заказу"""
        part_str = self.part_combobox.get()
        if not part_str:
            messagebox.showwarning("Ошибка", "Выберите запчасть")
            return
        
        try:
            part_id = int(part_str.split(' - ')[0])
            quantity = int(self.part_quantity.get())
        except (ValueError, IndexError):
            messagebox.showerror("Ошибка", "Некорректные данные")
            return
        
        if quantity <= 0:
            messagebox.showerror("Ошибка", "Количество должно быть больше 0")
            return
        
        part = next((p for p in self.data['parts'] if p['id'] == part_id), None)
        if not part:
            messagebox.showerror("Ошибка", "Запчасть не найдена")
            return
        
        # Проверяем доступное количество
        added_quantity = sum(p['quantity'] for p in self.selected_parts if p['part_id'] == part_id)
        available_quantity = part['quantity'] - added_quantity
        
        if quantity > available_quantity:
            messagebox.showerror("Ошибка", 
                f"Недостаточно запчастей на складе. Доступно: {available_quantity}")
            return
        
        # Проверяем, не добавлена ли уже эта запчасть
        for item in self.selected_parts:
            if item['part_id'] == part_id:
                item['quantity'] += quantity
                break
        else:
            self.selected_parts.append({
                'part_id': part_id,
                'name': part['name'],
                'price': part['price'],
                'quantity': quantity
            })
        
        # Обновляем таблицу
        self.update_selected_parts_table()
        self.update_parts_combobox()
        self.calculate_total()

    def remove_selected_part(self):
        """Удаление выбранной запчасти из заказа"""
        selected = self.selected_parts_table.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запчасть для удаления")
            return
        
        part_name = self.selected_parts_table.item(selected)['values'][0]
        self.selected_parts = [p for p in self.selected_parts if p['name'] != part_name]
        
        self.update_selected_parts_table()
        self.update_parts_combobox()
        self.calculate_total()

    def update_selected_parts_table(self):
        """Обновление таблицы выбранных запчастей"""
        for row in self.selected_parts_table.get_children():
            self.selected_parts_table.delete(row)
        
        for part in self.selected_parts:
            self.selected_parts_table.insert("", "end", values=(
                part['name'],
                f"{part['price']} руб.",
                part['quantity'],
                f"{part['price'] * part['quantity']} руб."
            ))

    def calculate_total(self):
        """Расчет общей суммы заказа"""
        parts_cost = sum(p['price'] * p['quantity'] for p in self.selected_parts)
        works = self.works_text.get("1.0", "end-1c").split('\n')
        works = [w.strip() for w in works if w.strip()]
        works_cost = len(works) * 1000  # Условная стоимость работы
        total = parts_cost + works_cost
        self.total_var.set(f"{total} руб.")

    def save_new_order(self):
        """Сохранение нового заказа"""
        try:
            # Проверка клиента
            client_str = self.client_combobox.get()
            if not client_str:
                messagebox.showerror("Ошибка", "Выберите клиента")
                return
            
            client_id = int(client_str.split(' - ')[0])
            
            # Проверка автомобиля
            car_str = self.car_combobox.get()
            if not car_str:
                messagebox.showerror("Ошибка", "Выберите автомобиль")
                return
            
            car_id = int(car_str.split(' - ')[0])
            
            # Получаем работы
            works = self.works_text.get("1.0", "end-1c").split('\n')
            works = [w.strip() for w in works if w.strip()]
            
            # Проверяем, что есть либо работы, либо запчасти
            if not works and not self.selected_parts:
                messagebox.showerror("Ошибка", "Добавьте работы или запчасти")
                return
            
            # Проверяем доступность всех запчастей
            for part in self.selected_parts:
                db_part = next((p for p in self.data['parts'] if p['id'] == part['part_id']), None)
                if not db_part or db_part['quantity'] < part['quantity']:
                    messagebox.showerror("Ошибка", 
                        f"Недостаточно запчастей '{part['name']}' на складе")
                    return
            
            # Создаем заказ
            order = {
                'id': self.get_next_id('order'),
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'client_id': client_id,
                'car_id': car_id,
                'works': works,
                'parts': [{
                    'part_id': p['part_id'],
                    'name': p['name'],
                    'price': p['price'],
                    'quantity': p['quantity']
                } for p in self.selected_parts],
                'status': 'в работе',
                'total': int(self.total_var.get().split()[0])
            }
            
            # Уменьшаем количество запчастей на складе
            for part_in_order in self.selected_parts:
                part = next((p for p in self.data['parts'] if p['id'] == part_in_order['part_id']), None)
                if part:
                    part['quantity'] -= part_in_order['quantity']
            
            # Добавляем заказ
            self.data['orders'].append(order)
            self.save_data()
            
            # Очищаем форму
            self.works_text.delete("1.0", "end")
            for row in self.selected_parts_table.get_children():
                self.selected_parts_table.delete(row)
            self.selected_parts.clear()
            self.total_var.set("0 руб.")
            
            # Обновляем таблицы
            self.update_orders_table()
            self.update_parts_table()
            self.update_parts_combobox()
            
            messagebox.showinfo("Успех", f"Заказ №{order['id']} успешно создан!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoserviceApp(root)
    root.mainloop()