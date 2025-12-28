# DailyEaze 📰🥛

A comprehensive **Newspaper & Milk Delivery Management Platform** built with **FastAPI** backend and **HTML/CSS/JavaScript** frontend.

## Features

### 🎯 Core Features
- **User Authentication**: Secure registration and login with password hashing
- **Newspaper Subscriptions**: Browse and subscribe to newspapers by language and genre
- **Milk Package Subscriptions**: Multiple milk package options with flexible delivery
- **Magazine Delivery**: Complementary magazines based on newspaper language
- **Delivery Calendar**: Visual calendar to track delivery schedules
- **Pause/Resume**: Pause and resume subscriptions anytime
- **Payment Gateway**: Stripe integration for fast, secure payments
- **Multi-language Support**: English, Hindi, Tamil, Marathi

### 📊 Subscription Management
- Daily, Weekly, and Monthly delivery frequencies
- Flexible pause periods (default 7 days)
- Real-time subscription status tracking
- Cost calculation based on subscription type

### 📅 Delivery Tracking
- Interactive calendar view with delivery status
- Pending, Delivered, and Paused status indicators
- Monthly calendar visualization

### 💳 Payment Processing
- Stripe payment integration
- Multiple payment methods support
- Payment history tracking
- Secure transaction handling

## Project Structure

```
DailyEaze/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── database/
│   │   ├── database.py        # Database configuration
│   │   └── models.py          # SQLAlchemy ORM models
│   ├── models/
│   │   └── schemas.py         # Pydantic request/response schemas
│   └── routes/
│       ├── auth.py            # Authentication endpoints
│       ├── newspapers.py       # Newspaper management endpoints
│       ├── milk.py            # Milk package endpoints
│       ├── magazines.py        # Magazine endpoints
│       ├── subscriptions.py    # Subscription management
│       └── payments.py         # Payment processing
├── frontend/
│   ├── pages/
│   │   ├── login.html         # User login page
│   │   ├── register.html      # User registration page
│   │   └── dashboard.html     # Main dashboard
│   ├── js/
│   │   ├── auth.js            # Authentication logic
│   │   └── dashboard.js       # Dashboard functionality
│   └── css/
│       └── style.css          # Responsive styling
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite/PostgreSQL**: Database (configurable)
- **Pydantic**: Data validation
- **Stripe API**: Payment processing
- **Bcrypt**: Password hashing
- **Python-Jose**: JWT authentication

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design with Flexbox & Grid
- **JavaScript**: Interactive functionality
- **Stripe.js**: Payment gateway integration

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/DailyEaze.git
   cd DailyEaze
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**:
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```
   
   Then edit `.env` with your Stripe keys:
   ```
   STRIPE_SECRET_KEY=sk_test_your_key
   STRIPE_PUBLIC_KEY=pk_test_your_key
   ```

5. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/user/{user_id}` - Get user details

### Newspapers
- `GET /api/newspapers/` - Get all newspapers
- `GET /api/newspapers/{newspaper_id}` - Get specific newspaper
- `GET /api/newspapers/language/{language}` - Filter by language
- `GET /api/newspapers/genre/{genre}` - Filter by genre

### Milk Packages
- `GET /api/milk/` - Get all milk packages
- `GET /api/milk/{package_id}` - Get specific package

### Magazines
- `GET /api/magazines/` - Get all magazines
- `GET /api/magazines/complementary/{language}` - Get complementary magazines

### Subscriptions
- `GET /api/subscriptions/{user_id}` - Get user subscriptions
- `POST /api/subscriptions/{subscription_id}/pause` - Pause subscription
- `POST /api/subscriptions/{subscription_id}/resume` - Resume subscription
- `GET /api/subscriptions/calendar/{user_id}` - Get delivery calendar

### Payments
- `POST /api/payments/create-payment-intent` - Create Stripe payment intent
- `POST /api/payments/confirm-payment/{payment_id}` - Confirm payment
- `GET /api/payments/history/{user_id}` - Get payment history

## API Documentation

Once the server is running, visit:
- **Swagger UI** (Interactive): http://localhost:8000/docs
- **ReDoc** (API Reference): http://localhost:8000/redoc

## Frontend Pages

### Login Page (`/static/pages/login.html`)
- User email and password login
- Link to registration page
- Secure authentication

### Registration Page (`/static/pages/register.html`)
- New user account creation
- Full address information collection
- Email verification
- Password validation

### Dashboard (`/static/pages/dashboard.html`)
- Active subscriptions view with status
- Delivery calendar with monthly view
- Subscription management (pause/resume)
- New subscription creation modal
- Payment processing interface

## Database Models

### User
- Email, password, name, phone, address
- City, pincode
- Admin privileges flag

### Newspaper
- Name, language, genre
- Pricing (daily, weekly, monthly)
- Active status

### Magazine
- Name, language, genre
- Complementary flag (free with newspaper)
- Price

### MilkPackage
- Name, quantity (ml)
- Pricing (daily, weekly, monthly)

### Subscription
- User reference
- Newspaper/Milk package reference
- Start/end dates
- Pause status with dates
- Frequency (daily, weekly, monthly)

### Delivery
- User and subscription reference
- Scheduled date and status
- Delivery timestamp
- Notes

### Payment
- User and subscription reference
- Amount and status
- Stripe transaction ID
- Payment method

## Usage Examples

### Create a Subscription
```javascript
const response = await fetch('http://localhost:8000/api/subscriptions/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 1,
        newspaper_id: 1,
        frequency: 'daily',
        total_cost: 150
    })
});
```

### Pause a Subscription
```javascript
const response = await fetch(
    'http://localhost:8000/api/subscriptions/1/pause?pause_days=7',
    { method: 'POST' }
);
```

### Process Payment
```javascript
const response = await fetch('http://localhost:8000/api/payments/create-payment-intent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        amount: 500,
        user_id: 1
    })
});
```

## Running Tests

```bash
pytest
```

## Configuration

### Environment Variables
```
DATABASE_URL=sqlite:///./deliveryeaze.db
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLIC_KEY=pk_test_your_key
```

### Database Setup
- **Development**: SQLite (default)
- **Production**: PostgreSQL (update `DATABASE_URL`)

## Deployment

### Development
```bash
uvicorn app.main:app --reload
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 80 --workers 4
```

### Using Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

## Features Roadmap

- [ ] Email notifications for deliveries
- [ ] SMS alerts for status updates
- [ ] Admin dashboard for managing content
- [ ] Customer support chat
- [ ] Mobile app (React Native)
- [ ] Loyalty rewards program
- [ ] Referral system
- [ ] Analytics dashboard
- [ ] Advanced subscription customization
- [ ] Multiple payment gateway support (PayPal, Razorpay)

## Security

- Passwords hashed with bcrypt
- CORS enabled for cross-origin requests
- SQL injection prevention through ORM
- Secure payment handling with Stripe
- Environment variables for sensitive data

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@dailyeaze.com or open an issue in the repository.

## Contact

- **Email**: aparna@dailyeaze.com
- **GitHub**: [@aparna](https://github.com)
- **Twitter**: [@DailyEaze](https://twitter.com)

---

**DailyEaze** - Making daily delivery management simple and efficient! 📦✨
"# DailyEase" 
