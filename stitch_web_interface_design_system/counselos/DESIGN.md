---
name: CounselOS
colors:
  surface: '#fff8f5'
  surface-dim: '#e0d8d5'
  surface-bright: '#fff8f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#faf2ee'
  surface-container: '#f4ece8'
  surface-container-high: '#eee7e3'
  surface-container-highest: '#e9e1dd'
  on-surface: '#1e1b19'
  on-surface-variant: '#464555'
  inverse-surface: '#33302d'
  inverse-on-surface: '#f7efeb'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#1d4ed8'
  on-secondary: '#ffffff'
  secondary-container: '#4069f2'
  on-secondary-container: '#fffbff'
  tertiary: '#005424'
  on-tertiary: '#ffffff'
  tertiary-container: '#006f31'
  on-tertiary-container: '#8df09f'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#dce1ff'
  secondary-fixed-dim: '#b7c4ff'
  on-secondary-fixed: '#001551'
  on-secondary-fixed-variant: '#0039b5'
  tertiary-fixed: '#95f8a7'
  tertiary-fixed-dim: '#79db8d'
  on-tertiary-fixed: '#00210a'
  on-tertiary-fixed-variant: '#005323'
  background: '#fff8f5'
  on-background: '#1e1b19'
  surface-variant: '#e9e1dd'
typography:
  display:
    fontFamily: Source Serif 4
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Source Serif 4
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Source Serif 4
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Source Serif 4
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  title:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22.4px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.03em
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  margin: 1.25rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system establishes an authoritative, precise, and forensic desktop environment crafted specifically for Indian litigation advocates, legal researchers, and chambers. Litigation workflows deal with high stakes, complex multi-volume evidence records, strict statutory deadlines, and confidential case briefs. The visual tone must project unyielding judicial gravitas, calm systematic order, and absolute evidentiary integrity.

The design language balances **Editorial Gravitas** with **Modern Information Utility**:
- **Dignified & Procedural:** Incorporates classical legal typographic traditions alongside utilitarian, density-optimized desktop UI patterns.
- **Evidence-Grounded & Traceable:** Every fact, excerpt, citation, and statute code has visual parity with verified records—featuring explicit source badging, strict metadata stamping, and cryptographic integrity states.
- **Clarity Over Cleverness:** Flat hierarchies, zero decorative fluff, high contrast, legible text rendering, and clear visual boundaries provide fatigue-free readability over long hours of brief preparation.
- **Offline Assurance:** Prominent status treatments signal a fully self-contained local environment ("LOCAL · SECURE"), reassuring advocates that case strategies and client privilege remain strictly within their workstation.

## Colors

The palette is anchored in warm stone neutrals rather than sterile cool slates, referencing physical parchment and high-grade legal bond paper, complemented by authoritative judicial indigo accents.

### Core Surface & Text Hierarchy
- **Canvas Base (`#FAFAF9`):** Neutral stone tint that softens full-screen glare during late-night litigation prep.
- **Surface Elevation (`#FFFFFF`):** Pure white reserved for document pages, reading panes, evidence cards, and focused modal dialogs.
- **Surface Subdued / Input Ground (`#F5F5F4`):** Recessed stone surface for sidebars, inspector panels, table headers, and form fields.
- **Structural Borders (`#E7E5E4`):** Crisp 1px boundary line used for structural panel demarcation, table grids, and divider rules.
- **Text Primary (`#1C1917`):** High-density carbon stone for judicial titles, body text, and core evidence arguments.
- **Text Secondary (`#44403C`):** Subdued charcoal for metadata keys, docket subtitles, and procedural tags.
- **Text Muted (`#78716C`):** Stone grey for timestamps, inactive states, placeholder text, and subtle grid dividers.

### Strategic Accents & Evidence Semantics
- **Authoritative Indigo (`#4F46E5` / Surface Wash `#EEF2FF`):** Primary interactive elements, selected evidence runs, focused pane outlines, and active statutory links.
- **Evidentiary Success / Admitted (`#15803D` / Tint `#F0FDF4`):** Admitted exhibits, verified authentic records, and completed procedural actions.
- **Procedural Warning / Pending (`#B45309` / Tint `#FFFBEB`):** Limitation periods nearing expiration, pending summons, or contested exhibits.
- **Evidentiary Danger / Inadmissible (`#B91C1C` / Tint `#FEF2F2`):** Flagged contradictions, rejected evidence, procedural objections, and irreversible file removals.
- **Reference / Case Law Link (`#1D4ED8` / Tint `#EFF6FF`):** Canonical cross-references to the Supreme Court, High Courts, and Indian Bare Acts.

## Typography

Typography governs the cognitive clarity of this design system. It uses a tri-font hierarchy matching desktop legal rigor:

1. **Source Serif 4:** Imparts judicial credibility and classical weight to page titles, case names (*e.g., K.S. Puttaswamy v. Union of India*), docket headers, and official memo headings.
2. **Inter:** High-legibility grotesque designed for screen utility. Applied across UI chrome, action menus, input fields, and analysis bodies at an optimal 14px or 15px with a deliberate 1.6 line-height ratio (`22.4px` and `24px`) to ensure prolonged scanning comfort without line-jumping.
3. **JetBrains Mono:** Reserved for structured evidentiary identifiers:
   - Case citations (*e.g., (2017) 10 SCC 1*)
   - Indian statutory sections (*e.g., Section 65B(4), IEA / Section 63, BSA*)
   - Document checksums, local SHA-256 hashes, timestamps, and exhibit pagination markers (*e.g., EX-P1-042*).

## Layout & Spacing

CounselOS uses a structured multi-pane desktop layout architecture tuned for Tauri window canvases (minimum 1280px width, targeting primary 1440px to 2560px displays).

### Multi-Pane Architecture
- **Primary Rail (Left, Fixed 240px–280px):** Navigation between Court Dockets, Active Briefs, Bare Acts Reference Library, and Offline Verification.
- **Evidence Explorer / Worklist (Center-Left, Variable 320px–420px):** Search index, witness statements, document chronologies, and tagged exhibits.
- **Active Scrutiny & Analysis Canvas (Center, Fluid flex):** The legal document reader, transcript comparison split, and brief argument editor.
- **Legal Intelligence & Citation Inspector (Right, Collapsible 340px–400px):** Pinpoints source evidence matches, Indian Penal Code / Bharatiya Nyaya Sanhita section matches, cross-references, and local hash validity.

### Grid Rhythm & Spacing Tokens
- Spacing follows a compact 4px baseline system (`0.25rem`, `0.5rem`, `0.75rem`, `1rem`, `1.5rem`), prioritizing dense information delivery over vacant padding.
- Panel margins default to `1.25rem` (`20px`), while panel internal gutters stay at `1rem` (`16px`) to keep related evidence clusters grouped closely.
- Panes use internal vertical scroll containers with zero layout bounce, ensuring stable reading positions when comparing two pages side by side.

## Elevation & Depth

This design system uses a tactile, low-elevation philosophy. In a professional legal desktop environment, floating shadows create visual noise and distract from text alignment. Depth is established through **tonal layering and crisp 1px borders**, supplemented by restrained micro-shadows.

### Layering Rules
- **Base Canvas (`#FAFAF9`):** The foundational substrate behind panes and structural frames.
- **Surface Elevation (`#FFFFFF`):** Reading zones, cards, and data tables exist on crisp white surfaces separated by `#E7E5E4` outlines.
- **Split-Pane Borders:** Vertical dividers are 1px solid `#E7E5E4`. When a pane is actively focused or selected for keyboard navigation, its boundary edge transitions to a 1px solid `#4F46E5`.
- **Micro-Shadow Token (Static Elements):** `0 1px 2px 0 rgba(28, 25, 23, 0.04)`. Applied to surface cards and pinned headers to lift them off the base stone wash.
- **Overlay Shadow Token (Context Menus, Flyouts, Command Palette):** `0 4px 16px -2px rgba(28, 25, 23, 0.10), 0 2px 6px -1px rgba(28, 25, 23, 0.06)` with a crisp 1px `#E7E5E4` border.
- **Offline Integrity Glow:** The persistent security status badge uses an inset hairline ring `box-shadow: inset 0 0 0 1px rgba(21, 128, 61, 0.2)` combined with a soft `#F0FDF4` fill.

## Shapes

The design system uses a strict **Soft (`roundedness: 1`)** geometry. 

- **Interactive controls, inputs, and buttons:** `4px` (`0.25rem`) radius. This conveys administrative firmness and judicial structure, steering clear of playful consumer rounds or cold 90-degree raw brutalism.
- **Evidence Cards & Panes:** `4px` (`0.25rem`) or `8px` (`0.5rem` for large modal dialogs and inspection panels).
- **Badges, Status Chips, and Citation Pills:** Fixed at `4px` (`0.25rem`) or square-cut micro-tags (`2px`). Rounded pill tags are restricted strictly to offline indicators and binary status indicators to separate them from standard clickable tags.

## Components

### Buttons & Interactive Controls
- **Primary Action (Admit Evidence, Generate Brief):** Solid `#4F46E5` background, `#FFFFFF` text, `4px` radius, 32px height (desktop compact). Hover state shifts to `#4338CA`. Active state: `#3730A3`.
- **Secondary / Outline Action:** Background `#FFFFFF`, 1px border `#E7E5E4`, text `#1C1917`. Hover state: background `#F5F5F4`, border `#D6D3D1`.
- **Destructive Action (Strike Out Record, Discard Draft):** `#B91C1C` text with `#FEF2F2` background; transitions to solid `#B91C1C` with `#FFFFFF` text on confirmation.

### Badges, Evidence Chips & Source Tags
- **Source Badges:** Monospace font (`JetBrains Mono`), 11px uppercase, 2px radius. Features an anchor glyph or page number (e.g., `[ANNEXURE P-4 · P. 112]`). Background `#F5F5F4`, border `#E7E5E4`, text `#44403C`.
- **Security & Status Pill:** Top-right desktop status pill containing a static green dot indicator, reading `LOCAL · SECURE`. Background `#F0FDF4`, border `1px solid #BBF7D0`, text `#15803D`.

### Input Fields & Search Bars
- **Case Docket Search:** Height 36px, background `#FFFFFF`, border `1px solid #E7E5E4`, text `#1C1917`. Placeholder `#78716C`. Focus state: 1px ring and border in `#4F46E5`. Includes inline hotkey indicator (`⌘K` or `Ctrl+K`) in `JetBrains Mono`.
- **Form Textareas & Legal Note Inputs:** Background `#F5F5F4`, border `1px solid #E7E5E4`, padding `8px 12px`. Transitions to `#FFFFFF` on focus for distraction-free drafting.

### Cards & Evidence Containers
- **Evidence Card:** `#FFFFFF` background, `1px solid #E7E5E4` border, `4px` radius. Divided into header (source file, exhibit number, timestamp in `JetBrains Mono`), body (verbatim excerpt in `Inter` 14px), and footer (tags, admissibility assessment, and citation markers).
- **Contradiction Flagged Card:** Left border accentuated with a 3px vertical accent stripe in `#B91C1C` (Danger/Contradiction) or `#B45309` (Pending Corroboration).

### Lists & Data Grids
- **Docket List Rows:** Compact 40px row height, alternating hover background `#F5F5F4`. Columns cleanly separated by hairline vertical borders or tabular spacing. Active row receives a subtle `#EEF2FF` tint with a 2px left border in `#4F46E5`.
- **Statute Reference Callouts:** Embedded blockquote containers styled with background `#F5F5F4`, left border `3px solid #4F46E5`, containing the Bare Act title in `Source Serif 4` and section body in `Inter` 13px.