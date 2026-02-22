#!/usr/bin/env python3
"""Full breakdown of yesterday's Google Ads performance - Campaign & Ad Group level"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

def main():
    client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/google-ads.yaml")
    customer_id = "8531896842"
    ga_service = client.get_service("GoogleAdsService")
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"DOZR Google Ads - Full Breakdown for {yesterday}")
    print("=" * 140)
    
    # ============ CAMPAIGN LEVEL ============
    print("\n" + "=" * 60)
    print("CAMPAIGN LEVEL PERFORMANCE")
    print("=" * 60)
    
    campaign_query = f"""
        SELECT
            campaign.name,
            campaign.status,
            campaign.bidding_strategy_type,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.all_conversions
        FROM campaign
        WHERE campaign.status = 'ENABLED'
            AND segments.date = '{yesterday}'
        ORDER BY metrics.cost_micros DESC
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=campaign_query)
        
        print(f"\n{'Campaign':<42} {'Strategy':<18} {'Impr':<7} {'Clicks':<6} {'CTR':<6} {'CPC':<7} {'Spend':<10} {'Conv':<6} {'Value':<10}")
        print("-" * 140)
        
        total_impr = 0
        total_clicks = 0
        total_cost = 0
        total_conv = 0
        total_value = 0
        
        campaign_data = []
        for row in response:
            cost = row.metrics.cost_micros / 1_000_000
            cpc = row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0
            ctr = row.metrics.ctr * 100 if row.metrics.ctr else 0
            
            campaign_data.append({
                'name': row.campaign.name,
                'strategy': row.campaign.bidding_strategy_type.name,
                'impr': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'ctr': ctr,
                'cpc': cpc,
                'cost': cost,
                'conv': row.metrics.conversions,
                'value': row.metrics.conversions_value
            })
            
            print(f"{row.campaign.name[:41]:<42} {row.campaign.bidding_strategy_type.name[:17]:<18} {row.metrics.impressions:<7} {row.metrics.clicks:<6} {ctr:<5.1f}% ${cpc:<6.2f} ${cost:<9.2f} {row.metrics.conversions:<6.1f} ${row.metrics.conversions_value:<9.2f}")
            
            total_impr += row.metrics.impressions
            total_clicks += row.metrics.clicks
            total_cost += cost
            total_conv += row.metrics.conversions
            total_value += row.metrics.conversions_value
        
        print("-" * 140)
        avg_ctr = (total_clicks / total_impr * 100) if total_impr else 0
        avg_cpc = (total_cost / total_clicks) if total_clicks else 0
        print(f"{'TOTAL':<42} {'':<18} {total_impr:<7} {total_clicks:<6} {avg_ctr:<5.1f}% ${avg_cpc:<6.2f} ${total_cost:<9.2f} {total_conv:<6.1f} ${total_value:<9.2f}")
        
        # ============ AD GROUP LEVEL ============
        print("\n\n" + "=" * 60)
        print("AD GROUP LEVEL PERFORMANCE")
        print("=" * 60)
        
        adgroup_query = f"""
            SELECT
                campaign.name,
                ad_group.name,
                ad_group.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM ad_group
            WHERE campaign.status = 'ENABLED'
                AND ad_group.status = 'ENABLED'
                AND segments.date = '{yesterday}'
                AND metrics.impressions > 0
            ORDER BY campaign.name, metrics.cost_micros DESC
        """
        
        response = ga_service.search(customer_id=customer_id, query=adgroup_query)
        
        print(f"\n{'Campaign':<35} {'Ad Group':<30} {'Impr':<7} {'Clicks':<6} {'Spend':<10} {'Conv':<6} {'Value':<10}")
        print("-" * 140)
        
        current_campaign = ""
        for row in response:
            cost = row.metrics.cost_micros / 1_000_000
            
            if row.campaign.name != current_campaign:
                if current_campaign:
                    print("-" * 140)
                current_campaign = row.campaign.name
            
            print(f"{row.campaign.name[:34]:<35} {row.ad_group.name[:29]:<30} {row.metrics.impressions:<7} {row.metrics.clicks:<6} ${cost:<9.2f} {row.metrics.conversions:<6.1f} ${row.metrics.conversions_value:<9.2f}")
        
        # ============ CONVERSION BREAKDOWN BY TYPE ============
        print("\n\n" + "=" * 60)
        print("CONVERSION BREAKDOWN BY TYPE")
        print("=" * 60)
        
        conv_query = f"""
            SELECT
                campaign.name,
                segments.conversion_action_name,
                segments.conversion_action_category,
                metrics.conversions,
                metrics.conversions_value,
                metrics.all_conversions
            FROM campaign
            WHERE campaign.status = 'ENABLED'
                AND segments.date = '{yesterday}'
                AND metrics.conversions > 0
            ORDER BY segments.conversion_action_name, campaign.name
        """
        
        response = ga_service.search(customer_id=customer_id, query=conv_query)
        
        # Group by conversion action
        conv_by_type = {}
        for row in response:
            action = row.segments.conversion_action_name
            if action not in conv_by_type:
                conv_by_type[action] = {'total': 0, 'value': 0, 'campaigns': []}
            conv_by_type[action]['total'] += row.metrics.conversions
            conv_by_type[action]['value'] += row.metrics.conversions_value
            conv_by_type[action]['campaigns'].append({
                'name': row.campaign.name,
                'conv': row.metrics.conversions,
                'value': row.metrics.conversions_value
            })
        
        print(f"\n{'Conversion Action':<35} {'Total':<8} {'Value':<12} {'Campaigns'}")
        print("-" * 140)
        
        for action, data in sorted(conv_by_type.items(), key=lambda x: x[1]['total'], reverse=True):
            campaigns_str = ", ".join([f"{c['name'][:20]}({c['conv']:.0f})" for c in data['campaigns'][:3]])
            if len(data['campaigns']) > 3:
                campaigns_str += f" +{len(data['campaigns'])-3} more"
            print(f"{action[:34]:<35} {data['total']:<8.1f} ${data['value']:<11.2f} {campaigns_str}")
        
        # ============ SUMMARY BY CONVERSION CATEGORY ============
        print("\n\n" + "=" * 60)
        print("SUMMARY: CALLS vs QUOTES vs CLOSED WON")
        print("=" * 60)
        
        calls = 0
        quotes = 0
        closed_won = 0
        other = 0
        
        calls_value = 0
        quotes_value = 0
        closed_won_value = 0
        
        for action, data in conv_by_type.items():
            action_lower = action.lower()
            if 'phone' in action_lower or 'call' in action_lower:
                calls += data['total']
                calls_value += data['value']
            elif 'quote' in action_lower or 'request' in action_lower:
                quotes += data['total']
                quotes_value += data['value']
            elif 'closed' in action_lower or 'won' in action_lower:
                closed_won += data['total']
                closed_won_value += data['value']
            else:
                other += data['total']
        
        print(f"\n{'Category':<25} {'Count':<10} {'Value':<15} {'Avg Value'}")
        print("-" * 60)
        print(f"{'Phone Calls':<25} {calls:<10.0f} ${calls_value:<14.2f} ${(calls_value/calls if calls else 0):.2f}")
        print(f"{'Quote Requests':<25} {quotes:<10.0f} ${quotes_value:<14.2f} ${(quotes_value/quotes if quotes else 0):.2f}")
        print(f"{'Closed Won Deals':<25} {closed_won:<10.0f} ${closed_won_value:<14.2f} ${(closed_won_value/closed_won if closed_won else 0):.2f}")
        if other:
            print(f"{'Other':<25} {other:<10.0f}")
        print("-" * 60)
        print(f"{'TOTAL':<25} {calls+quotes+closed_won+other:<10.0f} ${calls_value+quotes_value+closed_won_value:<14.2f}")
        
        # ============ KEY METRICS ============
        print("\n\n" + "=" * 60)
        print("KEY METRICS SUMMARY")
        print("=" * 60)
        
        roas = total_value / total_cost if total_cost else 0
        cost_per_call = total_cost / calls if calls else 0
        cost_per_quote = total_cost / quotes if quotes else 0
        cost_per_closed = total_cost / closed_won if closed_won else 0
        
        print(f"\nTotal Spend:           ${total_cost:,.2f}")
        print(f"Total Conversions:     {total_conv:.0f}")
        print(f"Total Conv Value:      ${total_value:,.2f}")
        print(f"ROAS:                  {roas:.2f}x")
        print(f"\nCost per Call:         ${cost_per_call:.2f}")
        print(f"Cost per Quote:        ${cost_per_quote:.2f}")
        print(f"Cost per Closed Won:   ${cost_per_closed:.2f}")
        
    except GoogleAdsException as ex:
        print(f"Google Ads API Error: {ex.failure.errors[0].message}")

if __name__ == "__main__":
    main()
