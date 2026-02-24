import csv
import os

print("=" * 120)
print("GENERATING KEYWORD CSV FILES FOR EACH CAMPAIGN")
print("=" * 120)

# Define keywords for each campaign based on the top 10 equipment analysis
campaign_keywords = {
    'Dozers': {
        'keywords': [
            # Weight-class specific
            ('large dozer rental', 'Phrase'),
            ('heavy dozer rental', 'Phrase'),
            ('d8 dozer rental', 'Phrase'),
            ('d9 dozer rental', 'Phrase'),
            ('d6 dozer rental', 'Phrase'),
            ('cat d8 rental', 'Phrase'),
            ('cat d9 rental', 'Phrase'),
            ('80000 lb dozer', 'Phrase'),
            ('100000 lb dozer', 'Phrase'),
            ('50000 lb dozer', 'Phrase'),

            # Location variants
            ('dozer rental texas', 'Phrase'),
            ('dozer rental kentucky', 'Phrase'),
            ('bulldozer rental texas', 'Phrase'),
            ('bulldozer rental kentucky', 'Phrase'),
            ('dozer rental near me', 'Phrase'),
            ('bulldozer rental near me', 'Phrase'),

            # Intent variants
            ('dozer for rent', 'Phrase'),
            ('bulldozer for rent', 'Phrase'),
            ('rent a dozer', 'Phrase'),
            ('rent a bulldozer', 'Phrase'),
            ('dozer hire', 'Phrase'),
            ('bulldozer hire', 'Phrase'),

            # Use case
            ('land clearing dozer', 'Phrase'),
            ('construction dozer rental', 'Phrase'),
            ('grading dozer rental', 'Phrase'),
            ('site prep dozer', 'Phrase'),
            ('demolition dozer rental', 'Phrase'),
            ('farm dozer rental', 'Phrase'),

            # Core category terms
            ('dozer rental', 'Phrase'),
            ('bulldozer rental', 'Phrase'),
            ('rent dozer', 'Phrase'),
            ('rent bulldozer', 'Phrase'),
        ],
        'negatives': [
            '-canada',
            '-canadian',
            '-jobs',
            '-hiring',
            '-career',
            '-employment',
            '-parts',
            '-for sale',
            '-buy',
            '-purchase',
            '-toy',
            '-model',
            '-miniature',
            '-blade only',
            '-attachments only',
            '-training',
            '-operator',
            '-certification',
            '-swamp dozer',
            '-forestry dozer',
            '-used equipment',
            '-equipment sales',
        ]
    },

    'Forklift': {
        'keywords': [
            # Type-specific
            ('warehouse forklift rental', 'Phrase'),
            ('indoor forklift rental', 'Phrase'),
            ('electric forklift rental', 'Phrase'),
            ('pneumatic tire forklift', 'Phrase'),
            ('cushion tire forklift', 'Phrase'),
            ('outdoor forklift rental', 'Phrase'),
            ('rough terrain forklift', 'Phrase'),

            # Capacity-based
            ('35000 lb forklift', 'Phrase'),
            ('35k forklift rental', 'Phrase'),
            ('20000 lb forklift', 'Phrase'),
            ('20k forklift rental', 'Phrase'),
            ('15000 lb forklift', 'Phrase'),
            ('15k forklift rental', 'Phrase'),
            ('large forklift rental', 'Phrase'),
            ('small forklift rental', 'Phrase'),

            # Location variants
            ('forklift rental kansas', 'Phrase'),
            ('forklift rental utah', 'Phrase'),
            ('forklift rental indiana', 'Phrase'),
            ('forklift rental near me', 'Phrase'),

            # Intent variants
            ('forklift for rent', 'Phrase'),
            ('rent a forklift', 'Phrase'),
            ('forklift hire', 'Phrase'),
            ('rent forklift', 'Phrase'),

            # Use case
            ('construction forklift rental', 'Phrase'),
            ('industrial forklift rental', 'Phrase'),

            # Core terms
            ('forklift rental', 'Phrase'),
        ],
        'negatives': [
            '-canada',
            '-jobs',
            '-training',
            '-certification',
            '-operator',
            '-parts',
            '-for sale',
            '-buy forklift',
            '-used forklift',
            '-toy',
            '-pallet jack',
            '-hand truck',
            '-hand pallet',
            '-manual',
            '-attachments only',
        ]
    },

    'Telehandler': {
        'keywords': [
            # Variants/synonyms
            ('telehandler rental', 'Phrase'),
            ('lull rental', 'Phrase'),
            ('reach forklift rental', 'Phrase'),
            ('zoom boom rental', 'Phrase'),
            ('telescopic handler rental', 'Phrase'),
            ('telehandler forklift rental', 'Phrase'),

            # Capacity-based
            ('14000 lb telehandler', 'Phrase'),
            ('14k telehandler rental', 'Phrase'),
            ('15000 lb telehandler', 'Phrase'),
            ('15k telehandler rental', 'Phrase'),
            ('10000 lb telehandler', 'Phrase'),

            # Height-based
            ('44 ft reach forklift', 'Phrase'),
            ('56 ft telehandler', 'Phrase'),
            ('high reach forklift', 'Phrase'),
            ('tall telehandler rental', 'Phrase'),

            # Location variants
            ('telehandler rental texas', 'Phrase'),
            ('telehandler rental kansas', 'Phrase'),
            ('telehandler rental near me', 'Phrase'),

            # Intent variants
            ('telehandler for rent', 'Phrase'),
            ('rent telehandler', 'Phrase'),
            ('telehandler hire', 'Phrase'),
            ('rent a telehandler', 'Phrase'),

            # Use case
            ('construction telehandler rental', 'Phrase'),
        ],
        'negatives': [
            '-canada',
            '-jobs',
            '-operator',
            '-parts',
            '-for sale',
            '-training',
            '-certification',
            '-forklift attachments',
            '-attachments only',
            '-toy',
        ]
    },

    'Loader': {
        'keywords': [
            # Type-specific
            ('wheel loader rental', 'Phrase'),
            ('front end loader rental', 'Phrase'),
            ('payloader rental', 'Phrase'),
            ('skid steer rental', 'Phrase'),
            ('compact loader rental', 'Phrase'),
            ('track loader rental', 'Phrase'),
            ('compact track loader', 'Phrase'),

            # Brand terms (generic)
            ('bobcat rental', 'Phrase'),
            ('skid loader rental', 'Phrase'),

            # Location variants
            ('loader rental near me', 'Phrase'),
            ('skid steer rental near me', 'Phrase'),
            ('wheel loader rental texas', 'Phrase'),

            # Intent variants
            ('loader for rent', 'Phrase'),
            ('rent wheel loader', 'Phrase'),
            ('rent skid steer', 'Phrase'),

            # Use case
            ('construction loader rental', 'Phrase'),
            ('farm loader rental', 'Phrase'),

            # Core terms
            ('loader rental', 'Phrase'),
        ],
        'negatives': [
            '-canada',
            '-jobs',
            '-operator',
            '-attachments only',
            '-bucket only',
            '-parts',
            '-for sale',
            '-training',
            '-certification',
        ]
    },

    'Scissor-Lift': {
        'keywords': [
            # Type-specific
            ('scissor lift rental', 'Phrase'),
            ('rough terrain scissor lift', 'Phrase'),
            ('electric scissor lift rental', 'Phrase'),
            ('narrow scissor lift', 'Phrase'),
            ('indoor scissor lift', 'Phrase'),
            ('outdoor scissor lift', 'Phrase'),

            # Height-based (category level)
            ('tall scissor lift rental', 'Phrase'),
            ('low scissor lift rental', 'Phrase'),
            ('20 ft scissor lift', 'Phrase'),
            ('25 ft scissor lift', 'Phrase'),
            ('30 ft scissor lift', 'Phrase'),

            # Location variants
            ('scissor lift rental near me', 'Phrase'),

            # Intent variants
            ('scissor lift for rent', 'Phrase'),
            ('rent scissor lift', 'Phrase'),
            ('scissor lift hire', 'Phrase'),

            # Core terms
            ('scissor lift rental', 'Phrase'),
        ],
        'negatives': [
            '-canada',
            '-jobs',
            '-training',
            '-certification',
            '-parts',
            '-for sale',
            '-boom lift',
            '-aerial lift',
            '-cherry picker',
            '-operator',
        ]
    },

    'Backhoe': {
        'keywords': [
            ('backhoe rental', 'Phrase'),
            ('backhoe rental near me', 'Phrase'),
            ('backhoe rental cost', 'Phrase'),
            ('backhoe loader rental', 'Phrase'),
            ('construction backhoe rental', 'Phrase'),
            ('rent backhoe', 'Phrase'),
            ('backhoe for rent', 'Phrase'),
            ('backhoe hire', 'Phrase'),
            ('rent a backhoe', 'Phrase'),
        ],
        'negatives': [
            '-canada',
            '-jobs',
            '-operator',
            '-parts',
            '-for sale',
            '-training',
            '-certification',
        ]
    },

    'Excavator': {
        'keywords': [
            # Note: Campaign currently paused, but keywords ready for relaunch
            ('excavator rental', 'Phrase'),
            ('mini excavator rental', 'Phrase'),
            ('compact excavator rental', 'Phrase'),
            ('large excavator rental', 'Phrase'),
            ('50 ton excavator', 'Phrase'),
            ('excavator rental near me', 'Phrase'),
            ('excavator for rent', 'Phrase'),
            ('rent excavator', 'Phrase'),
            ('rent mini excavator', 'Phrase'),
            ('small excavator rental', 'Phrase'),
        ],
        'negatives': [
            '-canada',
            '-jobs',
            '-operator',
            '-parts',
            '-for sale',
            '-training',
            '-certification',
            '-toy',
        ]
    },

    'DSA': {
        'keywords': [
            # DSA campaigns use dynamic targeting, so focus on negatives
        ],
        'negatives': [
            # Location exclusions
            '-canada',
            '-canadian',
            '-toronto',
            '-vancouver',
            '-montreal',
            '-quebec',
            '-alberta',
            '-ontario',
            '-british columbia',

            # Equipment exclusions
            '-trailer',
            '-truck rental',
            '-car rental',
            '-suv rental',
            '-motorcycle',
            '-van rental',

            # Jobs/employment
            '-jobs',
            '-hiring',
            '-employment',
            '-career',
            '-resume',
            '-apply',

            # Parts/sales
            '-parts',
            '-for sale',
            '-buy',
            '-purchase equipment',
            '-used equipment',
            '-equipment sales',

            # Irrelevant
            '-toy',
            '-model',
            '-miniature',
            '-rc',
            '-remote control',
            '-video game',
            '-game',

            # International
            '-uk',
            '-europe',
            '-asia',
            '-australia',
            '-mexico',

            # Training/services
            '-training',
            '-certification',
            '-operator',
            '-license',
            '-school',
        ]
    },

    'Brand': {
        'keywords': [
            ('dozr', 'Exact'),
            ('dozr rental', 'Exact'),
            ('dozr.com', 'Exact'),
            ('dozr equipment', 'Phrase'),
            ('dozr equipment rental', 'Phrase'),
        ],
        'negatives': [
            # Competitor protection
            '-united rentals',
            '-sunbelt',
            '-herc',
            '-home depot',
            '-lowes',
            '-cat rental',
            '-caterpillar rental store',
            '-sunbelt rentals',
            '-united rentals near me',
        ]
    }
}

# Create output directory
output_dir = 'keyword_csvs'
os.makedirs(output_dir, exist_ok=True)

print(f"\n📁 Creating CSV files in: {output_dir}/")
print("-" * 120)

# Generate CSV for each campaign
for campaign_name, data in campaign_keywords.items():
    filename = f"{output_dir}/{campaign_name.lower().replace(' ', '_')}_keywords.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(['Keyword', 'Match Type', 'Type'])

        # Write positive keywords
        for keyword, match_type in data['keywords']:
            writer.writerow([keyword, match_type, 'Positive'])

        # Write negative keywords
        for neg_keyword in data['negatives']:
            writer.writerow([neg_keyword, 'Negative', 'Negative'])

    positive_count = len(data['keywords'])
    negative_count = len(data['negatives'])

    print(f"✅ {campaign_name:.<30} {positive_count} keywords, {negative_count} negatives → {filename}")

# Create a master CSV with all keywords
print("\n" + "-" * 120)
print("📊 Creating master CSV with all keywords...")

master_filename = f"{output_dir}/master_all_keywords.csv"
with open(master_filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Campaign', 'Keyword', 'Match Type', 'Type'])

    for campaign_name, data in campaign_keywords.items():
        # Positive keywords
        for keyword, match_type in data['keywords']:
            writer.writerow([campaign_name, keyword, match_type, 'Positive'])

        # Negative keywords
        for neg_keyword in data['negatives']:
            writer.writerow([campaign_name, neg_keyword, 'Negative', 'Negative'])

print(f"✅ Master file created: {master_filename}")

# Create a Google Ads Editor import format CSV
print("\n" + "-" * 120)
print("📊 Creating Google Ads Editor import format...")

for campaign_name, data in campaign_keywords.items():
    editor_filename = f"{output_dir}/{campaign_name.lower().replace(' ', '_')}_google_ads_editor_format.csv"

    with open(editor_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Google Ads Editor format header
        writer.writerow(['Campaign', 'Ad Group', 'Keyword', 'Criterion Type', 'Max CPC'])

        # Write positive keywords
        for keyword, match_type in data['keywords']:
            # Use campaign name as ad group name (you can customize this)
            ad_group = f"{campaign_name} - General"
            writer.writerow([campaign_name, ad_group, keyword, match_type.lower(), ''])

        # Write negative keywords at campaign level
        for neg_keyword in data['negatives']:
            writer.writerow([campaign_name, '', neg_keyword, 'Negative', ''])

    print(f"✅ Google Ads Editor: {campaign_name:.<25} → {editor_filename}")

# Create summary report
print("\n\n" + "=" * 120)
print("📊 KEYWORD SUMMARY REPORT")
print("=" * 120)

total_positive = 0
total_negative = 0

print(f"\n{'Campaign':<20} {'Positive Keywords':>20} {'Negative Keywords':>20} {'Total':>15}")
print("-" * 80)

for campaign_name, data in sorted(campaign_keywords.items()):
    pos_count = len(data['keywords'])
    neg_count = len(data['negatives'])
    total = pos_count + neg_count

    total_positive += pos_count
    total_negative += neg_count

    print(f"{campaign_name:<20} {pos_count:>20} {neg_count:>20} {total:>15}")

print("-" * 80)
print(f"{'TOTAL':<20} {total_positive:>20} {total_negative:>20} {total_positive + total_negative:>15}")

print("\n\n" + "=" * 120)
print("✅ ALL CSV FILES GENERATED SUCCESSFULLY")
print("=" * 120)

print(f"\n📂 Files location: {os.path.abspath(output_dir)}/")
print("\n📝 Files created:")
print("   • Individual campaign CSVs (9 files)")
print("   • Google Ads Editor format CSVs (9 files)")
print("   • Master CSV with all keywords (1 file)")
print(f"\n   Total files: {len(campaign_keywords) * 2 + 1}")

print("\n📋 Next Steps:")
print("   1. Review the CSVs in the keyword_csvs/ folder")
print("   2. Use Google Ads Editor format files for bulk upload")
print("   3. Or use individual campaign CSVs for manual upload")
print("   4. Adjust Max CPC bids as needed")
print("   5. Monitor performance for 7 days before making further changes")

print("\n" + "=" * 120)
