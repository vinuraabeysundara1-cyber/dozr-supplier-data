#!/usr/bin/env python3
"""Get daily call volume from Google Ads for the last 30 days"""

from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
from collections import defaultdict

# Google Ads configuration
CONFIG_PATH = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/Config/google-ads.yaml"
CUSTOMER_ID = "8531896842"

def main():
    print("=" * 80)
    print("GOOGLE ADS DAILY CALL VOLUME ANALYSIS")
    print("=" * 80)

    # Initialize Google Ads client
    client = GoogleAdsClient.load_from_storage(CONFIG_PATH)
    ga_service = client.get_service("GoogleAdsService")

    # Query for call conversions over last 30 days
    query = """
        SELECT
            segments.date,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.all_conversions
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
            AND campaign.status = 'ENABLED'
        ORDER BY segments.date DESC
    """

    print("\nQuerying Google Ads API...")
    print(f"Customer ID: {CUSTOMER_ID}")
    print(f"Period: Last 30 days")
    print("-" * 80)

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query)

    # Aggregate by date and conversion action
    daily_data = defaultdict(lambda: defaultdict(float))
    conversion_types = set()

    for row in response:
        date = row.segments.date
        conv_action = row.segments.conversion_action_name
        conversions = row.metrics.conversions

        daily_data[date][conv_action] += conversions
        conversion_types.add(conv_action)

    # Identify call-related conversions
    call_related = [conv for conv in conversion_types
                   if any(keyword in conv.lower()
                         for keyword in ['call', 'phone', 'caller'])]

    print("\n📞 Call-Related Conversion Actions Identified:")
    print("-" * 80)
    for conv in sorted(call_related):
        print(f"  • {conv}")

    # Calculate daily call volume
    print("\n\n📊 DAILY CALL VOLUME (Last 30 Days)")
    print("=" * 80)
    print(f"{'Date':<12} {'Total Calls':<15} {'Details'}")
    print("-" * 80)

    daily_totals = []

    for date in sorted(daily_data.keys(), reverse=True):
        total_calls = sum(daily_data[date][conv] for conv in call_related)

        # Build details string
        details = []
        for conv in call_related:
            count = daily_data[date][conv]
            if count > 0:
                # Shorten conversion action name
                short_name = conv.replace('AdWords ', '').replace('Google Ads ', '')
                if 'Phone Call' in short_name:
                    short_name = 'Phone'
                elif 'Calls from ads' in short_name or 'Click-to-Call' in short_name:
                    short_name = 'Click-to-Call'
                elif 'Qualified' in short_name:
                    short_name = 'Qualified'

                details.append(f"{short_name}: {count:.0f}")

        details_str = " | ".join(details) if details else "-"

        print(f"{date:<12} {total_calls:<15.0f} {details_str}")
        daily_totals.append(total_calls)

    # Summary statistics
    if daily_totals:
        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)

        avg_daily = sum(daily_totals) / len(daily_totals)
        max_daily = max(daily_totals)
        min_daily = min(daily_totals)
        total_calls = sum(daily_totals)

        print(f"\n  Total Calls (30 days):     {total_calls:.0f}")
        print(f"  Average Calls per Day:     {avg_daily:.1f}")
        print(f"  Maximum Calls in a Day:    {max_daily:.0f}")
        print(f"  Minimum Calls in a Day:    {min_daily:.0f}")

        # Weekly average
        if len(daily_totals) >= 7:
            last_7_avg = sum(daily_totals[:7]) / 7
            print(f"  Last 7 Days Average:       {last_7_avg:.1f}")

    # Query for all conversion types to show context
    print("\n\n📈 ALL CONVERSION TYPES (Last 30 Days)")
    print("=" * 80)

    total_by_type = defaultdict(float)
    for date_data in daily_data.values():
        for conv_type, count in date_data.items():
            total_by_type[conv_type] += count

    # Sort by volume
    sorted_types = sorted(total_by_type.items(), key=lambda x: x[1], reverse=True)

    print(f"{'Conversion Type':<50} {'Total':<10} {'Avg/Day':<10}")
    print("-" * 70)

    for conv_type, total in sorted_types:
        avg = total / len(daily_data) if daily_data else 0
        is_call = any(keyword in conv_type.lower() for keyword in ['call', 'phone', 'caller'])
        marker = "📞 " if is_call else "   "
        print(f"{marker}{conv_type:<48} {total:<10.0f} {avg:<10.1f}")

if __name__ == "__main__":
    main()
