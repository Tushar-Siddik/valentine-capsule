import os
import sqlite3
import uuid
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from cryptography.fernet import Fernet
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import math
import psycopg2
from psycopg2.extras import DictCursor # IMPORTANT: For dictionary-like results from PostgreSQL

# --- CONFIGURATION ---
app = Flask(__name__)

# Define a path for the encryption key file
KEY_FILE = "secret.key"

def load_or_generate_key():
    """Load the encryption key from a file, or generate and save a new one."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    return key

# Initialize the cipher with the persistent key
try:
    cipher = Fernet(load_or_generate_key())
except Exception as e:
    print(f"CRITICAL: Could not initialize encryption. {e}")
    cipher = None


# --- DATABASE SETUP ---
# Use Render's database URL or fall back to local SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

def get_db_connection():
    """Returns a database connection and a boolean indicating if it's PostgreSQL."""
    if DATABASE_URL.startswith("postgres"):
        conn = psycopg2.connect(DATABASE_URL)
        return conn, True
    else:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row # Make SQLite return dict-like rows
        return conn, False

def init_db():
    """Initialize the database and ensure the schema is up-to-date."""
    conn, is_postgres = get_db_connection()
    
    # Use a dictionary cursor for PostgreSQL to get dict-like results
    if is_postgres:
        cursor = conn.cursor(cursor_factory=DictCursor)
    else:
        cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                encrypted TEXT NOT NULL,
                created_date TEXT,
                unlock_date TEXT,
                sender_name TEXT,
                recipient_name TEXT,
                message_title TEXT
            )
        ''')
        
        # The rest of the schema update logic is not strictly necessary for PostgreSQL
        # if you manage schema changes with migrations, but for this app, it's fine.
        if not is_postgres:
            cursor.execute("PRAGMA table_info(messages)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            schema_updates = {
                'created_date': 'TEXT',
                'unlock_date': 'TEXT',
                'sender_name': 'TEXT',
                'recipient_name': 'TEXT',
                'message_title': 'TEXT'
            }
            
            for column, col_type in schema_updates.items():
                if column not in existing_columns:
                    print(f"Adding missing column: {column}")
                    cursor.execute(f"ALTER TABLE messages ADD COLUMN {column} {col_type}")
        
        conn.commit()
    finally:
        conn.close()

def draw_heart(draw, x, y, size, color):
    """Draws a simple, clean heart shape."""
    # Heart is defined by two circles and a polygon
    draw.ellipse([x, y, x + size, y + size], fill=color) # Left circle
    draw.ellipse([x + size, y, x + 2*size, y + size], fill=color) # Right circle
    points = [
        (x, y + size/2),
        (x + size, y + size),
        (x + 2*size, y + size/2),
        (x + size, y + size * 1.75)
    ]
    draw.polygon(points, fill=color)

# --- ROUTES ---
@app.route("/", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        if not cipher:
            return jsonify({"error": "Server configuration error. Encryption not available."}), 500
            
        message = request.form["message"]
        if not message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
        
        msg_id = str(uuid.uuid4())
        encrypted = cipher.encrypt(message.encode()).decode()
        created_date = datetime.datetime.now().isoformat()
        
        unlock_date = datetime.date.today().isoformat()
        
        try:
            conn, is_postgres = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO messages (id, encrypted, created_date, unlock_date)
                   VALUES (?, ?, ?, ?)''',
                (msg_id, encrypted, created_date, unlock_date)
            )
            conn.commit()
            conn.close()
            
            link = url_for("view", msg_id=msg_id, _external=True)
            return jsonify({"link": link})
        except Exception as e:
            app.logger.error(f"Error saving message: {e}")
            return jsonify({"error": "Failed to save message."}), 500

    return render_template("create.html")

@app.route("/v/<msg_id>")
def view(msg_id):
    try:
        conn, is_postgres = get_db_connection()
        if is_postgres:
            cursor = conn.cursor(cursor_factory=DictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT * FROM messages WHERE id=?''', (msg_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return render_template("error.html", error="Message not found 💔"), 404

        today = datetime.date.today()
        
        # `row` is now a dictionary-like object for both DB types
        unlock_date_str = row['unlock_date']
        if unlock_date_str:
            try:
                unlock_date = datetime.datetime.fromisoformat(unlock_date_str).date()
            except ValueError:
                app.logger.error(f"Invalid date format for unlock_date: {unlock_date_str}")
                unlock_date = today 
        else:
            unlock_date = today 

        unlocked = today >= unlock_date

        message = None
        if unlocked:
            if not cipher:
                 return render_template("error.html", error="Server configuration error. Cannot decrypt message."), 500
            try:
                message = cipher.decrypt(row['encrypted'].encode()).decode()
            except Exception as e:
                app.logger.error(f"Decryption failed for {msg_id}: {e}")
                return render_template("error.html", error="This message could not be opened. It may be from an older version of the app. 💔"), 500

        created_date_str = row['created_date']
        
        return render_template(
            "view.html",
            unlocked=unlocked,
            message=message,
            valentines_date=unlock_date.isoformat(),
            created_date=created_date_str
        )
        
    except Exception as e:
        app.logger.error(f"Unexpected error viewing message {msg_id}: {type(e).__name__} - {e}")
        return render_template("error.html", error="Something went wrong while loading the message. 💔"), 50

def draw_floral_corner(draw, x, y, size, color):
    """Draws a decorative floral shape for the corners."""
    petal_color = (*color, 180) # Add transparency
    center_size = size * 0.3
    # Draw petals
    for i in range(6):
        angle = i * 60
        petal_x = x + size/2 + math.cos(math.radians(angle)) * size/2 - size/4
        petal_y = y + size/2 + math.sin(math.radians(angle)) * size/2 - size/4
        draw.ellipse([petal_x, petal_y, petal_x + size/2, petal_y + size/2], fill=petal_color)
    # Draw center
    draw.ellipse([x + size/2 - center_size/2, y + size/2 - center_size/2, 
                  x + size/2 + center_size/2, y + size/2 + center_size/2], fill=color)

def draw_enhanced_flourish(draw, x, y, width, color):
    """Draws an enhanced, more dynamic flourish made of various shapes."""
    num_shapes = 12
    for i in range(num_shapes):
        progress = i / (num_shapes - 1)
        
        # Create a more dynamic path
        base_x = x + progress * width
        base_y = y
        # Use a combination of sine waves for a more organic path
        y_offset = math.sin(progress * math.pi * 2) * 8
        x_offset = math.cos(progress * math.pi * 4) * 5
        
        # Vary shape size and type
        shape_size = 3 + abs(math.sin(progress * math.pi * 3)) * 5
        
        # Alternate between circles and diamonds
        if i % 2 == 0:
            # Draw a circle
            draw.ellipse([base_x + x_offset, base_y + y_offset - shape_size/2, 
                          base_x + x_offset + shape_size, base_y + y_offset + shape_size/2], 
                          fill=color)
        else:
            # Draw a diamond (rotated square)
            half_size = shape_size / 2
            points = [
                (base_x + x_offset, base_y + y_offset - half_size),
                (base_x + x_offset + half_size, base_y + y_offset),
                (base_x + x_offset, base_y + y_offset + half_size),
                (base_x + x_offset - half_size, base_y + y_offset)
            ]
            draw.polygon(points, fill=color)

def create_gradient_background(width, height, top_color, bottom_color):
    """Creates a vertical gradient background."""
    base = Image.new('RGB', (width, height), top_color)
    top = Image.new('RGB', (width, height), bottom_color)
    mask = Image.new('L', (width, height))
    for y in range(height):
        mask.putpixel((0, y), int(255 * (1 - y / height)))
    base.paste(top, (0, 0), mask)
    return base

@app.route("/generate-image/<msg_id>")
def generate_image(msg_id):
    try:
        db = get_db_connection()
        cursor = db.execute("SELECT encrypted FROM messages WHERE id=?", (msg_id,))
        row = cursor.fetchone()

        if not row:
            return "Message not found", 404

        message = cipher.decrypt(row[0].encode()).decode()

        # --- Image Generation Logic ---
        width, height = 900, 1200
        
        # Create a romantic gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        top_color = (255, 245, 240) # #FFF5F0
        bottom_color = (255, 230, 230) # #FFE6E6
        
        for y in range(height):
            ratio = y / height
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # --- Load Fonts ---
        def load_font(path, size, default_font="arial.ttf"):
            try:
                return ImageFont.truetype(path, size)
            except IOError:
                print(f"Warning: Font not found at {path}. Using default.")
                try:
                    return ImageFont.truetype(default_font, size)
                except IOError:
                    return ImageFont.load_default()

        title_font = load_font("static/fonts/PlayfairDisplay-Bold.ttf", 60)
        message_font = load_font("static/fonts/PlayfairDisplay-Italic.ttf", 40)
        footer_font = load_font("static/fonts/PlayfairDisplay-Regular.ttf", 25)

        # --- Define Colors ---
        frame_color = (230, 176, 170) # #E6B0AA
        dark_text_color = (139, 0, 0) # #8B0000
        
        # --- Draw Decorative Frame ---
        draw.rectangle([20, 20, width-20, height-20], outline=frame_color, width=8)
        draw.rectangle([35, 35, width-35, height-35], outline=frame_color, width=3)
        
        # --- Draw NEW Floral Corners ---
        corner_size = 35
        # Top-left
        draw_floral_corner(draw, 40, 40, corner_size, frame_color)
        # Top-right
        draw_floral_corner(draw, width - 40 - corner_size, 40, corner_size, frame_color)
        # Bottom-left
        draw_floral_corner(draw, 40, height - 40 - corner_size, corner_size, frame_color)
        # Bottom-right
        draw_floral_corner(draw, width - 40 - corner_size, height - 40 - corner_size, corner_size, frame_color)

        # --- Draw Title and Side Decorators ---
        title_text = "For You, Always"
        title_y = 120
        
        draw.text((width/2, title_y), title_text, font=title_font, fill=dark_text_color, anchor="mt")

        # --- Draw ENHANCED Flourish Divider Under Title ---
        flourish_y = 190
        draw_enhanced_flourish(draw, 150, flourish_y, width - 300, frame_color)

        # --- Draw Message ---
        y_text = 280
        lines = textwrap.wrap(message, width=35)
        for line in lines:
            draw.text((width/2, y_text), line, font=message_font, fill="#330000", anchor="mt")
            y_text += 55

        # --- Draw ENHANCED Flourish Divider Above Footer ---
        flourish_y = height - 150
        draw_enhanced_flourish(draw, 150, flourish_y, width - 300, frame_color)

        # --- Draw Footer with a Heart ---
        footer_text_left = "made with"
        footer_text_right = "   Valentine Capsule"
        footer_y = height - 80
        heart_size = 20
        
        left_bbox = draw.textbbox((0,0), footer_text_left, font=footer_font)
        left_text_width = left_bbox[2] - left_bbox[0]
        draw.text((width/2 - left_text_width/2 - heart_size, footer_y), footer_text_left, font=footer_font, fill=dark_text_color, anchor="mt")
        
        draw_heart(draw, width/2 - heart_size/2, footer_y - heart_size/2, heart_size, dark_text_color)
        
        right_bbox = draw.textbbox((0,0), footer_text_right, font=footer_font)
        right_text_width = right_bbox[2] - right_bbox[0]
        draw.text((width/2 + right_text_width/2 + heart_size, footer_y), footer_text_right, font=footer_font, fill=dark_text_color, anchor="mt")
        
        # --- Serve the Image ---
        img_io = io.BytesIO()
        img.save(img_io, 'PNG', quality=95)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='valentine-keepsake.png')

    except Exception as e:
        app.logger.error(f"Error generating image: {str(e)}")
        return "Failed to generate image", 500

@app.route('/favicon.ico')
def favicon():
    # You can return a 204 No Content response
    return '', 204
    # Or, if you have a favicon.ico file in your static folder:
    # return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    

# --- STARTUP ---
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)