"""
CRAVVY products config — single source of truth for SKUs, pricing, and combos.
Edit this file to update prices/descriptions across the entire site.
"""

# Core SKU data — 6 flavors, ₹50/pack (2 slices @ ₹25/slice), 15g protein
PRODUCTS = {
    'classic-peanut': {
        'slug': 'classic-peanut',
        'name': 'Classic Peanut',
        'subtitle': "the OG. you can't go wrong.",
        'tagline': 'tastes like biting into a peanut butter cloud at 3am',
        'long_desc': "The one that started it all. Pure roasted peanut, just enough sweetness, none of the chalky 'health bar' nonsense. If this is your first CRAVVY — start here.",
        'image': 'images/packs/classic-peanut-front.png',
        'image_back': 'images/packs/classic-peanut-back.png',
        'color': '#7B3FF2',
        'color_name': 'peanut',
        'text_color': '#FFE600',
        'on_color': '#FFE600',
        'protein': '15g',
        'fiber': '4g',
        'price': 50,
        'slices_per_pack': 2,
        'price_per_slice': 25,
        'flavor_notes': ['Roasted Peanut', 'Honey', 'Sea Salt'],
        'best_for': 'first-timers, OGs, peanut butter loyalists',
        'rating': 4.9,
        'review_count': 1247,
        'badge': 'OG'
    },
    'coco-crunch': {
        'slug': 'coco-crunch',
        'name': 'Coco Crunch',
        'subtitle': 'like a beach holiday in your mouth.',
        'tagline': 'almond + coconut hits different. trust the process.',
        'long_desc': "Almond butter base with toasted coconut shavings. Light, tropical, weirdly addictive. Tastes like vacation. Not actually a vacation.",
        'image': 'images/packs/coco-crunch-front.png',
        'image_back': 'images/packs/coco-crunch-back.png',
        'color': '#00A19A',
        'color_name': 'coco',
        'text_color': '#FF3DAA',
        'on_color': '#FF3DAA',
        'protein': '15g',
        'fiber': '4g',
        'price': 50,
        'slices_per_pack': 2,
        'price_per_slice': 25,
        'flavor_notes': ['Almond', 'Coconut', 'Vanilla'],
        'best_for': 'people who like Bounty bars but want their abs back',
        'rating': 4.8,
        'review_count': 892,
        'badge': 'BEACH MODE'
    },
    'choco-fudge': {
        'slug': 'choco-fudge',
        'name': 'Choco Fudge',
        'subtitle': "chocolate cake's healthier cousin.",
        'tagline': 'hazelnut + dark chocolate. dangerous combination.',
        'long_desc': "Hazelnut butter folded with dark chocolate. Tastes illegal. Isn't. Will replace your evening dessert habit, then become it.",
        'image': 'images/packs/choco-fudge-front.png',
        'image_back': 'images/packs/choco-fudge-back.png',
        'color': '#FF6A1A',
        'color_name': 'choco',
        'text_color': '#FFFFFF',
        'on_color': '#FFFFFF',
        'protein': '15g',
        'fiber': '4g',
        'price': 50,
        'slices_per_pack': 2,
        'price_per_slice': 25,
        'flavor_notes': ['Hazelnut', 'Dark Chocolate', 'Cocoa'],
        'best_for': 'chocoholics in denial about being chocoholics',
        'rating': 4.9,
        'review_count': 1654,
        'badge': 'FAN FAVE'
    },
    'salted-caramel': {
        'slug': 'salted-caramel',
        'name': 'Salted Caramel',
        'subtitle': 'sweet meets salty meets obsessed.',
        'tagline': "you'll think about this one between meals.",
        'long_desc': "Peanut butter with date-caramel ribbons and a hit of pink salt. Sweet enough to satisfy, salty enough to make you take a second bite immediately.",
        'image': 'images/packs/salted-caramel-front.png',
        'image_back': 'images/packs/salted-caramel-back.png',
        'color': '#EC2C8A',
        'color_name': 'caramel',
        'text_color': '#FFE600',
        'on_color': '#FFE600',
        'protein': '15g',
        'fiber': '4g',
        'price': 50,
        'slices_per_pack': 2,
        'price_per_slice': 25,
        'flavor_notes': ['Peanut', 'Date Caramel', 'Pink Salt'],
        'best_for': 'people whose love language is dessert',
        'rating': 4.8,
        'review_count': 1103,
        'badge': 'SWEET TOOTH'
    },
    'cookies-cream': {
        'slug': 'cookies-cream',
        'name': 'Cookies & Cream',
        'subtitle': 'childhood, but make it protein.',
        'tagline': "oreo vibes. zero shame.",
        'long_desc': "Vanilla peanut butter base with crushed cookie bits throughout. Tastes like the inside of an Oreo had a glow up. We don't make the rules.",
        'image': 'images/packs/cookies-cream-front.png',
        'image_back': 'images/packs/cookies-cream-back.png',
        'color': '#1F4FE0',
        'color_name': 'cookies',
        'text_color': '#FF6A1A',
        'on_color': '#FF6A1A',
        'protein': '15g',
        'fiber': '4g',
        'price': 50,
        'slices_per_pack': 2,
        'price_per_slice': 25,
        'flavor_notes': ['Vanilla', 'Cookie Crumble', 'Cream'],
        'best_for': 'the inner kid who refuses to grow up',
        'rating': 4.7,
        'review_count': 743,
        'badge': 'NOSTALGIA'
    },
    'pista-crunch': {
        'slug': 'pista-crunch',
        'name': 'Pista Crunch',
        'subtitle': "the snack that thinks it's fancy.",
        'tagline': 'pistachio butter for people with refined chaos.',
        'long_desc': "Real pistachio butter with bits of crushed pista throughout. Sounds expensive. Is, kind of. Worth it. Tastes like kulfi without the brain freeze.",
        'image': 'images/packs/pista-crunch-front.png',
        'image_back': 'images/packs/pista-crunch-back.png',
        'color': '#B8DC2A',
        'color_name': 'pista',
        'text_color': '#7B3FF2',
        'on_color': '#7B3FF2',
        'protein': '15g',
        'fiber': '4g',
        'price': 50,
        'slices_per_pack': 2,
        'price_per_slice': 25,
        'flavor_notes': ['Pistachio', 'Cardamom', 'Honey'],
        'best_for': 'the bougie one in your friend group',
        'rating': 4.8,
        'review_count': 567,
        'badge': 'BOUGIE'
    },
}

# Combo packs — savings get better as you stack
COMBOS = {
    'starter': {
        'slug': 'starter',
        'name': 'Starter Pack',
        'tagline': 'dip your toes in.',
        'qty': 3,
        'price': 135,
        'original_price': 150,
        'price_per_pack': 45,
        'savings': 15,
        'free_shipping': False,
        'most_picked': False,
        'extras': []
    },
    'rotation': {
        'slug': 'rotation',
        'name': 'The Rotation',
        'tagline': 'the snack drawer essential.',
        'qty': 6,
        'price': 270,
        'original_price': 300,
        'price_per_pack': 45,
        'savings': 30,
        'free_shipping': True,
        'most_picked': True,
        'extras': ['FREE shipping']
    },
    'full-rave': {
        'slug': 'full-rave',
        'name': 'The Full Rave',
        'tagline': "you're committed now. respect.",
        'qty': 12,
        'price': 480,
        'original_price': 600,
        'price_per_pack': 40,
        'savings': 120,
        'free_shipping': True,
        'most_picked': False,
        'extras': ['FREE shipping', 'CRAVVY sticker sheet', 'Surprise flavor sample']
    },
}

# Free shipping threshold for à la carte orders
FREE_SHIPPING_THRESHOLD = 399
SHIPPING_FEE = 49

# Brand value props for the "Why CRAVVY" section
VALUE_PROPS = [
    {'icon': '💪', 'title': '15G PROTEIN.', 'subtitle': "Actually measured. Not 'marketing protein.'"},
    {'icon': '🌾', 'title': 'FIBER THAT FILLS.', 'subtitle': 'Isabgol inside. Sorts your gut. We said it.'},
    {'icon': '🚫', 'title': 'NOT TOO SWEET.', 'subtitle': 'Sweet enough to crave. Not enough to crash.'},
    {'icon': '📃', 'title': 'NO FAKE STUFF.', 'subtitle': "If we can't pronounce it, it ain't in there."},
]

# Fake (for now) social proof
TESTIMONIALS = [
    {'handle': '@arjun.eats', 'text': 'bro this slaps. ate 3 in one sitting NOT SORRY', 'likes': '1.2k'},
    {'handle': '@thefitfriend', 'text': 'finally a snack i can post on my story without judgement', 'likes': '847'},
    {'handle': '@nehagram', 'text': 'my 4pm sugar craving has been cured. my mom is shook.', 'likes': '2.1k'},
    {'handle': '@gymrat_kabir', 'text': 'protein bars who??', 'likes': '612'},
    {'handle': '@kavya.draws', 'text': "the pista one is GENIUS i'm crying", 'likes': '934'},
    {'handle': '@dev.runs', 'text': "didn't expect to like this. lying — ordered the combo.", 'likes': '478'},
    {'handle': '@literallymegha', 'text': "choco fudge tastes like brownie batter and I don't make the rules", 'likes': '1.8k'},
    {'handle': '@aman_writes', 'text': 'replaced my evening biscuit habit. zero regrets.', 'likes': '305'},
]


def get_product(slug):
    """Get a single product by slug."""
    return PRODUCTS.get(slug)


def get_combo(slug):
    """Get a combo by slug."""
    return COMBOS.get(slug)


def all_products():
    """Return all products as a list."""
    return list(PRODUCTS.values())


def all_combos():
    """Return all combos as a list."""
    return list(COMBOS.values())
