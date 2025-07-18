import json
import yaml
from urllib.parse import urlparse
import os
import shutil
from PIL import Image

DEFAULT_TEXT_VAR = "Resume"

SRC_DIR = "./Pictures"
DEST_DIR = "./assets"

PICTURE_SIZES = {
    "photo.png": (500, 500),
    "logo": (200, 200),
    "company": (200, 200),
}


def prepare_assets():
    print(f"Copying {SRC_DIR} to {DEST_DIR}...")
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
    shutil.copytree(SRC_DIR, DEST_DIR)

    for name, size in PICTURE_SIZES.items():
        path = os.path.join(DEST_DIR, name)
        if os.path.isfile(path):
            print(f"Resizing {name} to {size[0]}x{size[1]}px")
            with Image.open(path) as img:
                img.thumbnail(size)
                img.save(path)

        if os.path.isdir(path):
            for file in os.listdir(path):
                if not file.endswith(".png"):
                    print(f"File: {file} in {name}, must be a .png. Skipping...")
                    continue

                pic_path = os.path.join(path, file)
                if not os.path.isfile(pic_path):
                    print(
                        f"Element of {name} must be a file. {file} is not a file. Skipping..."
                    )
                    continue

                print(f"Resizing {name}/{file} to {size[0]}x{size[1]}px")
                with Image.open(pic_path) as img:
                    img.thumbnail(size)
                    img.save(pic_path)

    photo_path = os.path.join(DEST_DIR, "photo.png")
    if os.path.isfile(photo_path):
        print("Resizing photo.png to 500px...")
        with Image.open(photo_path) as img:
            img.thumbnail((500, 500))
            img.save(photo_path)


def clean_domain(url):
    if not url:
        return None
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    # Remove 'www.' if present
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def pre_render():
    # Convert RESUME.json to _variables.yml
    with open("RESUME.json", "r", encoding="utf-8") as json_file:
        meta_data = json.load(json_file)

    with open("_quarto-development.yml", "w", encoding="utf-8") as yaml_file:
        google_analytics = meta_data.get("google-analytics", None)
        title = meta_data.get("title", "Resume")
        custom_domain = clean_domain(meta_data.get("custom-domain", None))
        secondary_email = meta_data.get("secondary-email", None)
        description = meta_data.get("description", DEFAULT_TEXT_VAR)
        keywords = ", ".join([secondary_email, custom_domain, DEFAULT_TEXT_VAR])
        development_profile = {
            "website": {
                "site-url": custom_domain,
                "page-footer": {
                    "center": [
                        {"text": secondary_email, "href": f"mailto:{secondary_email}"},
                    ]
                },
            },
            "format": {"html": {"description": description}},
            "format": {
                "html": {
                    "output-file": "index.html",
                    "header-includes": "\n".join(
                        [f'<meta name="keywords" content="{keywords}">']
                    ),
                    "pagetitle": title,
                },
                "pdf": {"output-file": "index.pdf"},
            },
        }
        if google_analytics:
            development_profile["website"]["google-analytics"] = google_analytics
        yaml.dump(
            development_profile, yaml_file, default_flow_style=False, encoding="utf-8"
        )
    print("Created _quarto-development.yml from RESUME.json")

    # Check for custom-domain and create CNAME file if it exists
    if custom_domain:
        with open("CNAME", "w") as cname_file:
            cname_file.write(custom_domain)
        print(f"Created CNAME file with domain: {custom_domain}")


if __name__ == "__main__":
    prepare_assets()
    pre_render()
