from __future__ import annotations
from datetime import datetime
from gc import callbacks
from uuid import uuid4
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.chip import MDChip
from kivymd.uix.banner import MDBanner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.pickers import MDDatePicker, MDDatePicker, MDTimePicker
from kivymd.toast import toast

from backend.models.event import Event
from backend.models.resource import Resource
from backend.models.constraint import Violation
from backend.models.sheduler import Sheduler
from backend.database.database_manager import DatabaseManager

class ResourceChip(MDChip):
    resource_id=StringProperty()

class NewEventScreen(MDScreen):
    current_date=ObjectProperty(allownone=True)
    start_time=ObjectProperty(allownone=True)
    end_time=ObjectProperty(allownone=True)
    selected_resource_ids=ListProperty([])

    _validation_clock=None
    _confirm_dialog=None

    @property
    def app(self):
        from kivy.app import App
        return App.get_running_app()

    @property
    def db(self)->DatabaseManager:
        return self.app.db

    @property
    def sheduler(self)->Sheduler:
        return self.app.sheduler

    def on_pre_enter(self, *args):
        self.build_resource_chips()

    # chips de recursos
    def build_resource_chips(self):
        box=self.ids.resources_chips_box
        box.clear_widgets()
        self.selected_resource_ids=[]

        for r_dict in self.db.list_resources():
            res=Resource.from_dict(r_dict)
            chip=ResourceChip(
                text=res.name,
                resource_id=res.id,
                check=True,
                icon="check",
                selected_color=self.app.theme_cls.primary_color,
                md_bg_color=self.app.theme_cls.bg_light,
            )
            chip.bind(on_release=self.on_resource_chip_toggled)
            box.add_widget(chip)

    def on_resource_chip_toggled(self, chip: ResourceChip):
        rid=chip.resource_id
        if chip.active:
            if rid not in self.selected_resource_ids:
                self.selected_resource_ids.append(rid)
        else:
            if rid in self.selected_resource_ids:
                self.selected_resource_ids.remove(rid)
        self.shedule_validation()

    # pickers fecha/ hora
    def open_date_selected(self, date_obj):
        picker=MDDatePicker(callback=self.on_date_selected)
        picker.open()

    def on_date_selected(self, date_obj):
        self.current_date = date_obj
        self.ids.date_field.text = date_obj.strftime('%d/%m/%Y')
        self.shedule_validation()

    def open_start_time_picker(self):
        picker=MDTimePicker()
        picker.bind(time=self.on_start_time_selected)
        picker.open()

    def on_start_time_selected(self, instance, time_obj):
        self.start_time=time_obj
        self.ids.start_time_field.text=time_obj.strftime('%H:%M')
        self.shedule_validation()

    def open_end_time_picker(self):
        picker=MDTimePicker()
        picker.bind(time=self.on_end_time_selected)
        picker.open()

    def on_end_time_selected(self, instance, time_obj):
        self.end_time=time_obj
        self.ids.end_time_field.text=time_obj.strftime('%H:%M')
        self.shedule_validation()

    # validacion tiempo real
    def shedule_validation(self):
        if self._validation_clock:
            self._validation_clock.cancel()
        self.validation_clock=Clock.schedule_once(self._do_validation, 0.3)

    def _build_temp_event(self)->Event | None:
        if not (self.current_date and self.start_time and self.end_time):
            return None
        start=datetime.combine(self.current_date, self.start_time)
        end=datetime.combine(self.current_date, self.end_time)
        if end<=start:
            return None
        return Event(
            id=str(uuid4()),
            name=self.ids.name_field.text or "Evento sin nombre",
            description=self.ids.description_field.text or "",
            event_type=self.ids.type_field.text or "",
            start=start,
            end=end,
            resource_ids=list(self.selected_resource_ids),
        )

    def _do_validation(self, *args):
        banner:MDBanner= self.ids.validation_banner
        temp_event=self._build_temp_event()
        if not temp_event:
            banner.text="Complete fecha y horas válidas."
            banner.icon="alert-circle-outline"
            banner.md_bg_color=(1,0.8,0.8,1)
            if not banner.opened:
                banner.open()
            return

        violations:list[Violation]=self.sheduler.validate_event(temp_event)
        if violations:
            banner.text=violations[0].message
            banner.icon="alert-decagram-outline"
            banner.md_bg_color=(1,0.7,0.7,1)
            if not banner.opened:
                banner.open()
        else:
            banner.text="Sin conflictos detectados."
            banner.icon="check-circle-outline"
            banner.md_bg_color=(0.8,1,0.8,1)
            if not banner.opened:
                banner.open()

    # guardado
    def on_save_button(self):
        temp_event=self._build_temp_event()
        if temp_event is None:
            toast("Datos incompletos o inválidos")
            return

        violations=self.sheduler.validate_event(temp_event)
        if violations:
            if not self._confirm_dialog:
                self._confirm_dialog=MDDialog(
                    title="Conflictos detectados",
                    type="simple",
                    buttons=[
                        MDFlatButton(
                            text="CANCELAR",
                            on_release=lambda *_: self._confirm_dialog.dismiss(),
                        ),
                        MDFlatButton(
                            text="IGNORAR Y GUARDAR",
                            on_release=lambda *_: self._force_save(temp_event),
                        ),
                    ]
                )
            self._confirm_dialog.text="\n".join(f"• {v.message}" for v in violations)
            self._confirm_dialog.open()
        else:
            self._force_save(temp_event)

    def force_save(self, event:Event):
        self.db.upsert_event(event.to_dict())
        toast("Evento guardado")
        if self._confirm_dialog:
            self._confirm_dialog.dismiss()
        self.manager.current="events"

