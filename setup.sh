#!/bin/bash

# Create necessary directories
mkdir -p certificates
mkdir -p static
mkdir -p .streamlit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create Streamlit config
cat > .streamlit/config.toml << EOF
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#2c3e50"
font = "sans serif"

[server]
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 10
EOF

# Create a stamp image if it doesn't exist
python -c "
from PIL import Image, ImageDraw, ImageFont
import os

stamp_path = 'static/stamp.png'
if not os.path.exists(stamp_path):
    width, height = 300, 120
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 0, 0, 255), width=2)
    draw.rectangle([(10, 10), (width-11, height-11)], outline=(200, 0, 0, 255), width=1)
    
    try:
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    draw.text((width/2, 30), 'MEDICAL STAMP', fill=(200, 0, 0, 255), font=font_large, anchor='mm')
    draw.text((width/2, 60), 'Authorized Signatory', fill=(150, 0, 0, 255), font=font_small, anchor='mm')
    draw.text((width/2, 85), 'Clinic Seal', fill=(150, 0, 0, 255), font=font_small, anchor='mm')
    
    image.save(stamp_path, 'PNG')
    print('Stamp image created successfully!')
else:
    print('Stamp image already exists.')
"

echo "Setup completed successfully!"
