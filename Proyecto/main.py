from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList
from kivymd.uix.card import MDCard

# IMPORTS DEL BACKEND
from backend.database.database_manager import DatabaseManager
from backend.models.event import Event
from backend.models.resource import Resource
from backend.models.scheduler import Scheduler
from datetime import datetime, timedelta

KV = """
MDScreen:
    MDNavigationLayout:
        id: nav_layout

        ScreenManager:
            id: sm

            MDScreen:
                name: "dashboard"
                MDBoxLayout:
                    orientation: "vertical"

                    MDTopAppBar:
                        title: "Smart Event Planner"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("toggle")]]
                        right_action_items: [["plus", lambda x: app.show_create_event_dialog()]]

                    MDScrollView:
                        MDBoxLayout:
                            orientation: "vertical"
                            padding: "16dp"
                            spacing: "12dp"
                            size_hint_y: None
                            height: self.minimum_height

                            MDLabel:
                                text: "Resumen"
                                font_style: "H6"
                                size_hint_y: None
                                height: dp(30)

                            MDBoxLayout:
                                orientation: "horizontal"
                                size_hint_y: None
                                height: dp(60)
                                spacing: "8dp"

                                MDCard:
                                    radius: dp(8)
                                    padding: "8dp"
                                    size_hint_x: 0.33
                                    MDLabel:
                                        text: f"Total: {app.total_events}"
                                        halign: "center"

                                MDCard:
                                    radius: dp(8)
                                    padding: "8dp"
                                    size_hint_x: 0.33
                                    MDLabel:
                                        text: f"Activos: {app.active_events}"
                                        halign: "center"

                                MDCard:
                                    radius: dp(8)
                                    padding: "8dp"
                                    size_hint_x: 0.33
                                    MDLabel:
                                        text: f"Conflictos: {app.conflict_events}"
                                        halign: "center"

                            MDLabel:
                                text: "Eventos Recientes"
                                font_style: "H6"
                                size_hint_y: None
                                height: dp(30)

                            MDList:
                                id: recent_events_list
                                size_hint_y: None
                                height: self.minimum_height

            MDScreen:
                name: "events"
                MDBoxLayout:
                    orientation: "vertical"

                    MDTopAppBar:
                        title: "Gestión de Eventos"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("toggle")]]

                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "16dp"
                        spacing: "8dp"

                        MDTextField:
                            id: search_field
                            hint_text: "Buscar eventos..."
                            mode: "round"
                            size_hint_x: 0.9
                            pos_hint: {"center_x": 0.5}
                            on_text: app.filter_events(self.text)

                        MDScrollView:
                            MDList:
                                id: all_events_list

            MDScreen:
                name: "resources"
                MDBoxLayout:
                    orientation: "vertical"

                    MDTopAppBar:
                        title: "Recursos Disponibles"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("toggle")]]

                    MDScrollView:
                        MDList:
                            id: resources_list

        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)

            MDBoxLayout:
                orientation: "vertical"
                padding: "12dp"
                spacing: "8dp"

                MDLabel:
                    text: "Smart Event Planner"
                    font_style: "H6"
                    font_size: "20sp"
                    bold: True
                    size_hint_y: None
                    height: dp(40)

                MDList:
                    MDListItem:
                        on_release:
                            sm.current = "dashboard"
                            nav_drawer.set_state("close")
                        MDListItemHeadlineText:
                            text: "Dashboard"

                    MDListItem:
                        on_release:
                            sm.current = "events"
                            nav_drawer.set_state("close")
                        MDListItemHeadlineText:
                            text: "Eventos"

                    MDListItem:
                        on_release:
                            sm.current = "resources"
                            nav_drawer.set_state("close")
                        MDListItemHeadlineText:
                            text: "Recursos"

                MDBoxLayout:
                    orientation: "vertical"
                    padding: "8dp"
                    spacing: "8dp"
                    size_hint_y: None
                    height: self.minimum_height

                    # Botones usando MDButton genérico
                    Button:
                        text: "Buscar Horarios"
                        size_hint_x: 1
                        on_release: app.show_slot_search_dialog()

                    Button:
                        text: "Exportar Datos"
                        size_hint_x: 1
                        on_release: app.export_data()

                    Button:
                        text: "Importar Datos"
                        size_hint_x: 1
                        on_release: app.import_data()
"""


class SmartEventPlannerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager("database.json")
        self.scheduler = Scheduler(self.db)
        self.current_event_id = None
        self.total_events = 0
        self.active_events = 0
        self.conflict_events = 0
        self.dialog = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def on_start(self):
        self.load_data()
        self.update_stats()
        self.refresh_ui()

    def load_data(self):
        try:
            self.db.load()
            if not self.db.list_events() and not self.db.list_resources():
                self.create_demo_data()
        except Exception as e:
            print(f"[ERROR] Cargando datos: {e}")

    def create_demo_data(self):
        demo_events = [
            {
                "id": "E001",
                "name": "Cirugía Cardíaca Paciente X",
                "description": "Cirugía de bypass con equipo CEC",
                "event_type": "cirugia_cardiaca",
                "start": datetime.now().strftime("%Y-%m-%dT%H:%M"),
                "end": (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M"),
                "resource_ids": ["OR1", "DR_CIR1", "DR_CARD1", "CEC1", "ENF1", "ENF2", "DR_AN1"]
            },
            {
                "id": "E002",
                "name": "Tomografía de Urgencia",
                "description": "Paciente con sospecha de apendicitis",
                "event_type": "diagnostico",
                "start": (datetime.now() + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M"),
                "end": (datetime.now() + timedelta(hours=4, minutes=30)).strftime("%Y-%m-%dT%H:%M"),
                "resource_ids": ["CT1", "DR_CARD1"]
            }
        ]
        
        for event_data in demo_events:
            self.db.upsert_event(event_data)
        
        print("[INFO] Datos de demostración creados")

    def refresh_ui(self):
        self.update_recent_events()
        self.update_all_events()
        self.update_resources()
        self.update_stats()

    def update_stats(self):
        events = self.db.list_events()
        self.total_events = len(events)
        
        now = datetime.now()
        self.active_events = sum(1 for e in events if datetime.strptime(e["end"], "%Y-%m-%dT%H:%M") > now)
        
        self.conflict_events = 0
        for event_data in events:
            event = Event.from_dict(event_data)
            violations = self.scheduler.validate_event(event)
            if violations:
                self.conflict_events += 1

    def update_recent_events(self):
        container = self.root.ids.recent_events_list
        container.clear_widgets()
        
        events = self.db.list_events()
        if not events:
            no_events = MDLabel(
                text="No hay eventos. Usa el botón + para crear uno.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(60)
            )
            container.add_widget(no_events)
            return
        
        for event_data in events[-5:]:
            self._add_event_card(container, event_data)

    def update_all_events(self):
        container = self.root.ids.all_events_list
        container.clear_widgets()
        
        events = self.db.list_events()
        if not events:
            no_events = MDLabel(
                text="No hay eventos registrados",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(60)
            )
            container.add_widget(no_events)
            return
        
        for event_data in events:
            self._add_event_list_item(container, event_data)

    def update_resources(self):
        container = self.root.ids.resources_list
        container.clear_widgets()
        
        resources = self.db.list_resources()
        if not resources:
            no_res = MDLabel(
                text="No hay recursos en la base de datos",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(60)
            )
            container.add_widget(no_res)
            return
        
        for res_data in resources:
            item = MDListItem(
                MDListItemHeadlineText(text=f"{res_data['name']} ({res_data['id']})"),
                MDListItemSupportingText(text=f"Tipo: {res_data['kind']} | Subtipo: {res_data.get('subtype', 'N/A')}")
            )
            container.add_widget(item)

    def _add_event_card(self, container, event_data):
        try:
            event = Event.from_dict(event_data)
            violations = self.scheduler.validate_event(event)
            
            bg_color = (1, 0.3, 0.3, 0.2) if violations else (0.3, 0.8, 0.3, 0.2)
            status_text = "⚠️ CONFLICTO" if violations else "✓ OK"
            
            card = MDCard(
                orientation="vertical",
                padding="12dp",
                radius=dp(8),
                size_hint_y=None,
                height=dp(100),
                md_bg_color=bg_color
            )
            
            card.add_widget(MDLabel(
                text=f"{event.name}",
                font_style="H6",
                size_hint_y=None,
                height=dp(25)
            ))
            
            card.add_widget(MDLabel(
                text=f"{event.start.strftime('%d/%m %H:%M')} - {event.end.strftime('%H:%M')}",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            ))
            
            card.add_widget(MDLabel(
                text=f"Recursos: {len(event.resource_ids)} | {status_text}",
                theme_text_color="Custom",
                text_color=(0, 0.5, 0, 1) if not violations else (1, 0, 0, 1),
                size_hint_y=None,
                height=dp(20)
            ))
            
            # Usar Button básico de Kivy
            from kivy.uix.button import Button
            btn = Button(
                text="Detalles",
                size_hint_x=1,
                size_hint_y=None,
                height=dp(30)
            )
            btn.bind(on_release=lambda x, e=event_data: self.show_event_details(e))
            card.add_widget(btn)
            
            container.add_widget(card)
            
        except Exception as e:
            print(f"Error creando tarjeta: {e}")

    def _add_event_list_item(self, container, event_data):
        try:
            event = Event.from_dict(event_data)
            violations = self.scheduler.validate_event(event)
            
            item = MDListItem(
                MDListItemHeadlineText(text=f"{event.name}"),
                MDListItemSupportingText(
                    text=f"{event.start.strftime('%d/%m %H:%M')} - {event.end.strftime('%H:%M')}"
                )
            )
            
            if violations:
                for v in violations:
                    item.add_widget(MDListItemSupportingText(
                        text=f"⚠️ {v.message}",
                        theme_text_color="Error"
                    ))
            
            item.bind(on_release=lambda x, e=event_data: self.show_event_details(e))
            container.add_widget(item)
            
        except Exception as e:
            print(f"Error creando item: {e}")

    def show_create_event_dialog(self):
        content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            padding="12dp",
            size_hint_y=None,
            height=dp(450)
        )
        
        fields = {
            "name": MDTextField(hint_text="Nombre del evento", mode="rectangle"),
            "description": MDTextField(hint_text="Descripción", mode="rectangle", multiline=True),
            "event_type": MDTextField(hint_text="Tipo (ej: cirugia_cardiaca, diagnostico)", mode="rectangle"),
            "start": MDTextField(hint_text="Inicio (YYYY-MM-DD HH:MM)", mode="rectangle"),
            "end": MDTextField(hint_text="Fin (YYYY-MM-DD HH:MM)", mode="rectangle"),
            "resource_ids": MDTextField(hint_text="IDs recursos (separados por coma)", mode="rectangle")
        }
        
        for field in fields.values():
            content.add_widget(field)
        
        actions = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            size_hint_y=None,
            height=dp(50)
        )
        
        from kivy.uix.button import Button
        
        cancel_btn = Button(text="Cancelar", size_hint_x=0.5)
        cancel_btn.bind(on_release=lambda x: self.dialog.dismiss())
        
        save_btn = Button(text="Crear Evento", size_hint_x=0.5)
        save_btn.bind(on_release=lambda x: self._save_new_event(fields))
        
        actions.add_widget(cancel_btn)
        actions.add_widget(save_btn)
        content.add_widget(actions)
        
        self.dialog = MDDialog(
            title="Nuevo Evento",
            type="custom",
            content_cls=content
        )
        self.dialog.open()

    def _save_new_event(self, fields):
        try:
            if not all(fields[k].text for k in ["name", "start", "end", "resource_ids"]):
                print("[WARNING] Completa todos los campos obligatorios")
                return
            
            event_dict = {
                "id": f"E{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "name": fields["name"].text,
                "description": fields["description"].text or "",
                "event_type": fields["event_type"].text or "general",
                "start": fields["start"].text,
                "end": fields["end"].text,
                "resource_ids": [r.strip() for r in fields["resource_ids"].text.split(",")]
            }
            
            event = Event.from_dict(event_dict)
            violations = self.scheduler.validate_event(event)
            
            if violations:
                msg = "\n".join([f"• {v.message}" for v in violations])
                print(f"[WARNING] Advertencias:\n{msg}")
                self.db.upsert_event(event_dict)
            else:
                self.db.upsert_event(event_dict)
                print("[SUCCESS] Evento creado exitosamente")
            
            self.dialog.dismiss()
            self.refresh_ui()
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")

    def show_event_details(self, event_data):
        try:
            event = Event.from_dict(event_data)
            violations = self.scheduler.validate_event(event)
            
            content = MDBoxLayout(
                orientation="vertical",
                spacing="8dp",
                padding="12dp",
                size_hint_y=None,
                height=dp(400)
            )
            
            info = [
                f"Nombre: {event.name}",
                f"Tipo: {event.event_type}",
                f"Inicio: {event.start.strftime('%d/%m/%Y %H:%M')}",
                f"Fin: {event.end.strftime('%d/%m/%Y %H:%M')}",
                f"Descripción: {event.description}",
                f"Recursos ({len(event.resource_ids)}): {', '.join(event.resource_ids)}"
            ]
            
            for line in info:
                content.add_widget(MDLabel(
                    text=line,
                    size_hint_y=None,
                    height=dp(25),
                    font_size="12sp"
                ))
            
            if violations:
                content.add_widget(MDLabel(
                    text="⚠️ CONFLICTOS DETECTADOS:",
                    theme_text_color="Error",
                    bold=True,
                    size_hint_y=None,
                    height=dp(25)
                ))
                for v in violations:
                    content.add_widget(MDLabel(
                        text=f"• {v.message}",
                        theme_text_color="Error",
                        size_hint_y=None,
                        height=dp(20),
                        font_size="11sp"
                    ))
            
            actions = MDBoxLayout(
                orientation="horizontal",
                spacing="8dp",
                size_hint_y=None,
                height=dp(50)
            )
            
            from kivy.uix.button import Button
            
            delete_btn = Button(text="Eliminar", size_hint_x=0.5)
            delete_btn.bind(on_release=lambda x: self.delete_event(event.id))
            
            close_btn = Button(text="Cerrar", size_hint_x=0.5)
            close_btn.bind(on_release=lambda x: self.dialog.dismiss())
            
            actions.add_widget(delete_btn)
            actions.add_widget(close_btn)
            content.add_widget(actions)
            
            self.dialog = MDDialog(
                title="Detalles del Evento",
                type="custom",
                content_cls=content
            )
            self.dialog.open()
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")

    def delete_event(self, event_id):
        if self.dialog:
            self.dialog.dismiss()
        
        self.db.delete_event(event_id)
        print(f"[INFO] Evento {event_id} eliminado")
        self.refresh_ui()

    def show_slot_search_dialog(self):
        content = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            padding="12dp",
            size_hint_y=None,
            height=dp(350)
        )
        
        fields = {
            "roles": MDTextField(hint_text="Roles (ej: cardiologo, cirujano)", mode="rectangle"),
            "subtypes": MDTextField(hint_text="Subtipos (ej: quirófano, tomografo)", mode="rectangle"),
            "duration": MDTextField(hint_text="Duración en horas", mode="rectangle", text="2"),
            "from_date": MDTextField(hint_text="Desde (YYYY-MM-DD HH:MM)", mode="rectangle")
        }
        
        for field in fields.values():
            content.add_widget(field)
        
        actions = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            size_hint_y=None,
            height=dp(50)
        )
        
        from kivy.uix.button import Button
        
        cancel_btn = Button(text="Cancelar", size_hint_x=0.5)
        cancel_btn.bind(on_release=lambda x: self.dialog.dismiss())
        
        search_btn = Button(text="Buscar", size_hint_x=0.5)
        search_btn.bind(on_release=lambda x: self._search_slots(fields))
        
        actions.add_widget(cancel_btn)
        actions.add_widget(search_btn)
        content.add_widget(actions)
        
        self.dialog = MDDialog(
            title="Buscar Horarios Disponibles",
            type="custom",
            content_cls=content
        )
        self.dialog.open()

    def _search_slots(self, fields):
        try:
            if not fields["duration"].text or not fields["from_date"].text:
                print("[WARNING] Completa duración y fecha")
                return
            
            filters = {
                "roles": [r.strip() for r in fields["roles"].text.split(",") if r.strip()] if fields["roles"].text else [],
                "subtypes": [s.strip() for s in fields["subtypes"].text.split(",") if s.strip()] if fields["subtypes"].text else []
            }
            
            duration = timedelta(hours=float(fields["duration"].text))
            from_dt = datetime.strptime(fields["from_date"].text, "%Y-%m-%d %H:%M")
            
            slots = self.scheduler.find_next_slots(
                required_filters=filters,
                duration=duration,
                from_dt=from_dt,
                max_results=5
            )
            
            self.dialog.dismiss()
            
            if not slots:
                print("[ERROR] No se encontraron horarios disponibles")
                return
            
            msg = "✅ Horarios encontrados:\n\n"
            for i, slot in enumerate(slots, 1):
                msg += f"{i}. {slot.start.strftime('%d/%m %H:%M')} - {slot.end.strftime('%H:%M')}\n"
                msg += f"   Recursos: {', '.join([r.id for r in slot.resources])}\n\n"
            
            print(f"[SUCCESS] {msg}")
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")

    def filter_events(self, text):
        container = self.root.ids.all_events_list
        container.clear_widgets()
        
        events = self.db.list_events()
        filtered = [e for e in events if text.lower() in e["name"].lower() or text.lower() in e.get("description", "").lower()]
        
        if not filtered:
            no_results = MDLabel(
                text="No se encontraron resultados",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(60)
            )
            container.add_widget(no_results)
            return
        
        for event_data in filtered:
            self._add_event_list_item(container, event_data)

    def export_data(self):
        try:
            self.db.export_to("database_export.json")
            print("[SUCCESS] Datos exportados a database_export.json")
        except Exception as e:
            print(f"[ERROR] {str(e)}")

    def import_data(self):
        try:
            self.db.import_from("database_import.json")
            print("[SUCCESS] Datos importados exitosamente")
            self.refresh_ui()
        except FileNotFoundError:
            print("[WARNING] No existe database_import.json")
        except Exception as e:
            print(f"[ERROR] {str(e)}")


if __name__ == "__main__":
    SmartEventPlannerApp().run()