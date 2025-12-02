"""SQLAdmin configuration."""

from sqladmin import Admin, ModelView

from src.core.database import engine
from src.models.auth import Organization, OrganizationMember, User
from src.models.crm import Activity, Contact, Deal, Task


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.name, User.created_at]
    column_searchable_list = [User.email, User.name]
    column_sortable_list = [User.id, User.email, User.created_at]
    column_default_sort = ("id", True)
    column_labels = {
        User.id: "ID",
        User.email: "Email",
        User.name: "Имя",
        User.created_at: "Создан",
    }
    can_create = True
    can_edit = True
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class OrganizationAdmin(ModelView, model=Organization):
    column_list = [Organization.id, Organization.name, Organization.created_at]
    column_searchable_list = [Organization.name]
    column_sortable_list = [Organization.id, Organization.name]
    column_labels = {
        Organization.id: "ID",
        Organization.name: "Название",
        Organization.created_at: "Создана",
    }
    can_delete = False
    name = "Организация"
    name_plural = "Организации"
    icon = "fa-solid fa-building"


class OrganizationMemberAdmin(ModelView, model=OrganizationMember):
    column_list = [
        OrganizationMember.id,
        OrganizationMember.organization_id,
        OrganizationMember.user_id,
        OrganizationMember.role,
    ]
    column_sortable_list = [OrganizationMember.id, OrganizationMember.role]
    column_labels = {
        OrganizationMember.id: "ID",
        OrganizationMember.organization_id: "Организация",
        OrganizationMember.user_id: "Пользователь",
        OrganizationMember.role: "Роль",
    }
    name = "Участник"
    name_plural = "Участники"
    icon = "fa-solid fa-users"


class ContactAdmin(ModelView, model=Contact):
    column_list = [
        Contact.id,
        Contact.name,
        Contact.email,
        Contact.phone,
        Contact.organization_id,
        Contact.created_at,
    ]
    column_searchable_list = [Contact.name, Contact.email]
    column_sortable_list = [Contact.id, Contact.name, Contact.created_at]
    column_labels = {
        Contact.id: "ID",
        Contact.name: "Имя",
        Contact.email: "Email",
        Contact.phone: "Телефон",
        Contact.organization_id: "Организация",
        Contact.created_at: "Создан",
    }
    name = "Контакт"
    name_plural = "Контакты"
    icon = "fa-solid fa-address-book"


class DealAdmin(ModelView, model=Deal):
    column_list = [
        Deal.id,
        Deal.title,
        Deal.amount,
        Deal.status,
        Deal.stage,
        Deal.organization_id,
        Deal.created_at,
    ]
    column_searchable_list = [Deal.title]
    column_sortable_list = [Deal.id, Deal.title, Deal.amount, Deal.created_at]
    column_default_sort = ("created_at", True)
    column_labels = {
        Deal.id: "ID",
        Deal.title: "Название",
        Deal.amount: "Сумма",
        Deal.status: "Статус",
        Deal.stage: "Этап",
        Deal.organization_id: "Организация",
        Deal.created_at: "Создана",
    }
    name = "Сделка"
    name_plural = "Сделки"
    icon = "fa-solid fa-handshake"


class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.id,
        Task.title,
        Task.deal_id,
        Task.due_date,
        Task.is_done,
        Task.created_at,
    ]
    column_searchable_list = [Task.title]
    column_sortable_list = [Task.id, Task.due_date, Task.is_done]
    column_labels = {
        Task.id: "ID",
        Task.title: "Название",
        Task.deal_id: "Сделка",
        Task.due_date: "Срок",
        Task.is_done: "Выполнено",
        Task.created_at: "Создана",
    }
    name = "Задача"
    name_plural = "Задачи"
    icon = "fa-solid fa-list-check"


class ActivityAdmin(ModelView, model=Activity):
    column_list = [
        Activity.id,
        Activity.deal_id,
        Activity.type,
        Activity.author_id,
        Activity.created_at,
    ]
    column_sortable_list = [Activity.id, Activity.type, Activity.created_at]
    column_default_sort = ("created_at", True)
    column_labels = {
        Activity.id: "ID",
        Activity.deal_id: "Сделка",
        Activity.type: "Тип",
        Activity.author_id: "Автор",
        Activity.created_at: "Создано",
    }
    can_create = False
    can_edit = False
    can_delete = False
    name = "Активность"
    name_plural = "Активности"
    icon = "fa-solid fa-clock-rotate-left"


def setup_admin(app):
    admin = Admin(
        app,
        engine,
        title="LoveKuhnya CRM",
        base_url="/admin",
    )
    admin.add_view(UserAdmin)
    admin.add_view(OrganizationAdmin)
    admin.add_view(OrganizationMemberAdmin)
    admin.add_view(ContactAdmin)
    admin.add_view(DealAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(ActivityAdmin)
    return admin
