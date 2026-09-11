"""
YĀTRĀ AI — Final Presentation Generator
Generates reports/final/Yatra_AI_Final_Presentation.pptx
12-slide comprehensive, fully-formatted professional presentation with embedded figures and speaker notes.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "reports", "final")
os.makedirs(OUTPUT_DIR, exist_ok=True)
PPTX_PATH = os.path.join(OUTPUT_DIR, "Yatra_AI_Final_Presentation.pptx")

# Color Palette (Academic / Premium Transport Tech)
COLOR_NAVY = RGBColor(15, 30, 60)       # #0F1E3C
COLOR_DARK_SLATE = RGBColor(30, 41, 59) # #1E293B
COLOR_MUTED = RGBColor(100, 116, 139)   # #64748B
COLOR_GOLD = RGBColor(217, 119, 6)      # #D97706 (Saffron/Gold accent)
COLOR_LIGHT_BG = RGBColor(248, 250, 252)# #F8FAFC
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_TEAL = RGBColor(13, 148, 136)     # #0D9488
COLOR_CARD_BG = RGBColor(241, 245, 249) # #F1F5F9
COLOR_CARD_BORDER = RGBColor(203, 213, 225)

def add_header(slide, title_text, category_text="YĀTRĀ AI — ACADEMIC RESEARCH TRACK"):
    """Adds consistent academic header to slides."""
    # Category badge
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.3))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_GOLD
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.5), Inches(0.7))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY
    
    # Accent line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_CARD_BORDER
    line.line.color.rgb = COLOR_CARD_BORDER

def add_card(slide, left, top, width, height, title=None, fill_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    """Adds a container card with subtle background."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    
    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), Inches(0.4))
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY
    return card

def set_speaker_notes(slide, notes_text):
    """Sets speaker notes for oral defense."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank
    
    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    
    # Dark hero background
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_NAVY
    bg.line.fill.background()
    
    # Decorative accent bar
    dec = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.5), Inches(0.15), Inches(4.5))
    dec.fill.solid()
    dec.fill.fore_color.rgb = COLOR_GOLD
    dec.line.fill.background()
    
    # Title text
    tb1 = slide1.shapes.add_textbox(Inches(1.3), Inches(1.5), Inches(11.0), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "YĀTRĀ AI (यात्रा AI)"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    
    p2 = tf1.add_paragraph()
    p2.text = "A Personalized Multi-Modal Travel Recommendation Engine for India"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_GOLD
    
    p3 = tf1.add_paragraph()
    p3.text = "Discrete Choice Recovery using Grounded Public Infrastructure & Calibrated Synthetic Behaviour"
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    
    # Meta / Stats Card
    card_top = Inches(4.2)
    stat_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), card_top, Inches(10.8), Inches(1.8))
    stat_box.fill.solid()
    stat_box.fill.fore_color.rgb = RGBColor(20, 38, 75)
    stat_box.line.color.rgb = RGBColor(51, 65, 85)
    
    tb_stats = slide1.shapes.add_textbox(Inches(1.5), card_top + Inches(0.15), Inches(10.4), Inches(1.5))
    tf_stats = tb_stats.text_frame
    tf_stats.word_wrap = True
    
    stats_p1 = tf_stats.paragraphs[0]
    stats_p1.text = "RESEARCH & TECHNICAL SPECIFICATIONS"
    stats_p1.font.size = Pt(11)
    stats_p1.font.bold = True
    stats_p1.font.color.rgb = COLOR_GOLD
    
    stats_p2 = tf_stats.add_paragraph()
    stats_p2.text = "• Core Dataset: 5,000 Synthetic Travellers | 40,000 Search Sessions | 138,603 Itinerary Candidate Rows\n" \
                    "• Grounded Data: 8,400+ Railway Stations | 11,100+ Scheduled Trains | 300,000+ Flight Records | IMD Rainfall\n" \
                    "• Evaluation: Strict 70/15/15 Traveller-Level Split | Pre-Training Leakage Audit | Deterministic Seed 42\n" \
                    "• Final Champion Model: Gradient Boosting Core (GB_core) @ Decision Threshold τ* = 0.30"
    stats_p2.font.size = Pt(12)
    stats_p2.font.color.rgb = COLOR_WHITE
    
    set_speaker_notes(slide1, 
        "Welcome committee members. Today I am presenting Yātrā AI, an intelligent multi-modal travel recommendation "
        "framework specifically engineered for the Indian transit ecosystem. This project addresses the lack of personalized "
        "multi-modal trip planning in India by coupling grounded public transport infrastructure with an axiomatic Multinomial "
        "Logit discrete choice simulation across 5,000 travellers and 138,603 candidate alternatives."
    )
    
    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "The Problem: Fragmented Transit & Multi-Attribute Trade-offs")
    
    # Left Card: The Real-World Friction
    add_card(slide2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), "The Indian Transit Dilemma")
    tb = slide2.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "1. Siloed Digital Platforms:"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_NAVY
    p_desc = tf.add_paragraph()
    p_desc.text = "Indian Railways (IRCTC) and domestic commercial airlines operate on disconnected booking portals. Travellers must cross-reference schedules manually across browser tabs."
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_DARK_SLATE
    
    p = tf.add_paragraph()
    p.text = "2. Hidden Door-to-Door Friction:"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_NAVY
    p_desc = tf.add_paragraph()
    p_desc.text = "Commercial OTAs sort by flight airtime or train schedule, ignoring check-in buffers, terminal airport transfers, and intermediate railway layovers."
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_DARK_SLATE
    
    p = tf.add_paragraph()
    p.text = "3. Zero Personalization:"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_NAVY
    p_desc = tf.add_paragraph()
    p_desc.text = "Existing engines cannot evaluate multidimensional trade-offs across cost, transit speed, operational delay risk, cabin comfort, and carbon emissions."
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_DARK_SLATE

    # Right Card: The User Archetype Contrast
    add_card(slide2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Contrasting Traveller Trade-offs")
    tb = slide2.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Scenario: Delhi to Bengaluru Corridor (1,740 km)"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_GOLD
    
    p = tf.add_paragraph()
    p.text = "\n• Executive Business Traveller:"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_NAVY
    p_desc = tf.add_paragraph()
    p_desc.text = "  - Values: High punctuality, minimal door-to-door transit time.\n  - Choice: Non-stop 2.8h flight (₹5,500). Price inelastic.\n  - Priority: Time & Reliability > Cost."
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_DARK_SLATE
    
    p = tf.add_paragraph()
    p.text = "\n• Budget-Conscious Student / Family:"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_NAVY
    p_desc = tf.add_paragraph()
    p_desc.text = "  - Values: Ticket affordability, sleeping berths, zero transfer penalty.\n  - Choice: Rajdhani Express or Sleeper Rail (₹850–₹2,200, 32h).\n  - Priority: Cost & Comfort > Duration."
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_DARK_SLATE
    
    p = tf.add_paragraph()
    p.text = "\nCore Challenge: How can an ML recommendation system automatically infer and satisfy these divergent trade-offs?"
    p.font.italic = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEAL

    set_speaker_notes(slide2,
        "Here we articulate the core real-world motivation. India has immense transit supply, but consumers face a high cognitive "
        "burden. A 1,740 km trip between Delhi and Bengaluru presents wildly divergent options: a 3-hour flight for 5,500 rupees "
        "versus a 32-hour train for 850 rupees. Existing travel websites treat all users identically. Yātrā AI is built to "
        "automate multi-attribute trade-offs tailored to each traveller's latent preferences."
    )

    # =========================================================================
    # SLIDE 3: YĀTRĀ AI SOLUTION & SYSTEM ARCHITECTURE
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "The Yātrā AI Solution & Architectural Concept")
    
    col_w = Inches(3.6)
    gap = Inches(0.4)
    left_base = Inches(0.8)
    
    # Tier 1 Card
    add_card(slide3, left_base, Inches(1.6), col_w, Inches(5.2), "1. Transit Knowledge Graph")
    tb = slide3.shapes.add_textbox(left_base + Inches(0.15), Inches(2.2), col_w - Inches(0.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Multi-Modal Graph Engine\n" \
             "• Ingests 8,400+ rail stations and major metro airports.\n" \
             "• Resolves stations into unified Metropolitan Transit Zones (e.g. NDLS/NZM/DEL -> Delhi NCR).\n" \
             "• Computes realistic door-to-door duration including check-in, ground transfer, and buffer times.\n" \
             "• Integrates historical rail punctuality and IMD climate rainfall."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE
    
    # Tier 2 Card
    add_card(slide3, left_base + col_w + gap, Inches(1.6), col_w, Inches(5.2), "2. Travel DNA Layer")
    tb = slide3.shapes.add_textbox(left_base + col_w + gap + Inches(0.15), Inches(2.2), col_w - Inches(0.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Psychometric Modeling\n" \
             "• 7-Dimensional continuous preference representation:\n" \
             "  1. Cost Sensitivity\n" \
             "  2. Time Sensitivity\n" \
             "  3. Reliability Sensitivity\n" \
             "  4. Comfort Preference\n" \
             "  5. Transfer Tolerance\n" \
             "  6. Departure Time Flexibility\n" \
             "  7. Sustainability Preference\n" \
             "• Continuous coordinate space replaces rigid demographic buckets."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE

    # Tier 3 Card
    add_card(slide3, left_base + (col_w + gap)*2, Inches(1.6), col_w, Inches(5.2), "3. ML Recommendation Filter")
    tb = slide3.shapes.add_textbox(left_base + (col_w + gap)*2 + Inches(0.15), Inches(2.2), col_w - Inches(0.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Pointwise Scoring & Filter\n" \
             "• Evaluates candidate itineraries generated by routing graph.\n" \
             "• Derives relative choice-set quality scores normalized per session.\n" \
             "• Predicts alternative selection probability: P(chosen = 1 | X).\n" \
             "• Calibrated decision threshold (τ* = 0.30) balances precision and recall.\n" \
             "• Surfaces curated 'Recommended For You' carousel to user."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE

    set_speaker_notes(slide3,
        "Yātrā AI operates in three interconnected tiers: first, a multimodal knowledge graph that bridges rail and flight "
        "schedules into unified metro corridors; second, a 7-dimensional continuous psychometric vector called Travel DNA "
        "that models user sensitivity; and third, a machine learning recommendation filter that scores candidates and surfaces "
        "the best itineraries."
    )

    # =========================================================================
    # SLIDE 4: DATA ARCHITECTURE & GROUNDED SOURCES
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Data Architecture: The Hybrid Data Strategy")
    
    # Left Box: Real Data Supply
    add_card(slide4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), "Grounded Public Transit Data (100% Real)")
    tb = slide4.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Authentic Supply Infrastructure:\n" \
             "• 8,400+ Railway Stations (Ministry of Railways / OGD India):\n" \
             "  Latitude, longitude, state, zone, station codes.\n\n" \
             "• 11,100+ Train Timetables (IRCTC / CRIS):\n" \
             "  Schedules, intermediate halts, train types (Rajdhani, Shatabdi, Mail).\n\n" \
             "• 300,000+ Domestic Flight Itineraries (Kaggle / OTA records):\n" \
             "  Air carriers (IndiGo, Air India, etc.), departure windows, fare classes.\n\n" \
             "• Historical Railway Delay Statistics:\n" \
             "  Punctuality baselines aggregated by service class.\n\n" \
             "• IMD High-Resolution Climate Rainfall:\n" \
             "  Gridded monthly precipitation archives for weather disruption risk."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE
    
    # Right Box: Canonical Join Strategy
    add_card(slide4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Canonical Join & Provenance Classification")
    tb = slide4.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Strict Join Strategy (Zero Fabricated Links):\n" \
             "• Station-to-Metro Aggregation: Haversine distance clustering (threshold <= 45 km) links individual stations (NDLS, NZM) and airport (DEL) to unified metro hubs.\n" \
             "• Regional Climate Linking: Rainfall joined strictly at state/meteorological sub-division level, avoiding invalid station-level micro-joins.\n\n" \
             "Explicit Feature Provenance Tiers:\n" \
             "• OBSERVED: Station GPS, flight fares, train timetables.\n" \
             "• DERIVED: Door-to-door transit duration, IRCA distance-based rail tariffs, carbon emission estimates (DGCA/CEA factors).\n" \
             "• SIMULATION PROXIES: Punctuality baselines, cabin comfort scores.\n" \
             "• SYNTHETIC: Traveller profiles, search sessions, choice labels."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE

    set_speaker_notes(slide4,
        "It is vital to emphasize our Hybrid Data Strategy. Because commercial booking logs across Indian Railways and airlines "
        "are private, we ground all physical supply—stations, trains, flights, delay distributions, and rainfall—in real public "
        "data. We also explicitly audit feature provenance: observed, derived tariffs, simulation proxies, and synthetic demand. "
        "We never invent joins merely to force datasets together."
    )

    # =========================================================================
    # SLIDE 5: SYNTHETIC TRAVELLER / TRAVEL DNA METHODOLOGY
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Synthetic Methodology: Axiomatic Multinomial Logit")
    
    # Left Column: Formulation
    add_card(slide5, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2), "Random Utility Maximization (RUM)")
    tb = slide5.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Systematic Bilinear Utility:\n" \
             "   V_ni = Σ β_k · DNA_nk · Score_nik\n" \
             "   Captures interactive valuation (e.g. cost sensitivity × relative fare score).\n\n" \
             "2. Gumbel Error Disturbance:\n" \
             "   U_ni = V_ni + ε_ni,  where ε_ni ~ Gumbel(0, 1)\n\n" \
             "3. Multinomial Logit Closed-Form Choice:\n" \
             "   P_ni = exp(V_ni) / Σ_j exp(V_nj)\n\n" \
             "4. Discrete Choice Sampling:\n" \
             "   chosen_ni = 1 if alternative i maximizes U_ni within session.\n\n" \
             "Automated Validation Suite (5/5 Passed):\n" \
             "• Structural: 0 nulls, exact 138,603 rows.\n" \
             "• Statistical: Empirical vs theoretical mean delta <= 0.0102.\n" \
             "• Axiomatic: Choice sum = 1.0 to machine epsilon (3.33e-16).\n" \
             "• Behavioral: 6/6 sensitivity interventions passed.\n" \
             "• Reproducibility: Seed 42 bitwise identical."
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_DARK_SLATE

    # Right Column: Visual Evidence
    add_card(slide5, Inches(6.6), Inches(1.6), Inches(5.9), Inches(5.2), "Travel DNA Distributions by Persona Archetype")
    img_path = os.path.join(BASE_DIR, "docs", "images", "travel_dna_boxplots_by_persona.png")
    if os.path.exists(img_path):
        slide5.shapes.add_picture(img_path, Inches(6.8), Inches(2.2), width=Inches(5.5))

    set_speaker_notes(slide5,
        "To model demand choices, we utilize the Nobel Prize-winning Multinomial Logit formulation from econometric choice theory. "
        "Systematic utility is a bilinear product of continuous Travel DNA sensitivities and normalized candidate quality scores. "
        "Crucially, our synthetic population passed 5 rigorous validation suites, verifying structural integrity, mathematical axioms "
        "to double machine epsilon, and behavioral sensitivity."
    )

    # =========================================================================
    # SLIDE 6: EDA & BEHAVIOURAL PATTERNS
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Exploratory Data Analysis & Behavioural Patterns")
    
    # Left Column: Key Facts & Distributions
    add_card(slide6, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2), "Key Dataset Distributions")
    tb = slide6.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "A. Class Distribution (Natural Imbalance):\n" \
             "• Class 0 (Not Chosen): 98,603 (71.14%)\n" \
             "• Class 1 (Chosen):     40,000 (28.86%)\n" \
             "• Natural Imbalance Ratio: 2.465 : 1\n" \
             "• Structural origin: Exactly 1 chosen among 2 to 5 candidate alternatives per session (mean = 3.465).\n\n" \
             "B. Modal Choice Share:\n" \
             "• Heavy Rail Choices: 20,884 (52.21%)\n" \
             "• Domestic Aviation: 19,116 (47.79%)\n\n" \
             "C. Correlation Structure Clarification:\n" \
             "• Intra-persona dimensions were sampled independently (|r| <= 0.089).\n" \
             "• Moderate aggregate correlation (Cost vs Time = -0.63) arises naturally from the mixture of persona-conditioned priors."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE

    # Right Column: Correlation Heatmap or Modal Share
    add_card(slide6, Inches(6.6), Inches(1.6), Inches(5.9), Inches(5.2), "Travel DNA Correlation Matrix (Population Mixture)")
    img_path = os.path.join(BASE_DIR, "docs", "images", "travel_dna_correlation_heatmap.png")
    if os.path.exists(img_path):
        slide6.shapes.add_picture(img_path, Inches(6.8), Inches(2.2), width=Inches(5.5))

    set_speaker_notes(slide6,
        "Here we observe the exploratory data analysis. The target variable exhibits a natural 2.465 to 1 class imbalance because "
        "exactly one option is chosen among 2 to 5 candidates per session. Notice also that modal share is well-balanced: 52% rail "
        "and 48% flight. Furthermore, we clarify that while individual persona dimensions are sampled independently, aggregate "
        "correlations like negative cost-time sensitivity reflect the mixture of diverse traveller archetypes."
    )

    # =========================================================================
    # SLIDE 7: MACHINE LEARNING FORMULATION & PRE-TRAINING AUDIT
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "ML Problem Formulation & Leakage Prevention")
    
    # Left Card: Problem Formulation
    add_card(slide7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), "Supervised Binary Classification")
    tb = slide7.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "• Formulation: Predict whether an alternative is selected:\n" \
             "  y_ni = chosen_ni ∈ {0, 1}\n\n" \
             "• Grouped Partitioning (Traveller-Level Split):\n" \
             "  - TRAIN (70%):      3,500 Travellers (97,163 rows)\n" \
             "  - VALIDATION (15%):   750 Travellers (20,715 rows)\n" \
             "  - TEST (15%):         750 Travellers (20,725 rows)\n" \
             "  - Invariant: Zero traveller overlap across splits (Seed 42).\n\n" \
             "• Two Feature Configurations:\n" \
             "  - Core (Model A — 28 features): 8 Travel DNA, 7 Candidate Scores, 8 Raw Attributes, 5 Context/Climate.\n" \
             "  - Extended (Model B — 29 features): Core + persona_type.\n\n" \
             "• Dual Preprocessing Pipelines:\n" \
             "  - Linear: StandardScaler + OneHotEncoder (fitted strictly on train).\n" \
             "  - Tree: Native numericals + OrdinalEncoder."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE
    
    # Right Card: Leakage Audit
    add_card(slide7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Pre-Training Leakage Audit Matrix")
    tb = slide7.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Strict Exclusion of Post-Choice Derivatives:\n" \
             "• utility (latent driver) -> EXCLUDED (Critical Leakage)\n" \
             "• choice_probability (posterior) -> EXCLUDED (Critical Leakage)\n" \
             "• rank (post-utility order) -> EXCLUDED (Critical Leakage)\n" \
             "• session_id, traveller_id -> EXCLUDED (Identifier Leakage)\n\n" \
             "Verification of Candidate Quality Scores:\n" \
             "• cost_score, time_score, reliability_score, comfort_score, transfer_score, carbon_score, departure_fit\n\n" \
             "AUDIT CONFIRMATION:\n" \
             "All candidate scores are pre-choice attributes computed from raw itinerary attributes relative to session bounds prior to utility calculation and choice simulation. They carry zero information about whether the alternative was chosen."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE

    set_speaker_notes(slide7,
        "Before training, we conducted a rigorous leakage audit. We strictly excluded all post-choice simulation outputs like "
        "utility, rank, and choice probability. Furthermore, we verified that normalized candidate scores are strictly pre-choice "
        "attributes computed before any choice occurs. We also enforced a strict traveller-level split to prevent identity leakage."
    )

    # =========================================================================
    # SLIDE 8: MODELS COMPARED & BENCHMARKING
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Algorithmic Benchmarking: Four Model Families")
    
    # Left Card: Model Descriptions
    add_card(slide8, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2), "Model Architectures & Inductive Biases")
    tb = slide8.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Logistic Regression (L2 Regularized):\n" \
             "   - Benchmark for linear separability.\n" \
             "   - Standard scaled continuous features + One-Hot Encoding.\n\n" \
             "2. Single Decision Tree (max_depth=10, min_leaf=20):\n" \
             "   - Non-linear orthogonal splitting.\n" \
             "   - Evaluates baseline tree partitioning capacity.\n\n" \
             "3. Random Forest (100 trees, max_depth=12, min_leaf=15):\n" \
             "   - Bagging ensemble to reduce tree variance.\n" \
             "   - Evaluates random subspace feature selection.\n\n" \
             "4. Histogram Gradient Boosting (max_iter=100, lr=0.1):\n" \
             "   - Gradient boosted decision trees with regularized shrinkage.\n" \
             "   - Native support for categorical splits and missing values."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE

    # Right Card: Train vs Val vs Test Chart
    add_card(slide8, Inches(6.6), Inches(1.6), Inches(5.9), Inches(5.2), "Train vs. Val vs. Test Metric Comparison")
    img_path = os.path.join(BASE_DIR, "reports", "phase4", "train_vs_val_test_comparison.png")
    if os.path.exists(img_path):
        slide8.shapes.add_picture(img_path, Inches(6.8), Inches(2.2), width=Inches(5.5))

    set_speaker_notes(slide8,
        "We evaluated four distinct model families representing linear, single-tree, bagging, and boosting paradigms. This provided "
        "a rigorous benchmark across inductive biases, allowing us to evaluate whether non-linear interactions are necessary "
        "and how regularized boosting compares to bagging in controlling overfitting."
    )

    # =========================================================================
    # SLIDE 9: BASELINE RESULTS & KEY SCIENTIFIC FINDINGS
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Phase 4 Step 1: Baseline Findings & Insights")
    
    # Left Card: Three Core Findings
    add_card(slide9, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2), "Three Major Empirical Findings")
    tb = slide9.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Tree Ensembles Decisively Outperform Linear Models:\n" \
             "• Gradient Boosting achieved Test F1 = 0.3386 vs. 0.2300 for Logistic Regression (+47.2% relative gain).\n" \
             "• Random Forest achieved highest baseline ROC-AUC = 0.6979.\n" \
             "• Rationale: Discrete choice utility is bilinear (Sensitivity × Score); tree partitions naturally capture this interaction.\n\n" \
             "2. persona_type Adds Negligible Incremental Value:\n" \
             "• Extended Model B showed ΔROC-AUC <= 0.0005 across all algorithms.\n" \
             "• Feature importance of persona_type was only 0.81%.\n" \
             "• Rationale: Continuous Travel DNA already provides complete psychometric coordinates; persona is redundant.\n\n" \
             "3. Candidate Scores Out-Predict Raw Attributes by 2.3x:\n" \
             "• cost_score (15.4%) vs. raw_cost (7.9%).\n" \
             "• Choice depends on relative superiority within session."
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_DARK_SLATE

    # Right Card: Model Comparison Plot
    add_card(slide9, Inches(6.6), Inches(1.6), Inches(5.9), Inches(5.2), "Baseline Model Performance Comparison")
    img_path = os.path.join(BASE_DIR, "reports", "phase4", "model_comparison_plot.png")
    if os.path.exists(img_path):
        slide9.shapes.add_picture(img_path, Inches(6.8), Inches(2.2), width=Inches(5.5))

    set_speaker_notes(slide9,
        "Step 1 yielded three critical scientific insights: First, tree models substantially outperformed logistic regression "
        "because choice utility is inherently interactive. Second, adding categorical persona type provided zero incremental value, "
        "proving that continuous Travel DNA is the superior representation. Third, candidate quality scores out-predicted raw attributes "
        "by 2.3 times, proving that choice depends on relative within-session comparisons."
    )

    # =========================================================================
    # SLIDE 10: THRESHOLD OPTIMIZATION & FINAL MODEL SELECTION
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Threshold Optimization & Final Champion Selection")
    
    # Left Card: Threshold Analysis & Metrics
    add_card(slide10, Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2), "Champion: Gradient Boosting Core @ τ* = 0.30")
    tb = slide10.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Validation-Only Threshold Selection:\n" \
             "• Evaluated τ ∈ [0.20, 0.60] strictly on validation data.\n" \
             "• Peak Validation F1 = 0.5283 @ τ* = 0.30 (tie-breaker saved 1,578 FP over 0.25).\n\n" \
             "Final Test Performance (Applied Once to Test Set):\n" \
             "• Test F1 Score:   0.5116 (Surged from 0.3366, +52.0%)\n" \
             "• Test Recall:     62.65% (Surged from 23.82%, +38.8% pts)\n" \
             "• Test Precision:  43.23% (Shift from 57.37%)\n" \
             "• Test ROC-AUC:    0.6976 (Invariant)\n" \
             "• Test Accuracy:   65.37% (Shift from 72.82%)\n\n" \
             "Confusion Matrix Shift (Test Set N = 20,725):\n" \
             "• True Positives:  1,429 -> 3,759 (+2,330 / +163.0% gain)\n" \
             "• False Negatives: 4,571 -> 2,241 (-2,330 / -50.97% drop)\n" \
             "• False Positives: 1,062 -> 4,936\n" \
             "• True Negatives: 13,663 -> 9,789"
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_DARK_SLATE

    # Right Card: Final Confusion Matrix Plot
    add_card(slide10, Inches(6.6), Inches(1.6), Inches(5.9), Inches(5.2), "Confusion Matrix Shift: Default (0.50) vs. Tuned (0.30)")
    img_path = os.path.join(BASE_DIR, "reports", "phase4", "final_confusion_matrix.png")
    if os.path.exists(img_path):
        slide10.shapes.add_picture(img_path, Inches(6.8), Inches(2.2), width=Inches(5.5))

    set_speaker_notes(slide10,
        "In Step 2, we addressed the positive recall deficit. At default 0.50 threshold, models missed 76% of chosen journeys. "
        "By optimizing the threshold strictly on validation data to 0.30, Test Recall surged from 23.8% to 62.7%, and F1 jumped "
        "from 0.3366 to 0.5116. We slashed false negatives by more than half, capturing 2,330 additional preferred journeys."
    )

    # =========================================================================
    # SLIDE 11: LIMITATIONS & FUTURE WORK
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Academic Boundaries, Limitations & Future Roadmap")
    
    # Left Card: Limitations
    add_card(slide11, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), "Explicit Research Limitations")
    tb = slide11.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Synthetic Behavioral Ground Truth:\n" \
             "   Labels (chosen) reflect simulated Multinomial Logit choices, NOT real-world booking conversions.\n\n" \
             "2. Simulation Proxies:\n" \
             "   Flight punctuality and cabin comfort are calibrated proxy baselines rather than live airline operations feeds.\n\n" \
             "3. Derived Tariff Schedules:\n" \
             "   Rail fares are derived from IRCA distance formulas rather than observed transaction receipts.\n\n" \
             "4. Pointwise Independence Assumption:\n" \
             "   The binary classifier predicts alternatives independently as Bernoulli trials; it does not enforce the constraint that exactly one option is chosen per session (Σ Y_nj = 1).\n\n" \
             "5. Geographic Coverage:\n" \
             "   Focuses on 6 major Indian metropolitan corridors."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE

    # Right Card: Future Work
    add_card(slide11, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Engineering & Research Roadmap")
    tb = slide11.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Phase 6 Production Extensions:\n\n" \
             "• Session-Aware Learning-to-Rank (LTR):\n" \
             "  Transition to LightGBM Ranker / LambdaMART optimizing listwise NDCG@1 and MRR conditioned on session_id.\n\n" \
             "• Econometric Mixed Logit Modeling:\n" \
             "  Estimate unobserved preference heterogeneity and cross-elasticities between rail and air modes.\n\n" \
             "• Live Transit API Integrations:\n" \
             "  Ingest live airline GDS fares and IRCTC dynamic pricing / waitlist confirmation probability feeds.\n\n" \
             "• Online Preference Learning:\n" \
             "  Update Travel DNA sliders dynamically via contextual multi-armed bandits (LinUCB) from user clickstream telemetry."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_DARK_SLATE

    set_speaker_notes(slide11,
        "We maintain full transparency regarding limitations. The choice labels are synthetic, flight delay values are proxies, "
        "and our binary model evaluates alternatives independently rather than enforcing the one-choice-per-session constraint. "
        "This lays out an exciting roadmap: transitioning to Learning-to-Rank with LambdaMART and connecting live IRCTC and airline APIs."
    )

    # =========================================================================
    # SLIDE 12: CONCLUSION & SCIENTIFIC SIGN-OFF
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    
    # Dark hero background
    bg = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_NAVY
    bg.line.fill.background()
    
    tb = slide12.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Conclusions & Project Sign-Off"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    
    # Main summary container
    sum_box = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.2), Inches(11.3), Inches(4.5))
    sum_box.fill.solid()
    sum_box.fill.fore_color.rgb = RGBColor(20, 38, 75)
    sum_box.line.color.rgb = RGBColor(51, 65, 85)
    
    tb_sum = slide12.shapes.add_textbox(Inches(1.3), Inches(2.4), Inches(10.7), Inches(4.0))
    tf_sum = tb_sum.text_frame
    tf_sum.word_wrap = True
    
    p = tf_sum.paragraphs[0]
    p.text = "1. Feasibility Demonstrated:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_GOLD
    p_desc = tf_sum.add_paragraph()
    p_desc.text = "Yātrā AI successfully proved the feasibility of recovering multi-attribute traveller discrete choice preferences across Indian multi-modal transit networks using grounded public data and calibrated simulation."
    p_desc.font.size = Pt(12)
    p_desc.font.color.rgb = COLOR_WHITE
    
    p = tf_sum.add_paragraph()
    p.text = "\n2. Superiority of Gradient Boosting & Relative Scoring:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_GOLD
    p_desc = tf_sum.add_paragraph()
    p_desc.text = "Tree-based gradient boosting decisively outperforms linear classification by capturing bilinear utility interactions. Candidate scores relative to session bounds represent 52% of predictive importance, dominating raw attributes."
    p_desc.font.size = Pt(12)
    p_desc.font.color.rgb = COLOR_WHITE
    
    p = tf_sum.add_paragraph()
    p.text = "\n3. Optimal Operational Champion:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_GOLD
    p_desc = tf_sum.add_paragraph()
    p_desc.text = "Gradient Boosting Core (GB_core) at τ* = 0.30 achieves 0.6976 ROC-AUC and 0.5116 F1, capturing 62.65% of preferred journeys while preserving parsimony and zero persona-coupling."
    p_desc.font.size = Pt(12)
    p_desc.font.color.rgb = COLOR_WHITE
    
    p = tf_sum.add_paragraph()
    p.text = "\nClosing Scientific Boundary:"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(148, 163, 184)
    p_desc = tf_sum.add_paragraph()
    p_desc.text = "\"The results demonstrate the feasibility of recovering simulated traveller preference patterns from grounded itinerary and Travel DNA features; they should not be interpreted as empirical estimates of real-world traveller conversion behaviour.\""
    p_desc.font.italic = True
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = RGBColor(203, 213, 225)

    set_speaker_notes(slide12,
        "In conclusion, Yātrā AI establishes a principled, reproducible benchmark for multi-modal travel recommendation in India. "
        "We demonstrated that relative candidate scoring and continuous Travel DNA combined with gradient boosting provide the "
        "strongest architecture for discrete choice recovery. Thank you, and I now welcome your questions."
    )

    # Save presentation
    try:
        prs.save(PPTX_PATH)
        print(f"[+] Successfully generated PowerPoint presentation at: {PPTX_PATH}")
        return PPTX_PATH
    except PermissionError:
        alt_path = os.path.join(OUTPUT_DIR, "Yatra_AI_Final_Presentation_Updated.pptx")
        prs.save(alt_path)
        print(f"[!] Target PPTX is currently open in PowerPoint. Saved updated presentation to: {alt_path}")
        return alt_path

if __name__ == "__main__":
    build_presentation()
