# Social Sharing Image Setup

## Required Image

To enable proper social media previews when users share the quiz, you need to create a social sharing image:

**File Location:** `C:\Users\kinta\OneDrive\Desktop\Scn\scientist_twin\static\scientist-twin-og.jpg`

### Image Specifications

- **Dimensions:** 1200px × 630px (Facebook/Instagram standard)
- **Format:** JPG or PNG
- **File Size:** Under 1MB recommended
- **Content Suggestions:**
  - App title: "Find Your Indian Scientist Twin"
  - Tagline: "Discover which legendary Indian scientist shares your personality"
  - Visual elements: Science-themed graphics (microscope, DNA, telescope, etc.)
  - SciRio branding/logo
  - Colorful, engaging design that appeals to all ages

### Why This Matters

This image appears when users share the quiz on:
- Facebook
- Instagram (when pasting link in bio/stories)
- Twitter (as large image preview)
- LinkedIn
- WhatsApp (on some platforms)

### Design Tips

1. **Text should be readable** - Use large, bold fonts
2. **Mobile-friendly** - Image appears at different sizes
3. **Brand consistency** - Match your quiz's coral/pink color scheme
4. **Kid-friendly** - Should appeal to young users while looking professional
5. **High contrast** - Ensure text stands out from background

### Quick Creation Options

**Option 1: Design Tools**
- Canva (has pre-made 1200x630 templates)
- Figma
- Adobe Photoshop

**Option 2: Online Generators**
- Social Media Image Maker
- Pablo by Buffer
- Crello

**Option 3: Use Existing Asset**
If you have a logo or hero image, resize it to 1200x630 and add text overlay.

### Current Status

✅ Open Graph meta tags added to HTML (index_v3.html:8-26)
✅ Meta tags reference `/static/scientist-twin-og.jpg`
⏳ **ACTION NEEDED:** Create and save the image file

Once created, the quiz will display beautifully when shared on all social platforms!

### Alternative (Quick Fix)

If you want to test immediately without creating a custom image, you can temporarily use the existing company logo by updating line 13 in `templates/index_v3.html`:

```html
<!-- Change from: -->
<meta property="og:image" content="{{ url_for('static', filename='scientist-twin-og.jpg', _external=True) if config.get('SERVER_NAME') else '/static/scientist-twin-og.jpg' }}">

<!-- To: -->
<meta property="og:image" content="/static/companyimage.png">
```

This will work but won't look as professional as a purpose-designed sharing image.
