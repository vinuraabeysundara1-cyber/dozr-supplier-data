#!/usr/bin/env python3
"""Pull today's Google Ads campaign performance for DOZR"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime, timedelta

def main():
    client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/google-ads.yaml")
    customer_id = "8531896842"
    
    ga_service = client.get_service("GoogleAdsService")
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Get today's and yesterday's performance for comparison
    query = f"""
        SELECT
            campaign.name,
            campaign.status,
            campaign.bidding_strategy_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.all_conversions,
            segments.date
        FROM campaign
        WHERE campaign.status = 'ENABLED'
            AND segments.date BETWEEN '{yesterday}' AND '{today}'
        ORDER BY campaign.name, segments.date
    """
    
    print(f"DOZR Google Ads Performance")
    print(f"Data for: {yesterday} to {today}")
    print("=" * 100)
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        campaigns = {}
        for row in response:
            name = row.campaign.name
            date = row.segments.date
            
            if name not in campaigns:
                campaigns[name] = {'yesterday': None, 'today': None, 'strategy': row.campaign.bidding_strategy_type.name}
            
            data = {
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost': row.metrics.cost_micros / 1_000_000,
                'conversions': row.metrics.conversions,
                'conv_value': row.metrics.conversions_value,
                'all_conv': row.metrics.all_conversions
            }
            
            if date == today:
                campaigns[name]['today'] = data
            else:
                campaigns[name]['yesterday'] = data
        
        print(f"\n{'Campaign':<45} {'Strategy':<20} {'Impr':<8} {'Clicks':<7} {'Cost':<10} {'Conv':<6} {'Value':<10}")
        print("-" * 110)
        
        total_cost = 0
        total_conv = 0
        total_value = 0
        
        for name, data in sorted(campaigns.items()):
            today_data = data.get('today') or {'impressions': 0, 'clicks': 0, 'cost': 0, 'conversions': 0, 'conv_value': 0}
            
            print(f"{name[:44]:<45} {data['strategy'][:19]:<20} {today_data['impressions']:<8} {today_data['clicks']:<7} ${today_data['cost']:<9.2f} {today_data['conversions']:<6.1f} ${today_data['conv_value']:<9.2f}")
            
            total_cost += today_data['cost']
            total_conv += today_data['conversions']
            total_value += today_data['conv_value']
        
        print("-" * 110)
        print(f"{'TOTAL TODAY':<45} {'':<20} {'':<8} {'':<7} ${total_cost:<9.2f} {total_conv:<6.1f} ${total_value:<9.2f}")
        
        # Now get conversion breakdown
        print("\n\nConversion Breakdown (Today):")
        print("=" * 80)
        
        conv_query = f"""
            SELECT
                campaign.name,
                segments.conversion_action_name,
                metrics.conversions,
                metrics.conversions_value
            FROM campaign
            WHERE campaign.status = 'ENABLED'
                AND segments.date = '{today}'
                AND metrics.conversions > 0
            ORDER BY campaign.name, metrics.conversions DESC
        """
        
        conv_response = ga_service.search(customer_id=customer_id, query=conv_query)
        
        print(f"\n{'Campaign':<40} {'Conversion Action':<25} {'Count':<8} {'Value':<10}")
        print("-" * 85)
        
        for row in conv_response:
            print(f"{row.campaign.name[:39]:<40} {row.segments.conversion_action_name[:24]:<25} {row.metrics.conversions:<8.1f} ${row.metrics.conversions_value:<9.2f}")
            
    except GoogleAdsException as ex:
        print(f"Google Ads API Error: {ex.failure.errors[0].message}")

if __name__ == "__main__":
    main()
