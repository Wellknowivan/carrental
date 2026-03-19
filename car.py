from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from datetime import datetime, timedelta
import json
import os


class CarRentalApp(App):
    def build(self):
        self.title = 'Прокат машинок и батутов'
        self.data_file = 'rental_data.json'
        self.load_data()

        # История для навигации
        self.screen_history = []

        # Главный экран
        self.main_layout = BoxLayout(orientation='vertical')
        self.show_login_screen()

        return self.main_layout

    def go_back(self):
        """Возврат на предыдущий экран"""
        if len(self.screen_history) > 1:
            self.screen_history.pop()
            previous_screen = self.screen_history[-1]
            self.show_screen_by_name(previous_screen)

    def show_screen_by_name(self, screen_name):
        """Показывает экран по имени"""
        if screen_name == 'login':
            self.show_login_screen()
        elif screen_name == 'date':
            self.show_date_screen()
        elif screen_name == 'point_choice':
            self.show_point_choice()
        elif screen_name == 'point':
            self.show_point_screen()
        elif screen_name == 'summary':
            self.show_summary(None)

    def add_to_history(self, screen_name):
        """Добавляет экран в историю"""
        self.screen_history.append(screen_name)

    def show_login_screen(self):
        self.main_layout.clear_widgets()
        self.add_to_history('login')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Заголовок
        layout.add_widget(Label(
            text='ПРОКАТ МАШИНОК',
            size_hint_y=0.2,
            font_size=24,
            color=(0.2, 0.6, 1, 1)
        ))

        # Поле ввода имени
        layout.add_widget(Label(text='Введите ваше имя:', size_hint_y=0.1))
        self.username_input = TextInput(
            multiline=False,
            size_hint_y=0.1,
            hint_text='Имя',
            font_size=18
        )
        layout.add_widget(self.username_input)

        # Кнопка входа
        self.login_btn = Button(
            text='ВОЙТИ',
            size_hint_y=0.15,
            background_color=(0.2, 0.6, 1, 1),
            font_size=18
        )
        self.login_btn.bind(on_press=self.login)
        layout.add_widget(self.login_btn)

        self.main_layout.add_widget(layout)

    def login(self, instance):
        self.username = self.username_input.text
        if self.username:
            self.show_date_screen()
        else:
            self.show_popup('Ошибка', 'Введите имя!')

    def show_date_screen(self):
        self.main_layout.clear_widgets()
        self.add_to_history('date')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Кнопка назад
        back_btn = Button(
            text='← НАЗАД',
            size_hint_y=0.1,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=14
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        layout.add_widget(back_btn)

        # Приветствие
        layout.add_widget(Label(
            text=f'Привет, {self.username}!',
            size_hint_y=0.1,
            font_size=20
        ))

        # Выбор даты
        layout.add_widget(Label(text='Выберите дату:', size_hint_y=0.1))

        current_date = datetime.now().strftime('%Y-%m-%d')
        self.date_input = TextInput(
            text=current_date,
            multiline=False,
            size_hint_y=0.1,
            font_size=18,
            hint_text='ГГГГ-ММ-ДД'
        )
        layout.add_widget(self.date_input)

        # Кнопка выбора точки
        btn = Button(
            text='ВЫБРАТЬ ТОЧКУ',
            size_hint_y=0.15,
            background_color=(0.2, 0.8, 0.2, 1),
            font_size=18
        )
        btn.bind(on_press=self.show_point_list)
        layout.add_widget(btn)

        self.main_layout.add_widget(layout)

    def show_point_list(self, instance):
        self.current_date = self.date_input.text

        # Проверяем формат даты
        try:
            datetime.strptime(self.current_date, '%Y-%m-%d')
        except ValueError:
            self.show_popup('Ошибка', 'Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД')
            return

        # Получаем все точки на эту дату
        self.points_on_date = []
        for p in self.data['points']:
            if p['date'] == self.current_date:
                self.points_on_date.append(p)

        if self.points_on_date:
            self.show_points_list()
        else:
            self.show_point_choice()

    def show_points_list(self):
        """Показывает список всех точек на выбранную дату"""
        self.main_layout.clear_widgets()
        self.add_to_history('points_list')

        main_layout = BoxLayout(orientation='vertical')

        # Кнопка назад
        top_panel = BoxLayout(size_hint_y=0.1, padding=10)
        back_btn = Button(
            text='← НАЗАД',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=14
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_panel.add_widget(back_btn)

        # Заголовок
        top_panel.add_widget(Label(
            text=f'ТОЧКИ НА {self.current_date}',
            font_size=16,
            color=(0.2, 0.6, 1, 1)
        ))
        main_layout.add_widget(top_panel)

        # Список точек
        scroll = ScrollView()
        points_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5, padding=10)
        points_list.bind(minimum_height=points_list.setter('height'))

        for i, point in enumerate(self.points_on_date, 1):
            # Считаем статистику для точки
            car_count = len(point['cars'])
            tramp_count = len(point['trampolines'])
            rental_count = len(point['rentals'])
            point_name = point.get('name', f'Точка {i}')

            # Горизонтальный контейнер для точки и кнопки удаления
            point_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=5)

            point_btn = Button(
                text=f"{point_name}\nМашинок: {car_count} | Батутов: {tramp_count} | Аренд: {rental_count}",
                size_hint_x=0.8,
                background_color=(0.3, 0.5, 0.8, 1),
                font_size=14
            )
            point_btn.bind(on_press=lambda x, p=point: self.select_point(p))
            point_row.add_widget(point_btn)

            # Кнопка удаления точки
            delete_btn = Button(
                text='🗑️',
                size_hint_x=0.2,
                background_color=(0.8, 0.2, 0.2, 1),
                font_size=20
            )
            delete_btn.bind(on_press=lambda x, p=point: self.delete_point(p))
            point_row.add_widget(delete_btn)

            points_list.add_widget(point_row)

        # Кнопка создания новой точки
        new_point_btn = Button(
            text='+ СОЗДАТЬ НОВУЮ ТОЧКУ',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.8, 0.2, 1),
            font_size=14
        )
        new_point_btn.bind(on_press=self.create_new_point_dialog)
        points_list.add_widget(new_point_btn)

        scroll.add_widget(points_list)
        main_layout.add_widget(scroll)

        self.main_layout.add_widget(main_layout)

    def create_new_point_dialog(self, instance):
        """Диалог создания новой точки с названием"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        content.add_widget(Label(text='Введите название точки:', font_size=16))
        point_name_input = TextInput(
            multiline=False,
            hint_text='Например: "Центральная площадка"',
            font_size=14
        )
        content.add_widget(point_name_input)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(text='Отмена')
        create_btn = Button(text='Создать', background_color=(0.2, 0.8, 0.2, 1))

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(create_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='Новая точка',
            content=content,
            size_hint=(0.8, 0.5)
        )

        def create_point(instance):
            point_name = point_name_input.text.strip()
            if not point_name:
                point_name = f"Точка {len([p for p in self.data['points'] if p['date'] == self.current_date]) + 1}"

            point_id = f"{self.current_date}_{len([p for p in self.data['points'] if p['date'] == self.current_date]) + 1}"

            self.current_point = {
                'id': point_id,
                'date': self.current_date,
                'name': point_name,
                'created_at': datetime.now().isoformat(),
                'cars': [],
                'trampolines': [],
                'rentals': []
            }
            self.data['points'].append(self.current_point)
            self.save_data()
            popup.dismiss()
            self.show_point_screen()

        create_btn.bind(on_press=create_point)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def delete_point(self, point):
        """Удаление точки с подтверждением"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        point_name = point.get('name', f"Точка на {point['date']}")
        content.add_widget(Label(
            text=f"Удалить точку '{point_name}'?\nВсе данные будут потеряны!",
            font_size=16
        ))

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        def confirm(instance):
            self.data['points'].remove(point)
            self.save_data()
            popup.dismiss()
            # Обновляем список точек
            self.points_on_date = [p for p in self.data['points'] if p['date'] == self.current_date]
            if self.points_on_date:
                self.show_points_list()
            else:
                self.show_point_choice()

        def cancel(instance):
            popup.dismiss()

        yes_btn = Button(text='Да', background_color=(0.8, 0.2, 0.2, 1))
        yes_btn.bind(on_press=confirm)

        no_btn = Button(text='Нет', background_color=(0.2, 0.8, 0.2, 1))
        no_btn.bind(on_press=cancel)

        btn_layout.add_widget(no_btn)
        btn_layout.add_widget(yes_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='Подтверждение удаления',
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def select_point(self, point):
        """Выбирает существующую точку"""
        self.current_point = point
        self.show_point_screen()

    def show_point_choice(self):
        self.main_layout.clear_widgets()
        self.add_to_history('point_choice')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Кнопка назад
        back_btn = Button(
            text='← НАЗАД',
            size_hint_y=0.1,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=14
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        layout.add_widget(back_btn)

        layout.add_widget(Label(
            text='На эту дату нет точек!',
            size_hint_y=0.2,
            font_size=18,
            color=(1, 0.5, 0, 1)
        ))

        # Кнопка создания новой точки
        new_btn = Button(
            text='СОЗДАТЬ НОВУЮ ТОЧКУ',
            size_hint_y=0.2,
            background_color=(0.2, 0.6, 1, 1),
            font_size=16
        )
        new_btn.bind(on_press=self.create_new_point_dialog)
        layout.add_widget(new_btn)

        self.main_layout.add_widget(layout)

    def show_point_screen(self):
        self.main_layout.clear_widgets()
        self.add_to_history('point')

        main_box = BoxLayout(orientation='vertical')

        # Верхняя панель с навигацией
        top_panel = BoxLayout(size_hint_y=0.1, padding=5)

        # Кнопка назад
        back_btn = Button(
            text='←',
            size_hint_x=0.15,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=20
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_panel.add_widget(back_btn)

        # Информация о точке
        point_name = self.current_point.get('name', f"Точка {self.current_point['id'].split('_')[-1]}")
        top_panel.add_widget(Label(
            text=f"{point_name}\n{self.current_point['date']}",
            font_size=14,
            color=(0.2, 0.6, 1, 1)
        ))

        # Кнопка списка точек
        points_btn = Button(
            text='📋',
            size_hint_x=0.15,
            background_color=(0.2, 0.6, 1, 1),
            font_size=20
        )
        points_btn.bind(on_press=lambda x: self.show_point_list(None))
        top_panel.add_widget(points_btn)

        main_box.add_widget(top_panel)

        # Список машинок и батутов
        scroll = ScrollView(size_hint_y=0.7)
        self.items_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5, padding=10)
        self.items_list.bind(minimum_height=self.items_list.setter('height'))

        self.refresh_items_list()
        scroll.add_widget(self.items_list)
        main_box.add_widget(scroll)

        # Нижняя панель с кнопками
        bottom_panel = BoxLayout(size_hint_y=0.2, spacing=5, padding=5)

        add_car_btn = Button(
            text='➕ МАШИНКА',
            background_color=(0.3, 0.6, 0.3, 1),
            font_size=14
        )
        add_car_btn.bind(on_press=self.add_car_dialog)
        bottom_panel.add_widget(add_car_btn)

        add_tramp_btn = Button(
            text='🎪 БАТУТ',
            background_color=(0.6, 0.4, 0.8, 1),
            font_size=14
        )
        add_tramp_btn.bind(on_press=self.add_trampoline)
        bottom_panel.add_widget(add_tramp_btn)

        summary_btn = Button(
            text='💰 ИТОГИ',
            background_color=(1, 0.6, 0, 1),
            font_size=14
        )
        summary_btn.bind(on_press=self.show_summary)
        bottom_panel.add_widget(summary_btn)

        main_box.add_widget(bottom_panel)
        self.main_layout.add_widget(main_box)

        # Обновляем таймеры каждую секунду
        Clock.schedule_interval(self.update_timers, 1)

    def refresh_items_list(self):
        self.items_list.clear_widgets()

        # Заголовок для машинок
        if self.current_point['cars']:
            self.items_list.add_widget(Label(
                text='🚗 МАШИНКИ:',
                size_hint_y=None,
                height=30,
                bold=True,
                color=(0.2, 0.6, 1, 1)
            ))

            for car in self.current_point['cars']:
                # Создаем горизонтальный контейнер для каждой машинки
                item_box = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=70,
                    spacing=2
                )

                # Определяем цвет в зависимости от статуса
                if car.get('active'):
                    bg_color = (0.2, 0.8, 0.2, 1)
                    time_left = self.get_time_left(car)
                    status = f" (осталось {time_left})"
                else:
                    bg_color = (0.3, 0.3, 0.3, 1)
                    status = ""

                car_btn = Button(
                    text=f"🚗 {car['name']}{status}",
                    size_hint_x=0.7,
                    background_color=bg_color,
                    font_size=14
                )
                car_btn.bind(on_press=lambda x, c=car: self.start_timer(c, 'car'))
                item_box.add_widget(car_btn)

                if car.get('active'):
                    return_btn = Button(
                        text='↩️\nВЕРНУТЬ',
                        size_hint_x=0.3,
                        background_color=(0.8, 0.2, 0.2, 1),
                        font_size=12
                    )
                    return_btn.bind(on_press=lambda x, c=car: self.return_item(c, 'car'))
                    item_box.add_widget(return_btn)

                self.items_list.add_widget(item_box)

        # Заголовок для батутов
        if self.current_point['trampolines']:
            self.items_list.add_widget(Label(
                text='\n🎪 БАТУТЫ:',
                size_hint_y=None,
                height=30,
                bold=True,
                color=(0.6, 0.4, 0.8, 1)
            ))

            for tramp in self.current_point['trampolines']:
                item_box = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=70,
                    spacing=2
                )

                if tramp.get('active'):
                    bg_color = (0.2, 0.8, 0.2, 1)
                    time_left = self.get_time_left(tramp)
                    status = f" (осталось {time_left})"
                else:
                    bg_color = (0.3, 0.3, 0.3, 1)
                    status = ""

                tramp_btn = Button(
                    text=f"🎪 Батут {tramp['id']}{status}",
                    size_hint_x=0.7,
                    background_color=bg_color,
                    font_size=14
                )
                tramp_btn.bind(on_press=lambda x, t=tramp: self.start_timer(t, 'trampoline'))
                item_box.add_widget(tramp_btn)

                if tramp.get('active'):
                    return_btn = Button(
                        text='↩️\nВЕРНУТЬ',
                        size_hint_x=0.3,
                        background_color=(0.8, 0.2, 0.2, 1),
                        font_size=12
                    )
                    return_btn.bind(on_press=lambda x, t=tramp: self.return_item(t, 'trampoline'))
                    item_box.add_widget(return_btn)

                self.items_list.add_widget(item_box)

    def get_time_left(self, item):
        if item.get('end_time'):
            try:
                end = datetime.fromisoformat(item['end_time'])
                now = datetime.now()
                if end > now:
                    diff = end - now
                    minutes = diff.seconds // 60
                    seconds = diff.seconds % 60
                    return f"{minutes:02d}:{seconds:02d}"
            except:
                pass
        return "00:00"

    def return_item(self, item, item_type):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        item_name = item.get('name', f"Батут {item['id']}")
        content.add_widget(Label(
            text=f"Вернуть {item_name} досрочно?",
            font_size=16
        ))

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        def confirm(instance):
            item['active'] = False
            item.pop('end_time', None)
            item.pop('start_time', None)

            self.save_data()
            self.refresh_items_list()
            self.show_popup('Успех', f'{item_name} возвращен!')
            popup.dismiss()

        def cancel(instance):
            popup.dismiss()

        yes_btn = Button(text='Да', background_color=(0.2, 0.8, 0.2, 1))
        yes_btn.bind(on_press=confirm)

        no_btn = Button(text='Нет', background_color=(0.8, 0.2, 0.2, 1))
        no_btn.bind(on_press=cancel)

        btn_layout.add_widget(no_btn)
        btn_layout.add_widget(yes_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='Подтверждение возврата',
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def add_car_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        content.add_widget(Label(text='Введите название машинки:'))
        car_name_input = TextInput(
            multiline=False,
            hint_text='Например: "Красная Ferrari"'
        )
        content.add_widget(car_name_input)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(text='Отмена')
        add_btn = Button(text='Добавить', background_color=(0.2, 0.8, 0.2, 1))

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(add_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='Новая машинка',
            content=content,
            size_hint=(0.8, 0.5)
        )

        def add_car(instance):
            if car_name_input.text:
                car = {
                    'id': len(self.current_point['cars']) + 1,
                    'name': car_name_input.text,
                    'active': False
                }
                self.current_point['cars'].append(car)
                self.save_data()
                self.refresh_items_list()
                popup.dismiss()

        add_btn.bind(on_press=add_car)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def add_trampoline(self, instance):
        tramp = {
            'id': len(self.current_point['trampolines']) + 1,
            'active': False
        }
        self.current_point['trampolines'].append(tramp)
        self.save_data()
        self.refresh_items_list()
        self.show_popup('Успех', 'Батут добавлен!')

    def start_timer(self, item, item_type):
        if item.get('active'):
            self.show_popup('Внимание', 'Этот предмет уже арендован!')
            return

        minutes = 15 if item_type == 'car' else 10
        price = 10 if item_type == 'car' else 5

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        item_name = item.get('name', f"Батут {item['id']}")
        content.add_widget(Label(
            text=f"Арендовать {item_name} на {minutes} мин за {price} руб.?",
            font_size=16
        ))

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        def confirm(instance):
            item['active'] = True
            item['start_time'] = datetime.now().isoformat()
            item['end_time'] = (datetime.now() + timedelta(minutes=minutes)).isoformat()

            rental = {
                'id': len(self.current_point['rentals']) + 1,
                'item_id': item['id'],
                'item_type': item_type,
                'item_name': item_name,
                'start_time': datetime.now().isoformat(),
                'end_time': item['end_time'],
                'price': price,
                'user': self.username,
                'returned_early': False
            }
            self.current_point['rentals'].append(rental)

            self.save_data()
            self.refresh_items_list()
            popup.dismiss()
            self.show_popup('Аренда начата', f"{item_name} арендован на {minutes} минут")

        def cancel(instance):
            popup.dismiss()

        yes_btn = Button(text='Да', background_color=(0.2, 0.8, 0.2, 1))
        yes_btn.bind(on_press=confirm)

        no_btn = Button(text='Нет', background_color=(0.8, 0.2, 0.2, 1))
        no_btn.bind(on_press=cancel)

        btn_layout.add_widget(no_btn)
        btn_layout.add_widget(yes_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='Подтверждение',
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def update_timers(self, dt):
        if not hasattr(self, 'current_point') or not self.current_point:
            return

        updated = False
        now = datetime.now()

        for car in self.current_point['cars']:
            if car.get('active') and car.get('end_time'):
                try:
                    end = datetime.fromisoformat(car['end_time'])
                    if now >= end:
                        car['active'] = False
                        car.pop('end_time', None)
                        car.pop('start_time', None)
                        updated = True
                except:
                    pass

        for tramp in self.current_point['trampolines']:
            if tramp.get('active') and tramp.get('end_time'):
                try:
                    end = datetime.fromisoformat(tramp['end_time'])
                    if now >= end:
                        tramp['active'] = False
                        tramp.pop('end_time', None)
                        tramp.pop('start_time', None)
                        updated = True
                except:
                    pass

        if updated:
            self.save_data()
            self.refresh_items_list()

    def show_summary(self, instance):
        self.main_layout.clear_widgets()
        self.add_to_history('summary')

        layout = BoxLayout(orientation='vertical', padding=10)

        # Верхняя панель с навигацией
        top_panel = BoxLayout(size_hint_y=0.1, padding=5)

        back_btn = Button(
            text='← НАЗАД',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size=14
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_panel.add_widget(back_btn)

        point_name = self.current_point.get('name', f"Точка {self.current_point['id'].split('_')[-1]}")
        top_panel.add_widget(Label(
            text=f"ИТОГИ\n{point_name}",
            font_size=14,
            color=(1, 0.6, 0, 1)
        ))
        layout.add_widget(top_panel)

        layout.add_widget(Label(
            text=f"Сотрудник: {self.username}",
            size_hint_y=0.05,
            font_size=14
        ))

        scroll = ScrollView(size_hint_y=0.6)
        rentals_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
        rentals_list.bind(minimum_height=rentals_list.setter('height'))

        total = 0
        car_count = 0
        tramp_count = 0

        car_rentals = {}
        tramp_rentals = {}

        for rental in self.current_point['rentals']:
            if rental['item_type'] == 'car':
                car_count += 1
                if rental['item_name'] not in car_rentals:
                    car_rentals[rental['item_name']] = []
                car_rentals[rental['item_name']].append(rental)
            else:
                tramp_count += 1
                if rental['item_name'] not in tramp_rentals:
                    tramp_rentals[rental['item_name']] = []
                tramp_rentals[rental['item_name']].append(rental)
            total += rental['price']

        if car_rentals:
            rentals_list.add_widget(Label(
                text='🚗 МАШИНКИ:',
                size_hint_y=None,
                height=30,
                bold=True,
                color=(0.2, 0.6, 1, 1)
            ))

            for car_name, rentals in sorted(car_rentals.items()):
                for i, rental in enumerate(rentals, 1):
                    try:
                        start_time = datetime.fromisoformat(rental['start_time']).strftime('%H:%M')
                    except:
                        start_time = "??:??"

                    rental_text = f"{start_time} - {car_name} - {i} - {rental['price']} руб."
                    rentals_list.add_widget(Label(
                        text=rental_text,
                        size_hint_y=None,
                        height=25,
                        font_size=12
                    ))

        if tramp_rentals:
            rentals_list.add_widget(Label(
                text='\n🎪 БАТУТЫ:',
                size_hint_y=None,
                height=30,
                bold=True,
                color=(0.6, 0.4, 0.8, 1)
            ))

            for tramp_name, rentals in sorted(tramp_rentals.items()):
                for i, rental in enumerate(rentals, 1):
                    try:
                        start_time = datetime.fromisoformat(rental['start_time']).strftime('%H:%M')
                    except:
                        start_time = "??:??"

                    rental_text = f"{start_time} - {tramp_name} - {i} - {rental['price']} руб."
                    rentals_list.add_widget(Label(
                        text=rental_text,
                        size_hint_y=None,
                        height=25,
                        font_size=12
                    ))

        scroll.add_widget(rentals_list)
        layout.add_widget(scroll)

        stats = BoxLayout(orientation='vertical', size_hint_y=0.15, spacing=5)
        stats.add_widget(Label(
            text=f"Машинок арендовано: {car_count}",
            size_hint_y=None,
            height=20
        ))
        stats.add_widget(Label(
            text=f"Батутов арендовано: {tramp_count}",
            size_hint_y=None,
            height=20
        ))
        stats.add_widget(Label(
            text=f"ИТОГО: {total} руб.",
            size_hint_y=None,
            height=30,
            font_size=18,
            color=(0, 1, 0, 1)
        ))
        layout.add_widget(stats)

        self.main_layout.add_widget(layout)

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        popup.open()

    def load_data(self):
        """Загружаем данные из файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {'points': []}
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            self.data = {'points': []}

    def save_data(self):
        """Сохраняем данные в файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            self.show_popup('Ошибка', 'Не удалось сохранить данные!')


if __name__ == '__main__':
    CarRentalApp().run()