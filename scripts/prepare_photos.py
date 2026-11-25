from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
from html import escape

# Project directory
ROOT = Path(__file__).resolve().parent.parent

# Private folder for new original photographs
SOURCE = Path.home() / "Desktop" / "Astrocony_New"

ARCHIVE = Path.home() / "Desktop" / "Astrocony_Originals"

# Public gallery directory
DESTINATION = ROOT / "photography" / "images"

# Gallery HTML file
HTML_FILE = ROOT / "photography" / "index.html"

# Image configuration
MAX_SIZE = 1000
FONT_SIZE = 48
OPACITY = 85
JPEG_QUALITY = 85

WATERMARK = "\u00a9 A S T R O C O N Y"


def process_photo(source_file, output_file):

    img = ImageOps.exif_transpose(
        Image.open(source_file)
    ).convert("RGBA")

    img.thumbnail(
        (MAX_SIZE, MAX_SIZE),
        Image.Resampling.LANCZOS
    )

    watermark = Image.new(
        "RGBA", img.size, (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(watermark)

    font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        FONT_SIZE
    )

    draw.text(
        (img.width / 2, img.height / 2),
        WATERMARK,
        font=font,
        fill=(255, 255, 255, OPACITY),
        anchor="mm"
    )

    result = Image.alpha_composite(img, watermark)

    result.convert("RGB").save(
        output_file,
        quality=JPEG_QUALITY
    )

    print(f"Processed: {output_file.name}")


def find_new_photos():

    SOURCE.mkdir(parents=True, exist_ok=True)

    photos = []

    for file in sorted(SOURCE.iterdir()):

        if file.is_file() and file.suffix.lower() in [".jpg", ".jpeg"]:
            photos.append(file)

    return photos

def get_next_number():

    numbers = []

    for file in DESTINATION.iterdir():

        if file.is_file() and file.stem.startswith("photo"):

            number = file.stem[5:]

            if number.isdigit():
                numbers.append(int(number))

    return max(numbers, default=0) + 1


def update_html(filename, title, location, date, buy_url=""):

    html = HTML_FILE.read_text(encoding="utf-8")

    image_path = f"images/{filename}"

    if f'src="{image_path}"' in html:
        print(f"Already in gallery: {filename}")
        return

    new_entry = f'''
        <img
            src="{escape(image_path)}"
            alt="{escape(title)}"
            data-title="{escape(title)}"
            data-location="{escape(location)}"
            data-date="{escape(date)}"
            data-buy="{escape(buy_url)}"
        >

'''

    marker = "    </section>"

    if html.count(marker) != 1:
        raise ValueError("Gallery closing tag not found or ambiguous")

    html = html.replace(marker, new_entry + marker, 1)

    HTML_FILE.write_text(html, encoding="utf-8")

    print(f"HTML updated: {filename}")



def get_photo_info(photo):

    print(f"\nPhotograph: {photo.name}")

    title = input("Title: ").strip()
    location = input("Location: ").strip()
    date = input("Date: ").strip()
    buy_url = input("Ko-fi product URL (optional): ").strip()

    return title, location, date, buy_url



def archive_photo(photo, filename):

    ARCHIVE.mkdir(parents=True, exist_ok=True)

    archived_file = ARCHIVE / f"{Path(filename).stem}_original{photo.suffix}"

    if archived_file.exists():
        raise FileExistsError(f"Original already exists: {archived_file.name}")

    photo.rename(archived_file)

    print(f"Original archived: {archived_file.name}")



def main():

    photos = find_new_photos()

    if not photos:
        print("No new photographs found.")
        return

    next_number = get_next_number()

    print(f"New photographs: {len(photos)}")
    print(f"Next available number: {next_number}")

    for i, photo in enumerate(photos):

        filename = f"photo{next_number + i}.jpg"
        output_file = DESTINATION / filename

        title, location, date, buy_url = get_photo_info(photo)

        process_photo(photo, output_file)

        update_html(filename, title, location, date, buy_url)

        archive_photo(photo, filename)

    print(f"\nSuccessfully processed {len(photos)} photographs.")


if __name__ == "__main__":
    main()



