import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      // Common
      "welcome": "Welcome",
      "login": "Login",
      "logout": "Logout",
      "submit": "Submit",
      "cancel": "Cancel",
      "save": "Save",
      "delete": "Delete",
      "edit": "Edit",
      "view": "View",
      "search": "Search",
      "loading": "Loading...",
      "error": "Error",
      "success": "Success",
      
      // Navigation
      "dashboard": "Dashboard",
      "customers": "Customers",
      "cars": "Cars",
      "workOrders": "Work Orders",
      "appointments": "Appointments",
      "invoices": "Invoices",
      "staff": "Staff",
      "reports": "Reports",
      "settings": "Settings",
      
      // Auth
      "staffLogin": "Staff Login",
      "customerLogin": "Customer Login",
      "username": "Username",
      "password": "Password",
      "phone": "Phone Number",
      "forgotPassword": "Forgot Password?",
      
      // Customer Portal
      "myCars": "My Cars",
      "myAppointments": "My Appointments",
      "serviceHistory": "Service History",
      "bookAppointment": "Book Appointment",
      "changePassword": "Change Password",
      
      // Work Orders
      "createWorkOrder": "Create Work Order",
      "workOrderStatus": "Status",
      "assignedMechanic": "Assigned Mechanic",
      "reportedIssues": "Reported Issues",
      "mechanicNotes": "Mechanic Notes",
      "lineItems": "Line Items",
      "addLineItem": "Add Line Item",
      
      // Invoices
      "invoiceNumber": "Invoice Number",
      "subtotal": "Subtotal",
      "tax": "Tax",
      "total": "Total",
      "downloadPDF": "Download PDF",
      "payOnline": "Pay Online",
      
      // Statuses
      "status": {
        "created": "Created",
        "diagnosing": "Diagnosing",
        "in_progress": "In Progress",
        "done": "Done",
        "draft": "Draft",
        "finalized": "Finalized",
        "paid": "Paid",
        "requested": "Requested",
        "confirmed": "Confirmed",
        "arrived": "Arrived",
        "rejected": "Rejected"
      }
    }
  },
  bg: {
    translation: {
      // Common
      "welcome": "Добре дошли",
      "login": "Вход",
      "logout": "Изход",
      "submit": "Изпрати",
      "cancel": "Отказ",
      "save": "Запази",
      "delete": "Изтрий",
      "edit": "Редактирай",
      "view": "Преглед",
      "search": "Търсене",
      "loading": "Зареждане...",
      "error": "Грешка",
      "success": "Успех",
      
      // Navigation
      "dashboard": "Табло",
      "customers": "Клиенти",
      "cars": "Автомобили",
      "workOrders": "Работни поръчки",
      "appointments": "Срещи",
      "invoices": "Фактури",
      "staff": "Персонал",
      "reports": "Отчети",
      "settings": "Настройки",
      
      // Auth
      "staffLogin": "Вход за персонал",
      "customerLogin": "Вход за клиент",
      "username": "Потребителско име",
      "password": "Парола",
      "phone": "Телефонен номер",
      "forgotPassword": "Забравена парола?",
      
      // Customer Portal
      "myCars": "Моите автомобили",
      "myAppointments": "Моите срещи",
      "serviceHistory": "История на обслужване",
      "bookAppointment": "Запази час",
      "changePassword": "Смяна на парола",
      
      // Work Orders
      "createWorkOrder": "Създай работна поръчка",
      "workOrderStatus": "Статус",
      "assignedMechanic": "Определен механик",
      "reportedIssues": "Докладвани проблеми",
      "mechanicNotes": "Бележки на механика",
      "lineItems": "Позиции",
      "addLineItem": "Добави позиция",
      
      // Invoices
      "invoiceNumber": "Номер на фактура",
      "subtotal": "Междинна сума",
      "tax": "ДДС",
      "total": "Обща сума",
      "downloadPDF": "Изтегли PDF",
      "payOnline": "Плати онлайн",
      
      // Statuses
      "status": {
        "created": "Създадена",
        "diagnosing": "Диагностика",
        "in_progress": "В процес",
        "done": "Завършена",
        "draft": "Чернова",
        "finalized": "Финализирана",
        "paid": "Платена",
        "requested": "Заявена",
        "confirmed": "Потвърдена",
        "arrived": "Пристигнал",
        "rejected": "Отказана"
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('language') || 'bg',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
