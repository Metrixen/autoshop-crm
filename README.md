# AutoShop CRM

A complete **white-label CRM SaaS for auto repair shops**. Each shop gets its own deployment with a custom domain. Customers log in via phone number + password to view their cars, service history, and book appointments. Shop staff manage work orders, invoicing, and customer relationships.

## Features

### User Roles & Capabilities
- **Super Admin** - Platform management, shop provisioning, billing, feature toggles
- **Manager/Owner** - Shop management, staff management, reports & analytics
- **Receptionist** - Customer registration, appointment management, work order creation, invoice finalization
- **Mechanic** - Work order updates, task management, parts & labor tracking
- **Customer** - View cars & service history, book appointments, download invoices, online payments

### Core Functionality
- **Customer Portal** - Dashboard with car overview, active work orders, service history, appointment booking
- **Work Order Management** - Complete lifecycle from creation to completion with status tracking
- **Invoice System** - Auto-generated invoices with PDF export and online payment (Stripe)
- **Appointment System** - Customer requests with receptionist confirmation, SMS notifications
- **SMS Notifications** - Welcome messages, appointment confirmations, completion alerts, service reminders
- **Mileage Prediction** - Proactive service reminders based on predicted mileage
- **Multi-Language** - Bulgarian and English with language switcher
- **Analytics Dashboard** - Revenue tracking, mechanic performance, customer retention metrics
- **GDPR Compliant** - Consent management, configurable data retention

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Vite, React Router
- **Authentication**: JWT tokens with role-based access control
- **Integrations**: Twilio (SMS), Stripe (Payments), ReportLab (PDF generation)
- **Background Jobs**: APScheduler for mileage predictions and reminders
- **API Docs**: Auto-generated OpenAPI/Swagger documentation

## Project Structure

```
autoshop-crm/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings & configuration
│   │   ├── database.py          # SQLite connection & session
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API route handlers
│   │   ├── services/            # Business logic
│   │   ├── middleware/          # Auth, CORS, etc.
│   │   ├── utils/               # Helper utilities
│   │   └── seed.py              # Seed data script
│   ├── tests/                   # Backend tests
│   ├── requirements.txt         # Python dependencies
│   └── alembic/                 # DB migrations
├── frontend/
│   ├── src/
│   │   ├── components/          # Shared UI components
│   │   ├── pages/               # Page components by role
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client
│   │   ├── i18n/                # Translations (BG + EN)
│   │   ├── context/             # React context providers
│   │   └── App.jsx              # Main app component
│   ├── package.json             # Node dependencies
│   └── vite.config.js           # Vite configuration
├── docs/                        # Documentation
├── docker-compose.yml           # Docker setup
├── README.md                    # This file
└── .gitignore                   # Git ignore patterns
```

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using Alembic)
alembic upgrade head

# Seed demo data
python -m app.seed

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///./autoshop.db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio SMS
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

# Shop Configuration
SHOP_NAME=Demo Auto Shop
SHOP_PHONE=+359888123456
SHOP_ADDRESS=Sofia, Bulgaria
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

### Manual Deployment

Each shop deployment requires:
1. Separate SQLite database
2. Unique domain/subdomain
3. Environment variables configured per shop
4. Background scheduler running for mileage predictions

See `docs/deployment.md` for detailed deployment instructions.

## API Documentation

Interactive API documentation is automatically generated and available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## User Roles & Permissions Matrix

| Capability | Super Admin | Manager | Receptionist | Mechanic | Customer |
|---|:---:|:---:|:---:|:---:|:---:|
| Create/manage shops | ✅ | ❌ | ❌ | ❌ | ❌ |
| Platform billing & analytics | ✅ | ❌ | ❌ | ❌ | ❌ |
| Impersonate shop admin | ✅ | ❌ | ❌ | ❌ | ❌ |
| Feature toggles per shop | ✅ | ❌ | ❌ | ❌ | ❌ |
| Add/remove staff | ✅ | ✅ | ❌ | ❌ | ❌ |
| Shop settings & config | ✅ | ✅ | ❌ | ❌ | ❌ |
| View shop reports/analytics | ✅ | ✅ | ❌ | ❌ | ❌ |
| Register customers | ✅ | ✅ | ✅ | ❌ | ❌ |
| Manage appointments | ✅ | ✅ | ✅ | ❌ | Book only |
| Create work orders | ✅ | ✅ | ✅ | ❌ | ❌ |
| Update work order status | ✅ | ✅ | ✅ | ✅ | ❌ |
| Add invoice line items | ✅ | ✅ | ✅ | ✅* | ❌ |
| Finalize invoices | ✅ | ✅ | ✅ | ❌ | ❌ |
| Reassign work orders | ✅ | ✅ | ✅ | ✅ | ❌ |
| View own cars & history | ❌ | ❌ | ❌ | ❌ | ✅ |
| Download invoices | ❌ | ❌ | ❌ | ❌ | ✅ |
| Pay online | ❌ | ❌ | ❌ | ❌ | ✅ |

\* If allowed by shop setting

## Demo Credentials

After running the seed script, you can log in with:

**Super Admin**
- Username: `admin@autoshop.com`
- Password: `admin123`

**Manager**
- Username: `manager@demoshop.bg`
- Password: `manager123`

**Receptionist**
- Phone: `+359888000001`
- Password: `reception123`

**Mechanic**
- Phone: `+359888000002`
- Password: `mechanic123`

**Customer**
- Phone: `+359888111111`
- Password: (auto-generated, shown in seed output)

## SMS Notifications

The system sends SMS notifications for:
1. **Welcome** - New customer registration with auto-generated password
2. **Appointment Confirmed** - Date/time and shop details
3. **Car Ready** - Completion notification with invoice total
4. **Service Reminder** - Proactive reminder based on mileage prediction
5. **Password Reset** - Reset code/link

All SMS messages include a link to the shop's website.

## Mileage Prediction & Service Reminders

- Requires minimum 2 visits with recorded mileage
- Calculates average km/day from visit history
- Configurable service interval per car
- Daily background job checks all cars
- SMS reminder sent when predicted mileage reaches service interval within 2 weeks

## GDPR Compliance

- Consent prompt on customer's first login
- Configurable data retention period per shop
- Customer data export available
- Right to be forgotten implementation

## Support & Documentation

- Full product specification: `docs/product-spec.md`
- API documentation: Available at `/docs` endpoint
- Architecture diagrams: `docs/architecture.md`

## License

Proprietary - All rights reserved

## Contributing

This is a proprietary white-label SaaS product. Internal contributions only.

---

**Built with ❤️ for auto repair shops**