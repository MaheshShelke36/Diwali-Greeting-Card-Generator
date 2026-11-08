
from flask import Flask, render_template, request, redirect
from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
import uuid

app = Flask(__name__)

# Folder to save generated cards
OUTPUT_FOLDER = "static/generated"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# --------------------------------
# LOAD FONTS
# --------------------------------

def get_font(size, bold=False):

    if bold:
        path = "C:/Windows/Fonts/arialbd.ttf"
    else:
        path = "C:/Windows/Fonts/arial.ttf"

    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


# --------------------------------
# DRAW DECORATIVE SPARKLE
# --------------------------------

def draw_sparkle(draw, x, y, size, color):

    draw.line(
        (x, y - size, x, y + size),
        fill=color,
        width=5
    )

    draw.line(
        (x - size, y, x + size, y),
        fill=color,
        width=5
    )

    draw.line(
        (x - size // 2, y - size // 2,
         x + size // 2, y + size // 2),
        fill=color,
        width=3
    )

    draw.line(
        (x + size // 2, y - size // 2,
         x - size // 2, y + size // 2),
        fill=color,
        width=3
    )


# --------------------------------
# DRAW DIYA
# --------------------------------

def draw_diya(draw, x, y):

    gold = (255, 205, 85)
    orange = (255, 145, 35)
    light = (255, 240, 170)

    # Flame
    draw.ellipse(
        (x - 24, y - 95, x + 24, y - 25),
        fill=orange
    )

    draw.ellipse(
        (x - 10, y - 75, x + 10, y - 25),
        fill=light
    )

    # Diya bowl
    draw.ellipse(
        (x - 65, y - 35, x + 65, y + 15),
        fill=orange,
        outline=gold,
        width=5
    )

    draw.arc(
        (x - 65, y - 35, x + 65, y + 30),
        start=0,
        end=180,
        fill=gold,
        width=5
    )


# --------------------------------
# FIT TEXT INSIDE CARD
# --------------------------------

def fit_font(draw, text, max_width, size, minimum=20):

    while size > minimum:

        font = get_font(size, bold=True)

        box = draw.textbbox(
            (0, 0),
            text,
            font=font
        )

        if box[2] - box[0] <= max_width:
            return font

        size -= 2

    return get_font(minimum, bold=True)


# --------------------------------
# WRAP MESSAGE
# --------------------------------

def wrap_message(draw, message, font, max_width):

    words = message.split()

    lines = []
    current_line = ""

    for word in words:

        test_line = (current_line + " " + word).strip()

        width = draw.textbbox(
            (0, 0),
            test_line,
            font=font
        )[2]

        if width <= max_width:

            current_line = test_line

        else:

            if current_line:
                lines.append(current_line)

            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


# --------------------------------
# GALLERY PAGE
# --------------------------------

@app.route("/gallery")
def gallery():

    cards = []

    for filename in os.listdir(OUTPUT_FOLDER):

        if filename.endswith(".png"):
            cards.append(filename)

    # Newest cards first
    cards.sort(
        key=lambda filename: os.path.getmtime(
            os.path.join(OUTPUT_FOLDER, filename)
        ),
        reverse=True
    )

    return render_template(
        "gallery.html",
        cards=cards,
        total_cards=len(cards)
    )


# --------------------------------
# DELETE CARD
# --------------------------------

@app.route("/delete/<filename>", methods=["POST"])
def delete_card(filename):

    if os.path.basename(filename) != filename:
        return "Invalid filename", 400

    if not filename.endswith(".png"):
        return "Invalid file type", 400

    file_path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    if os.path.isfile(file_path):
        os.remove(file_path)

    return redirect("/gallery")


# --------------------------------
# HOME PAGE
# --------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------
# GENERATE GREETING CARD
# --------------------------------

@app.route("/generate", methods=["POST"])
def generate():

    # Get form information

    sender = request.form.get("sender", "").strip()
    receiver = request.form.get("receiver", "").strip()
    design = request.form.get(
        "design",
        "Traditional Diwali"
    )
    message = request.form.get("message", "").strip()

    # Check required fields

    if not sender or not receiver or not message:
        return "Please fill all the fields.", 400

    # --------------------------------
    # GET CUSTOMIZATION VALUES
    # --------------------------------

    font_size = request.form.get("font_size", "32")

    text_color = request.form.get(
        "text_color",
        "#fff5dc"
    )

    background_color = request.form.get(
        "background_color",
        "#681326"
    )

    # Validate font size

    if font_size not in ["24", "32", "42"]:
        font_size = "32"

    font_size = int(font_size)

    # Convert selected colors into RGB

    try:

        text_color = ImageColor.getrgb(text_color)

        background_color = ImageColor.getrgb(
            background_color
        )

    except (ValueError, TypeError):

        return "Invalid color selected.", 400

    # --------------------------------
    # CARD DIMENSIONS
    # --------------------------------

    WIDTH = 1200
    HEIGHT = 1600

    # Golden decoration color

    gold = (255, 220, 135)

    # Greeting line color

    white = (255, 245, 225)

    # --------------------------------
    # CREATE BACKGROUND
    # --------------------------------

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        background_color
    )

    draw = ImageDraw.Draw(img)

    # --------------------------------
    # GOLDEN BORDER
    # --------------------------------

    draw.rounded_rectangle(
        (55, 55, 1145, 1545),
        radius=35,
        outline=gold,
        width=7
    )

    # --------------------------------
    # CORNER DECORATIONS
    # --------------------------------

    draw_sparkle(
        draw, 125, 125, 25, gold
    )

    draw_sparkle(
        draw, 1075, 1470, 25, gold
    )

    # --------------------------------
    # TOP DECORATIONS
    # --------------------------------

    draw_sparkle(
        draw, 400, 280, 30, gold
    )

    draw_sparkle(
        draw, 800, 280, 30, gold
    )

    draw_diya(draw, 600, 330)

    # --------------------------------
    # MAIN TITLE
    # --------------------------------

    title = "HAPPY DIWALI"

    title_font = fit_font(
        draw,
        title,
        950,
        100
    )

    draw.text(
        (600, 480),
        title,
        fill=text_color,
        font=title_font,
        anchor="mm"
    )

    # --------------------------------
    # DECORATIVE DIVIDER
    # --------------------------------

    draw.line(
        (230, 600, 500, 600),
        fill=gold,
        width=4
    )

    draw.line(
        (700, 600, 970, 600),
        fill=gold,
        width=4
    )

    draw_sparkle(
        draw, 600, 600, 17, gold
    )

    # --------------------------------
    # GREETING TEXT
    # --------------------------------

    wish_font = get_font(36)

    draw.text(
        (600, 680),
        "Wishing you happiness and prosperity",
        fill=white,
        font=wish_font,
        anchor="mm"
    )

    # --------------------------------
    # RECEIVER NAME
    # --------------------------------

    receiver_text = "Dear " + receiver

    receiver_font = fit_font(
        draw,
        receiver_text,
        950,
        font_size + 5
    )

    draw.text(
        (600, 850),
        receiver_text,
        fill=text_color,
        font=receiver_font,
        anchor="mm"
    )

    # --------------------------------
    # MESSAGE
    # --------------------------------

    message_font = get_font(font_size)

    lines = wrap_message(
        draw,
        message,
        message_font,
        900
    )

    # Reduce font size for long messages

    while len(lines) > 5 and message_font.size > 25:

        message_font = get_font(
            message_font.size - 3
        )

        lines = wrap_message(
            draw,
            message,
            message_font,
            900
        )

    # Draw message

    line_height = message_font.size + 20

    total_height = len(lines) * line_height

    start_y = 1030 - (total_height // 2)

    for line in lines:

        draw.text(
            (600, start_y),
            line,
            fill=text_color,
            font=message_font,
            anchor="mm"
        )

        start_y += line_height

    # --------------------------------
    # BOTTOM DIYAS
    # --------------------------------

    draw_diya(draw, 400, 1300)

    draw_diya(draw, 800, 1300)

    draw_sparkle(
        draw, 600, 1280, 30, gold
    )

    # --------------------------------
    # SENDER NAME
    # --------------------------------

    sender_text = "With love, " + sender

    sender_font = fit_font(
        draw,
        sender_text,
        950,
        max(20, font_size - 4)
    )

    draw.text(
        (600, 1430),
        sender_text,
        fill=text_color,
        font=sender_font,
        anchor="mm"
    )

    # --------------------------------
    # SAVE PNG IMAGE
    # --------------------------------

    filename = (
        "diwali_" + uuid.uuid4().hex[:8] + ".png"
    )

    file_path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    # Save with 300 DPI metadata

    img.save(
        file_path,
        dpi=(300, 300)
    )

    # --------------------------------
    # SHOW GENERATED CARD
    # --------------------------------

    return render_template(
        "card.html",
        card=filename
    )


# --------------------------------
# RUN FLASK APPLICATION
# --------------------------------

if __name__ == "__main__":

    app.run(debug=True)
