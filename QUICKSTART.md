# Quick Start Guide - DailyEaze

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup Environment
```bash
copy .env.example .env
```

Edit `.env` and add your Stripe API keys:
- Get keys from: https://dashboard.stripe.com/apikeys
- Update `STRIPE_SECRET_KEY` and `STRIPE_PUBLIC_KEY`

### Step 3: Run the Server
```bash
uvicorn app.main:app --reload
```

The application will start at: **http://localhost:8000**

### Step 4: Access the Application
- **Frontend**: http://localhost:8000/static/pages/login.html
- **API Docs**: http://localhost:8000/docs
- **API Reference**: http://localhost:8000/redoc

## 📋 Default Test Data

### Sample User Credentials
- **Email**: test@example.com
- **Password**: password123

### Sample Newspapers (To be added to DB)
1. **The Times of India** (English, General)
   - Daily: ₹10, Weekly: ₹60, Monthly: ₹250

2. **Dainik Bhaskar** (Hindi, General)
   - Daily: ₹8, Weekly: ₹50, Monthly: ₹200

3. **Hindu Business Line** (English, Business)
   - Daily: ₹15, Weekly: ₹90, Monthly: ₹350

### Sample Milk Packages (To be added to DB)
1. **1L Full Cream**
   - Daily: ₹50, Weekly: ₹300, Monthly: ₹1200

2. **500ml Toned Milk**
   - Daily: ₹25, Weekly: ₹150, Monthly: ₹600

3. **1L Double Toned**
   - Daily: ₹45, Weekly: ₹270, Monthly: ₹1080

## 🗄️ Database Initialization

### Add Sample Data (Optional)
```python
from app.database.database import SessionLocal
from app.database.models import Newspaper, MilkPackage, User

db = SessionLocal()

# Add newspaper
newspaper = Newspaper(
    name="The Times of India",
    language="English",
    genre="General",
    price_daily=10,
    price_weekly=60,
    price_monthly=250,
    description="India's leading newspaper"
)
db.add(newspaper)
db.commit()
```

## 🔑 API Key Setup

### Stripe Keys
1. Go to https://dashboard.stripe.com/apikeys
2. Copy **Secret Key** and **Public Key**
3. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLIC_KEY=pk_test_...
   ```

## 📱 Frontend Pages

### Login Page
- URL: `/static/pages/login.html`
- Enter email and password
- Click "Register here" for new account

### Register Page
- URL: `/static/pages/register.html`
- Fill all required fields
- Create account and login

### Dashboard
- URL: `/static/pages/dashboard.html`
- View subscriptions
- Create new subscriptions
- Check delivery calendar
- Make payments

## 🧪 Testing Stripe Payments

### Test Card Numbers
- **Visa**: 4242 4242 4242 4242
- **Mastercard**: 5555 5555 5555 4444
- **Amex**: 3782 822463 10005

**Expiry**: Any future date (e.g., 12/25)  
**CVC**: Any 3 digits (e.g., 123)

## 📝 API Usage Examples

### 1. Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "phone": "+91 9876543210",
    "address": "123 Main St",
    "city": "New Delhi",
    "pincode": "110001"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/auth/login?email=user@example.com&password=password123"
```

### 3. Get Newspapers
```bash
curl "http://localhost:8000/api/newspapers/"
```

### 4. Get Milk Packages
```bash
curl "http://localhost:8000/api/milk/"
```

### 5. Pause Subscription
```bash
curl -X POST "http://localhost:8000/api/subscriptions/1/pause?pause_days=7"
```

### 6. Resume Subscription
```bash
curl -X POST "http://localhost:8000/api/subscriptions/1/resume"
```

## 🐛 Troubleshooting

### Python Not Found
```bash
py -m venv venv  # Create venv with Python launcher
venv\Scripts\activate
pip install -r requirements.txt
```

### Port 8000 Already in Use
```bash
uvicorn app.main:app --reload --port 8001
```

### Database Lock Error
```bash
# Delete the database file and recreate
rm deliveryeaze.db
# Run the server again to auto-create
```

### CORS Errors
- The app already has CORS enabled for all origins
- Check browser console for specific errors
- Ensure API URL is correct in JavaScript files

## 📚 Project Files Reference

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application setup |
| `app/database/database.py` | Database connection & config |
| `app/database/models.py` | SQLAlchemy models |
| `app/models/schemas.py` | Pydantic schemas |
| `app/routes/*.py` | API endpoints |
| `frontend/pages/*.html` | Web pages |
| `frontend/js/*.js` | JavaScript logic |
| `frontend/css/style.css` | Styling |

## 🎯 Next Steps

1. **Add Sample Data**: Create newspapers, magazines, and milk packages in the database
2. **Configure Stripe**: Set up real Stripe account for payments
3. **Customize Styling**: Modify `frontend/css/style.css` for branding
4. **Add Admin Panel**: Create admin dashboard for content management
5. **Deploy**: Use Docker or cloud platform (AWS, Heroku, DigitalOcean)

## ✅ Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Setup `.env` file with Stripe keys
- [ ] Run server (`uvicorn app.main:app --reload`)
- [ ] Access frontend (http://localhost:8000/static/pages/login.html)
- [ ] Register a test account
- [ ] Add sample newspapers and milk packages
- [ ] Create a subscription
- [ ] Test pause/resume functionality
- [ ] Test payment gateway (use test card: 4242 4242 4242 4242)

## 📞 Support

For issues or questions:
1. Check the main README.md
2. Review API documentation at /docs
3. Check console for JavaScript errors
4. Review server logs for backend errors

---

**Happy Coding! 🎉**
