"""
Generate stunning vector SVGs for Project Logo, Favicon, and Remaining Cricket Country Avatars.
"""
import os

AVATAR_DIR = r"c:\Users\Fardin\Desktop\model\app\static\avatars"
IMG_DIR = r"c:\Users\Fardin\Desktop\model\app\static\img"
STATIC_DIR = r"c:\Users\Fardin\Desktop\model\app\static"

os.makedirs(AVATAR_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# 1. Project Logo SVG
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1329"/>
      <stop offset="50%" stop-color="#060913"/>
      <stop offset="100%" stop-color="#020408"/>
    </linearGradient>
    <linearGradient id="neonGreenCyan" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4ade80"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
    <linearGradient id="cyberPurple" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8b5cf6"/>
      <stop offset="100%" stop-color="#ec4899"/>
    </linearGradient>
    <linearGradient id="ballGrad" x1="20%" y1="20%" x2="80%" y2="80%">
      <stop offset="0%" stop-color="#ff4b5c"/>
      <stop offset="60%" stop-color="#d90429"/>
      <stop offset="100%" stop-color="#7a0010"/>
    </linearGradient>
    <linearGradient id="woodGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fcd34d"/>
      <stop offset="50%" stop-color="#d97706"/>
      <stop offset="100%" stop-color="#92400e"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    <filter id="subtleGlow">
      <feGaussianBlur stdDeviation="5" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Background Circle with Cyber Tech Ring -->
  <circle cx="250" cy="250" r="236" fill="url(#bgGrad)" stroke="url(#neonGreenCyan)" stroke-width="6" filter="url(#subtleGlow)"/>
  <circle cx="250" cy="250" r="220" fill="none" stroke="rgba(74, 222, 128, 0.25)" stroke-width="2" stroke-dasharray="14 10"/>
  <circle cx="250" cy="250" r="206" fill="none" stroke="rgba(34, 211, 238, 0.15)" stroke-width="1.5"/>

  <!-- AI Neural Grid Lines -->
  <g opacity="0.4" stroke="url(#neonGreenCyan)" stroke-width="1.5">
    <line x1="80" y1="250" x2="420" y2="250" stroke-dasharray="6 8"/>
    <line x1="250" y1="80" x2="250" y2="420" stroke-dasharray="6 8"/>
    <line x1="130" y1="130" x2="370" y2="370" stroke-dasharray="4 6"/>
    <line x1="130" y1="370" x2="370" y2="130" stroke-dasharray="4 6"/>
    <circle cx="130" cy="130" r="4" fill="#4ade80"/>
    <circle cx="370" cy="130" r="4" fill="#06b6d4"/>
    <circle cx="130" cy="370" r="4" fill="#8b5cf6"/>
    <circle cx="370" cy="370" r="4" fill="#4ade80"/>
  </g>

  <!-- Cricket Bat (Angled Backing) -->
  <g transform="rotate(-38 250 250)">
    <!-- Handle -->
    <rect x="238" y="45" width="24" height="95" rx="8" fill="#e2e8f0" stroke="#0f172a" stroke-width="2"/>
    <rect x="242" y="60" width="16" height="6" fill="#8b5cf6"/>
    <rect x="242" y="80" width="16" height="6" fill="#4ade80"/>
    <rect x="242" y="100" width="16" height="6" fill="#06b6d4"/>
    <!-- Blade -->
    <path d="M230 135 L270 135 L276 380 Q250 405 224 380 Z" fill="url(#woodGrad)" stroke="#fde68a" stroke-width="3" filter="url(#subtleGlow)"/>
    <path d="M246 145 L254 145 L254 375 L246 375 Z" fill="rgba(255,255,255,0.2)"/>
    <!-- Tech Accent on Bat Blade -->
    <path d="M240 180 L260 180 L256 310 L244 310 Z" fill="rgba(15, 23, 42, 0.45)"/>
    <circle cx="250" cy="245" r="5" fill="#4ade80"/>
  </g>

  <!-- Dynamic Cyber Cricket Ball with Glow -->
  <g transform="translate(295, 175)">
    <!-- Glowing Halo -->
    <circle cx="0" cy="0" r="62" fill="none" stroke="url(#neonGreenCyan)" stroke-width="4" filter="url(#glow)" opacity="0.8"/>
    <!-- Ball Base -->
    <circle cx="0" cy="0" r="54" fill="url(#ballGrad)" stroke="#ffa8b2" stroke-width="2"/>
    <!-- Ball Seam -->
    <path d="M-40 -35 Q 0 0 -40 35" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-dasharray="4 3"/>
    <path d="M-36 -32 Q 4 0 -36 32" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>
    <path d="M38 -36 Q 0 0 38 36" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-dasharray="4 3"/>
    <!-- Ball Highlight -->
    <ellipse cx="-18" cy="-20" rx="14" ry="8" fill="rgba(255,255,255,0.4)" transform="rotate(-30 -18 -20)"/>
    <!-- AI Data Pulse on Ball -->
    <circle cx="15" cy="15" r="5" fill="#4ade80" filter="url(#glow)"/>
    <circle cx="25" cy="-10" r="3" fill="#22d3ee" filter="url(#glow)"/>
  </g>

  <!-- Analytics Trajectory Line -->
  <path d="M 90 360 Q 200 280 300 180 T 410 110" fill="none" stroke="url(#neonGreenCyan)" stroke-width="4" stroke-linecap="round" stroke-dasharray="8 6" filter="url(#glow)"/>

  <!-- Stumps Cyber Icon (Bottom Left) -->
  <g transform="translate(105, 280) scale(0.65)">
    <rect x="0" y="0" width="6" height="110" rx="3" fill="#38bdf8"/>
    <rect x="22" y="0" width="6" height="110" rx="3" fill="#4ade80"/>
    <rect x="44" y="0" width="6" height="110" rx="3" fill="#38bdf8"/>
    <rect x="-4" y="-8" width="58" height="6" rx="3" fill="#facc15"/>
  </g>

  <!-- Pro Badge at Bottom -->
  <g transform="translate(250, 420)">
    <rect x="-75" y="-22" width="150" height="44" rx="22" fill="url(#neonGreenCyan)" filter="url(#subtleGlow)"/>
    <rect x="-72" y="-19" width="144" height="38" rx="19" fill="#060913"/>
    <text x="0" y="6" font-family="'Inter', sans-serif" font-weight="900" font-size="20" fill="url(#neonGreenCyan)" text-anchor="middle" letter-spacing="4">PRO AI</text>
  </g>
</svg>"""

# 2. Favicon SVG
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="100%" height="100%">
  <defs>
    <linearGradient id="favBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a1020"/>
      <stop offset="100%" stop-color="#020408"/>
    </linearGradient>
    <linearGradient id="favBall" x1="20%" y1="20%" x2="80%" y2="80%">
      <stop offset="0%" stop-color="#ff4b5c"/>
      <stop offset="100%" stop-color="#b91c1c"/>
    </linearGradient>
    <linearGradient id="favRing" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4ade80"/>
      <stop offset="100%" stop-color="#22d3ee"/>
    </linearGradient>
  </defs>
  <circle cx="64" cy="64" r="60" fill="url(#favBg)" stroke="url(#favRing)" stroke-width="4"/>
  <!-- Cricket Ball -->
  <circle cx="64" cy="64" r="38" fill="url(#favBall)"/>
  <!-- Seam -->
  <path d="M38 40 Q 64 64 38 88" fill="none" stroke="#ffffff" stroke-width="3" stroke-dasharray="3 2"/>
  <path d="M90 40 Q 64 64 90 88" fill="none" stroke="#ffffff" stroke-width="3" stroke-dasharray="3 2"/>
  <!-- Lightning / AI Spark -->
  <polygon points="64,22 56,56 70,54 58,94 76,50 62,52" fill="#4ade80"/>
</svg>"""

# 3. Country SVG Generator Template
def make_country_avatar(name, flag_emoji, primary_color, secondary_color, accent_color, badge_text, icon_type):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad_{badge_text}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{primary_color}"/>
      <stop offset="60%" stop-color="{secondary_color}"/>
      <stop offset="100%" stop-color="#090d16"/>
    </linearGradient>
    <linearGradient id="jerseyGrad_{badge_text}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{primary_color}"/>
      <stop offset="100%" stop-color="{secondary_color}"/>
    </linearGradient>
    <filter id="glow_{badge_text}">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Circular Outer Frame -->
  <circle cx="200" cy="200" r="190" fill="url(#bgGrad_{badge_text})" stroke="{accent_color}" stroke-width="8" filter="url(#glow_{badge_text})"/>
  <circle cx="200" cy="200" r="176" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2" stroke-dasharray="8 6"/>

  <!-- Stadium Stadium Background Silhouette -->
  <path d="M 30 260 Q 200 230 370 260 L 370 380 L 30 380 Z" fill="rgba(0,0,0,0.35)"/>
  <circle cx="200" cy="90" r="45" fill="rgba(255,255,255,0.06)"/>

  <!-- Player Torso & Jersey -->
  <path d="M 110 390 C 110 310, 145 270, 200 270 C 255 270, 290 310, 290 390 Z" fill="url(#jerseyGrad_{badge_text})" stroke="{accent_color}" stroke-width="4"/>
  <!-- Jersey Collar & Accents -->
  <polygon points="175,270 200,315 225,270 210,270 200,290 190,270" fill="{accent_color}"/>
  <path d="M 150 320 Q 200 340 250 320" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="3"/>

  <!-- Jersey Emblem / Country Text -->
  <rect x="160" y="335" width="80" height="28" rx="14" fill="rgba(0,0,0,0.5)" stroke="{accent_color}" stroke-width="1.5"/>
  <text x="200" y="354" font-family="'Inter', sans-serif" font-weight="900" font-size="14" fill="{accent_color}" text-anchor="middle" letter-spacing="1.5">{badge_text}</text>

  <!-- Player Neck -->
  <rect x="182" y="215" width="36" height="60" rx="10" fill="#e2a87c"/>

  <!-- Player Head -->
  <ellipse cx="200" cy="180" rx="46" ry="54" fill="#f1b98d"/>

  <!-- Beard / Hair Style -->
  <path d="M 156 160 C 152 220, 170 240, 200 240 C 230 240, 248 220, 244 160 C 238 180, 230 195, 200 195 C 170 195, 162 180, 156 160 Z" fill="#2d1d14" opacity="0.85"/>
  <!-- Smile -->
  <path d="M 188 208 Q 200 218 212 208" fill="none" stroke="#78350f" stroke-width="3" stroke-linecap="round"/>
  <!-- Eyes -->
  <circle cx="184" cy="175" r="4.5" fill="#1e1b18"/>
  <circle cx="216" cy="175" r="4.5" fill="#1e1b18"/>
  <circle cx="185.5" cy="173.5" r="1.5" fill="#ffffff"/>
  <circle cx="217.5" cy="173.5" r="1.5" fill="#ffffff"/>

  <!-- Cricket Helmet / Cap -->
  <path d="M 148 165 C 145 105, 255 105, 252 165 C 235 150, 165 150, 148 165 Z" fill="{primary_color}" stroke="{accent_color}" stroke-width="3"/>
  <path d="M 144 162 Q 200 148 256 162 L 268 170 Q 200 152 132 170 Z" fill="{secondary_color}"/>
  <!-- Cap Badge -->
  <circle cx="200" cy="135" r="14" fill="{accent_color}"/>
  <text x="200" y="140" font-family="'Inter', sans-serif" font-weight="900" font-size="12" fill="#0f172a" text-anchor="middle">{flag_emoji}</text>

  <!-- Cricket Bat / Ball Silhouette (Right) -->
  <g transform="translate(280, 110) rotate(25) scale(0.7)">
    <rect x="0" y="0" width="14" height="120" rx="5" fill="#fbbf24" stroke="#d97706" stroke-width="2"/>
    <circle cx="7" cy="-12" r="12" fill="#ef4444"/>
  </g>

  <!-- Top Title Badge -->
  <g transform="translate(200, 35)">
    <rect x="-85" y="-16" width="170" height="32" rx="16" fill="rgba(6,9,19,0.85)" stroke="{accent_color}" stroke-width="2"/>
    <text x="0" y="5" font-family="'Inter', sans-serif" font-weight="800" font-size="13" fill="#ffffff" text-anchor="middle">{name}</text>
  </g>
</svg>"""

COUNTRIES = [
    ("Australia", "🦘", "#f59e0b", "#047857", "#fbbf24", "AUS", "bat"),
    ("New Zealand", "🌿", "#18181b", "#27272a", "#38bdf8", "NZ", "ball"),
    ("Sri Lanka", "🦁", "#1d4ed8", "#eab308", "#fbbf24", "SL", "lion"),
    ("West Indies", "🌴", "#831843", "#d97706", "#f59e0b", "WI", "palm"),
    ("Afghanistan", "🇦🇫", "#2563eb", "#dc2626", "#22c55e", "AFG", "star"),
    ("Zimbabwe", "🇿🇼", "#dc2626", "#15803d", "#facc15", "ZIM", "bird"),
    ("Ireland", "☘️", "#15803d", "#047857", "#4ade80", "IRE", "clover"),
    ("Netherlands", "🦁", "#ea580c", "#1e40af", "#fb923c", "NED", "tulip")
]

# Write Logo & Favicon
with open(os.path.join(IMG_DIR, "logo.svg"), "w", encoding="utf-8") as f:
    f.write(LOGO_SVG)

with open(os.path.join(STATIC_DIR, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(FAVICON_SVG)

with open(os.path.join(IMG_DIR, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(FAVICON_SVG)

# Write Country SVGs
for name, emoji, p_col, s_col, acc_col, code, itype in COUNTRIES:
    filename = f"avatar_{name.lower().replace(' ', '')}.svg"
    svg_content = make_country_avatar(name, emoji, p_col, s_col, acc_col, code, itype)
    with open(os.path.join(AVATAR_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {filename}")

print("All SVGs created successfully!")
