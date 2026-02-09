
# Valentine Capsule
*Seal your love, reveal in time*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)

A romantic web application that allows users to create heartfelt messages, seal them digitally, and share them with loved ones to be revealed at a special moment.

## 🌟 Features

- **Message Creation**: Write and seal heartfelt messages with an elegant, romantic interface
- **Timed Reveal**: Messages can be set to unlock on a specific date (like Valentine's Day)
- **Unique Sharing Links**: Each message gets a unique URL for easy sharing
- **Beautiful Keepsakes**: Download messages as beautifully designed image keepsakes
- **Dark/Light Mode**: Toggle between romantic light and dark themes
- **Handwriting Font**: Option to switch to a handwritten font for a personal touch
- **Animated Backgrounds**: Floating hearts and romantic visual effects
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Background Music**: Romantic piano music that plays during message reveal
- **Word Counter**: Track your message length as you write
- **Copy Protection**: Encourages original writing by disabling paste functionality

## 🛠 Tech Stack

- **Backend**: Python 3.8+, Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Libraries**:
  - Cryptography (for message encryption)
  - Pillow (for creating keepsake images)

## 📁 Project Structure

```
valentine_capsule/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── LICENSE                 # MIT License
│
├── templates/              # HTML templates
│   ├── create.html         # Message creation page
│   ├── view.html           # Message viewing page
│   └── error.html          # error page
│
├── static/                 # Static assets
│   ├── style.css           # Application styles
│   ├── heart.js            # Heart animation script
│   ├── romantic-piano-128.mp3  # Background music
│   ├── paper-texture.jpg   # Background texture
│   ├── favicon.ico         # Website icon
│   └── fonts/              # Custom fonts
│
└── database.db             # SQLite database

```

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tushar-Siddik/valentine-capsule.git
   cd valentine-capsule
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create necessary directories**
   ```bash
   mkdir -p static/fonts static/emojis data
   ```

5. **Add font files**
   - Download the required fonts (Playfair Display family)
   - Place them in the `static/fonts/` directory

## 🎯 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

3. **Create a message**
   - Write your heartfelt message
   - Toggle between normal and handwriting fonts
   - Watch the word counter as you type
   - Click "Seal the Letter" when ready

4. **Share your message**
   - Copy the unique link provided
   - Share it with your loved one
   - They can view it when the time comes

5. **View a message**
   - If it's before the reveal date, they'll see a countdown
   - After the reveal date, the message will display with:
     - Romantic animations
     - Background music
     - Option to download as a keepsake image

## 🎨 Customization

### Changing the Reveal Date
Edit the `VALENTINES_DATE` variable in `app.py`:
```python
VALENTINES_DATE = datetime.date(2026, 2, 14)  # Change to your desired date
```

### Customizing the Keepsake Design
Modify the `generate_image()` function in `app.py` to:
- Change colors and fonts
- Adjust decorative elements
- Modify the layout


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Credits

Created with ❤️ by [Md. Siddiqur Rahman](https://www.linkedin.com/in/siddiqurrahman1/)

## 🙏 Acknowledgments

- Google Fonts for the beautiful typography
- The Flask community for the amazing framework

## 📞 Support

If you have any questions or suggestions, please:
- Open an issue on GitHub

---

*"Seal your love, reveal in time"* 💕