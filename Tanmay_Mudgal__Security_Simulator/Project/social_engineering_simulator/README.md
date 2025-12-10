# Social Engineering Attack Simulator & Training Platform

An educational web platform designed to help users recognize and respond to social engineering attacks through interactive training scenarios powered by machine learning.

## 🎯 Features

### Core Functionality
- **Interactive Attack Scenarios**: 30+ realistic scenarios covering:
  - 🎣 Phishing attacks (Easy, Medium, Hard)
  - 🍭 Baiting attacks (Easy, Medium, Hard)
  - 🎭 Pretexting attacks (Easy, Medium, Hard)
  
- **ML-Powered Personalization**: 
  - Adaptive difficulty adjustment based on user performance
  - Smart scenario recommendations targeting weakest areas
  - User vulnerability profiling and assessment
  
- **Comprehensive Analytics**:
  - Real-time performance tracking
  - Detailed vulnerability profiles
  - Progress visualization by attack type
  - Recent activity monitoring
  
- **Gamification**:
  - Achievement system with badges
  - Global leaderboard rankings
  - Score tracking and level progression
  - Performance-based rewards

### Security Features
- Secure user authentication with password hashing
- Session management
- Input validation and sanitization
- CSRF protection ready
- Rate limiting capability

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: MySQL with SQLAlchemy ORM
- **ML**: scikit-learn (KNN + K-Means clustering)
- **Security**: Werkzeug password hashing, Flask-WTF

### Frontend
- **Design**: Premium modern UI with glassmorphism
- **Fonts**: Google Fonts (Inter, Poppins)
- **Styling**: Custom CSS with gradients and animations
- **Responsive**: Mobile-first responsive design

### Machine Learning
- **Algorithm**: K-Nearest Neighbors for scenario recommendation
- **Features**: 7-dimensional user feature vector
  - Accuracy rates per scenario type (3)
  - Average response time (1)
  - Total engagement level (1)
  - Performance trend (1)
  - Consistency score (1)
- **Clustering**: K-Means for user segmentation

## 📦 Installation

### Prerequisites
- Python 3.8+
- MySQL Server 5.7+
- pip package manager

### Setup Steps

1. **Clone/Navigate to the project directory**
   ```bash
   cd social_engineering_simulator
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy `.env.example` to `.env` and update with your settings:
   ```env
   FLASK_ENV=development
   SECRET_KEY=your-secure-secret-key-here
   
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=social_engineering_db
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```
   
   This will:
   - Create the `social_engineering_db` database
   - Create all required tables
   - Populate 30+ training scenarios
   - Display initialization statistics

6. **Run the application**
   ```bash
   python run.py
   ```
   
   The application will be available at `http://localhost:5000`

## 🚀 Usage

### First Time Setup
1. Navigate to `http://localhost:5000`
2. Click "Register here" to create a new account
3. Fill in username, email, and password
4. Login with your credentials

### Training Flow
1. **Dashboard**: View your stats, achievements, and overall progress
2. **Start Training**: Get ML-recommended scenarios based on your weaknesses
3. **Complete Scenarios**: Read scenarios and identify if they're legitimate or attacks
4. **Receive Feedback**: Learn from explanations and improve
5. **Track Progress**: Monitor your improvement across different attack types

### Navigation
- **Dashboard**: Main hub with stats and quick start
- **Analytics**: Detailed vulnerability profile and performance metrics
- **Progress**: Track success rates and view recent activity
- **Leaderboard**: Compare your score with other users
- **Profile**: View achievements and account information

## 📊 Database Schema

### Tables
- **users**: User accounts and authentication
- **scenarios**: Training scenarios with difficulty levels
- **user_responses**: User answers and performance data
- **learning_progress**: Success rates by attack type
- **achievements**: Unlocked badges and milestones

## 🤖 Machine Learning Model

### Personalization Engine
The ML engine uses a 7-feature vector to personalize training:

1. **Phishing Accuracy** (0-1): Success rate on phishing scenarios
2. **Baiting Accuracy** (0-1): Success rate on baiting scenarios
3. **Pretexting Accuracy** (0-1): Success rate on pretexting scenarios
4. **Response Time** (normalized): Average time to complete scenarios
5. **Engagement Level** (normalized): Total scenarios attempted
6. **Performance Trend** (-1 to 1): Recent improvement or decline
7. **Consistency** (0-1): Stability of performance

### Adaptive Difficulty
- **Beginners** (<5 attempts): Easy scenarios
- **Low Performance** (<60% accuracy): Easy scenarios
- **Moderate Performance** (60-80% accuracy): Medium scenarios
- **High Performance** (>80% accuracy): Hard scenarios

### Recommendation Algorithm
- Uses KNN to predict which scenario type the user needs most
- Targets weakest areas to ensure balanced training
- Retrains automatically every 10 responses across all users

## 🎨 Design Philosophy

The UI follows modern web design principles:
- **Glassmorphism**: Transparent cards with backdrop blur
- **Vibrant Gradients**: Eye-catching color schemes
- **Smooth Animations**: Micro-interactions enhance UX
- **Responsive**: Works seamlessly on desktop and mobile
- **Accessible**: Clear typography and color contrasts

## 🔒 Security Considerations

- Passwords are hashed using Werkzeug's secure methods
- Session cookies are HTTP-only
- SQL injection protection via SQLAlchemy ORM
- Input validation on all forms
- Environment variables for sensitive configuration

## 📝 Future Enhancements

- Real-time multiplayer competitions
- Custom scenario creation by administrators
- Email-based phishing simulation
- Advanced ML models (Neural Networks)
- Mobile application
- Integration with corporate training programs
- Certificate generation for completed training

## 🐛 Troubleshooting

### Database Connection Issues
- Verify MySQL server is running
- Check credentials in `.env` file
- Ensure `social_engineering_db` database exists

### Module Import Errors
- Verify virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

### Port Already in Use
- Change port in `run.py`: `app.run(port=5001)`

## 📄 License

This project is created for educational purposes as part of an AI/ML academic project.

## 👥 Contributors

Created as an AI/ML course project for social engineering awareness training.

## 🙏 Acknowledgments

- Scenario content inspired by real-world social engineering cases
- UI design influenced by modern web design trends
- Security best practices from OWASP guidelines

---

**Remember**: The best defense against social engineering is awareness and skepticism. Stay vigilant! 🛡️
