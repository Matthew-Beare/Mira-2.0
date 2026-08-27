# MIRA Brand Asset Integration Specification

## Brand hierarchy

Primary product brand: **MIRA**

Expansion when useful: **Modular Intelligence & Reasoning Assistant**

Supporting technical component: **MIRROR**, described as MIRA's companion reality database.

MIRROR should not normally appear as a co-equal logo/wordmark in user-facing product chrome.

## Design-source rule

Prefer vector source for every logo/mark. The canonical source should be SVG with clean paths and no embedded raster image unless the artwork genuinely requires raster texture.

Do not make platform-specific icon files the design source. Windows ICO, Linux PNG sizes, Android launcher exports, favicons, installer graphics, and store assets should be generated from the canonical masters.

## Required master assets

### 1. Primary MIRA symbol / app mark

- Canonical: `mira-mark.svg`
- Artboard: **1024 × 1024**, square
- Background: transparent
- Keep the essential mark inside the central **800 × 800** safe area.
- Must remain recognizable at 16–32 px.
- Deliver full-color, light-background, dark-background, and monochrome variants.

Also deliver a preview PNG at **1024 × 1024**.

Uses: desktop shortcut, Windows/Linux app icon source, web favicon/app icon source, mobile icon source, tray/status variants, installer branding.

### 2. Horizontal wordmark / navigation lockup

- Canonical: `mira-wordmark-horizontal.svg`
- Artboard: **2400 × 600** (**4:1**)
- Background: transparent
- Important artwork/text should remain inside a **2200 × 440** safe area.
- Deliver light-background, dark-background, and monochrome variants.

Uses: desktop title/landing surfaces, website header, README/docs, installer header, about screens.

### 3. Square logo lockup

- Canonical: `mira-lockup-square.svg`
- Artboard: **1600 × 1600**
- Background: transparent
- May combine symbol + MIRA wordmark/tagline if the design benefits from it.
- Keep essential content inside the central **1280 × 1280** area.

Uses: splash/about pages, profile/project tiles, larger promotional surfaces.

### 4. Wide hero / app banner master

- Canonical: `mira-hero-wide.svg` plus PNG preview
- Canvas: **2560 × 1024** (**2.5:1**)
- Keep all essential logo/text content inside the centered **1600 × 800** safe zone.
- Outside the safe zone should be extendable/croppable background treatment only.
- Avoid placing critical detail within 160 px of any edge.

Uses: responsive web/app welcome screen, large desktop landing surface, documentation/release graphics.

### 5. Thin application/header banner crop

- Canonical export: **1920 × 480** (**4:1**)
- Keep essential content within the centered **1440 × 360** safe zone.
- Must still work when horizontally cropped on smaller desktop/tablet layouts.

Uses: Windows/Linux/web application header or onboarding surface where a thin banner is appropriate.

### 6. 16:9 promotional / release graphic

- Canvas: **1920 × 1080**
- Keep important content inside centered **1600 × 900**.
- This is promotional/marketing artwork, not the source of truth for logos.

Uses: release notes, GitHub/social preview, presentations, launch graphics, app showcase images.

### 7. Android adaptive-icon foreground

- Canonical: `mira-android-foreground.svg`
- Artboard: **1080 × 1080**
- Background: transparent
- Keep the essential logo inside the central **660 × 660** safe zone so adaptive masks do not mutilate it.
- Provide the background treatment separately as a solid color/gradient specification or separate vector asset.

Uses: generated Android adaptive launcher icons.

### 8. Monochrome utility mark

- Canonical: `mira-mark-mono.svg`
- Artboard: **1024 × 1024**
- Single-color vector with transparent background.
- Must remain legible at **16 px**.

Uses: system tray, status bar, notification glyph source, tiny UI controls, high-contrast modes.

## Generated platform exports

The code/build system should generate these from the canonical masters rather than requiring the designer to hand-maintain them:

### Windows
- ICO containing at least: **16, 20, 24, 32, 40, 48, 64, 128, 256 px**.
- Installer/application graphics as required by the chosen packaging system.

### Linux
- PNG app icons: **16, 24, 32, 48, 64, 128, 256, 512 px**.
- SVG retained where desktop environment/package format supports it.

### Web/PWA
- favicon: **16, 32, 48 px** generated from the master;
- PWA icons: **192 × 192** and **512 × 512**;
- maskable PWA icon: **512 × 512** derived from a safe-zone-compliant source;
- Apple-touch style icon as required by current web packaging.

### Android
- adaptive foreground/background resources generated from the Android master;
- Play/store listing icon derived at **512 × 512** when needed.

### Future iOS/macOS, if supported
- derive required platform icon sets from the same 1024 × 1024 master after platform-specific safe-zone review.

## Visual variants required

For the symbol and horizontal wordmark, retain:

1. full-color on light background;
2. full-color on dark background;
3. white/near-white monochrome;
4. black/near-black monochrome;
5. symbol-only;
6. horizontal wordmark/lockup.

Do not create dozens of independent artistic variants. Variants should be deterministic treatments of the same identity.

## Typography / font handoff

Record the font family name, weight, tracking, and any modifications used in the wordmark. Do not rely on a proprietary font file being bundled unless licensing is explicitly cleared. For the canonical logo SVG, convert custom wordmark lettering to vector outlines when appropriate so the brand does not break when the font is unavailable.

## Source-file delivery

Preferred deliverables from the branding-design workflow:

- SVG masters for every canonical vector asset;
- PNG previews at the specified master sizes;
- a short text file listing colors in HEX and, if useful, RGB/HSL;
- typography names/weights and spacing notes;
- light/dark/monochrome variants;
- no watermarks;
- no flattened screenshot mockup as the only source.

## UI integration principle

Branding assets are presentation resources. UI code must reference canonical named assets and generated derivatives rather than embedding random copied images in individual screens. This makes later brand refinement a resource replacement instead of another archaeological expedition through five clients.
