# AutoShop CRM - Full Product Specification

## Overview
AutoShop CRM is a white-label SaaS platform designed specifically for auto repair shops. Each shop gets its own deployment with a custom domain. The system manages customer relationships, work orders, invoicing, appointments, and provides comprehensive analytics.

## Architecture

### Backend (Python + FastAPI)
- **Framework**: FastAPI for high-performance REST API
- **Database**: SQLite for simplicity (easily upgradeable to PostgreSQL)
- **Authentication**: JWT tokens with role-based access control
- **Background Jobs**: APScheduler for mileage predictions and reminders

### Frontend (React)
- **Framework**: React 18 with Vite for fast development
- **Styling**: Tailwind CSS for responsive design
- **State Management**: Zustand for global state
- **Internationalization**: i18next for Bulgarian + English support
- **API Client**: Axios with interceptors for authentication

## User Roles & Capabilities

### Super Admin
- Platform-level management
- Shop provisioning and billing
- Feature toggles per shop
- Impersonate shop admins
- View all analytics

### Manager/Owner
- Shop configuration and settings
- Staff management (add/remove)
- Full analytics and reports
- All receptionist capabilities

### Receptionist
- Customer registration
- Appointment management
- Work order creation
- Invoice finalization
- Customer search

### Mechanic
- View assigned work orders
- Update work order status
- Add diagnostic notes
- Add line items (parts/labor)
- Reassign work orders

### Customer
- View owned cars
- View service history
- Book appointments
- Download invoices
- Pay online (if enabled)
- Change password

## Core Features

### 1. Customer Management
- Phone-based authentication
- Auto-generated passwords sent via SMS
- GDPR consent management
- Email and phone tracking
- Multiple cars per customer

### 2. Car Management
- Complete vehicle records (make, model, year, VIN, plate)
- Mileage tracking
- Service interval configuration
- Ownership transfer capability
- Photo attachments

### 3. Work Orders
- Status flow: Created → Diagnosing → In Progress → Done
- Customer intake notes
- Mechanic diagnostic findings
- Parts and labor line items
- Assignment history
- Before/after photos
- Time tracking

### 4. Invoicing
- Auto-generation from work orders
- Sequential invoice numbering per shop
- VAT calculation (20% for Bulgaria)
- PDF export with bilingual support
- Status: Draft → Finalized → Paid
- Stripe integration for online payments

### 5. Appointments
- Customer booking system
- Free-form scheduling
- SMS confirmations
- Status: Requested → Confirmed → Arrived → Rejected
- Auto-conversion to work orders

### 6. SMS Notifications
- Welcome messages with password
- Appointment confirmations
- Car ready notifications
- Service reminders
- Password reset codes
- Usage tracking for billing

### 7. Mileage Prediction & Reminders
- Requires minimum 2 visits
- Calculates average km/day
- Predicts service needs 2 weeks ahead
- Automated daily checks
- Proactive SMS reminders

### 8. Analytics & Reports
- Daily/weekly/monthly revenue
- Mechanic performance metrics
- Popular services analysis
- Customer retention tracking
- Work order completion stats

### 9. Multi-Language Support
- Bulgarian (primary)
- English (secondary)
- User-selectable language
- Persistent preference storage

## Security

### Authentication
- JWT tokens with expiration
- Refresh token support
- Role-based access control
- Password hashing with bcrypt

### Authorization
- Endpoint-level permission checks
- Shop-level data isolation
- Customer data privacy
- Staff hierarchy enforcement

### GDPR Compliance
- Consent tracking
- Data retention policies
- Right to be forgotten
- Data export capability

## Deployment

### Single Shop Deployment
Each shop gets:
- Separate SQLite database
- Own domain/subdomain
- Independent configuration
- Isolated data

### Environment Variables
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./autoshop.db
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+359888123456
STRIPE_SECRET_KEY=your-stripe-key
```

### Background Services
- Scheduler runs daily at 9 AM
- Checks mileage predictions
- Sends service reminders
- Tracks SMS usage

## Billing Model

### Subscription Tiers
- **Basic**: Core features, limited SMS
- **Professional**: Full features, higher SMS allowance
- **Enterprise**: Custom features, unlimited SMS

### Usage-Based Billing
- Monthly subscription fee
- Additional charge per SMS sent
- Super admin tracks usage per shop

## Future Enhancements

### Phase 2
- Mobile apps (iOS/Android)
- Parts inventory management
- Supplier integrations
- Email notifications
- Advanced scheduling

### Phase 3
- Customer feedback system
- Loyalty programs
- Marketing campaigns
- Multi-location support
- Advanced analytics with ML

## Technology Stack Summary

**Backend:**
- Python 3.11+
- FastAPI 0.109+
- SQLAlchemy 2.0+
- Pydantic 2.5+
- Twilio 8.11+
- Stripe 7.11+
- ReportLab 4.0+
- APScheduler 3.10+

**Frontend:**
- React 18.2+
- Vite 5.0+
- TailwindCSS 3.4+
- React Router 6.21+
- i18next 23.7+
- Axios 1.6+
- date-fns 3.2+

**DevOps:**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Pytest for testing

## API Documentation
FastAPI auto-generates interactive API documentation:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI schema: `/openapi.json`

## Testing Strategy

### Backend Tests
- Unit tests for services
- Integration tests for API endpoints
- Authentication flow tests
- Permission tests

### Frontend Tests
- Component tests
- Integration tests
- E2E tests with Playwright

## Support & Maintenance

### Monitoring
- Application logs
- Error tracking
- Performance metrics
- SMS delivery tracking

### Updates
- Security patches
- Feature releases
- Database migrations
- Backward compatibility

---

**Built with ❤️ for auto repair shops**
