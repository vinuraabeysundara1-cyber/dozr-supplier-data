#!/usr/bin/env python3
"""
Cross-reference Herc Rentals gap fill branches with OMS database
"""

import json
import re
from datetime import datetime

BASE_DIR = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches"

def extract_branch_number(branch_name):
    """Extract branch number from OMS branch name like 'Herc Rentals (9422) - Kansas City MO'"""
    match = re.search(r'\((\d+)\)', branch_name)
    if match:
        return match.group(1)
    return None

def main():
    # Load OMS data
    with open(f"{BASE_DIR}/herc_oms_branches.json", 'r') as f:
        oms_data = json.load(f)

    # Load gap fill data
    with open(f"{BASE_DIR}/herc_gap_fill_branches.json", 'r') as f:
        gap_fill_data = json.load(f)

    oms_branches = oms_data.get('branches', [])
    gap_fill_branches = gap_fill_data.get('branches', [])

    print("=" * 70)
    print("HERC RENTALS CROSS-REFERENCE REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    # Extract branch numbers from OMS
    oms_numbers = {}
    for b in oms_branches:
        branch_name = b.get('branch_name', '')
        num = extract_branch_number(branch_name)
        if num:
            oms_numbers[num] = b

    # Extract branch numbers from gap fill
    gap_fill_numbers = {}
    for b in gap_fill_branches:
        num = b.get('branch_number', '')
        if num:
            gap_fill_numbers[num] = b

    print(f"\nOMS Database: {len(oms_branches)} total branches ({len(oms_numbers)} with branch numbers)")
    print(f"Gap Fill Search: {len(gap_fill_branches)} branches found")

    # Find matches, new branches, and OMS-only branches
    matched = []
    new_to_add = []
    oms_only = []

    all_numbers = set(oms_numbers.keys()) | set(gap_fill_numbers.keys())

    for num in sorted(all_numbers):
        in_oms = num in oms_numbers
        in_gap_fill = num in gap_fill_numbers

        if in_oms and in_gap_fill:
            matched.append(num)
        elif in_gap_fill and not in_oms:
            new_to_add.append(num)
        elif in_oms and not in_gap_fill:
            oms_only.append(num)

    print(f"\n" + "=" * 70)
    print("CROSS-REFERENCE RESULTS")
    print("=" * 70)
    print(f"\nMatched (in both OMS and Gap Fill): {len(matched)}")
    print(f"NEW - Not in OMS (add to database): {len(new_to_add)}")
    print(f"OMS Only (not found in gap fill): {len(oms_only)}")

    # Show NEW branches to add
    print(f"\n" + "-" * 70)
    print(f"NEW BRANCHES TO ADD TO OMS ({len(new_to_add)} branches)")
    print("-" * 70)

    new_by_state = {}
    for num in new_to_add:
        b = gap_fill_numbers[num]
        state = b.get('state', 'Unknown')
        if state not in new_by_state:
            new_by_state[state] = []
        new_by_state[state].append(b)

    for state in sorted(new_by_state.keys()):
        branches = new_by_state[state]
        print(f"\n{state} ({len(branches)} new branches):")
        for b in branches:
            print(f"  {b['branch_number']} - {b.get('branch_name', '')} - {b.get('city', '')}")
            print(f"       Address: {b.get('address', '')} {b.get('zip', '')}")
            print(f"       Phone: {b.get('phone', '')} | Services: {b.get('services', '')}")

    # Show matched branches
    print(f"\n" + "-" * 70)
    print(f"MATCHED BRANCHES ({len(matched)} branches)")
    print("-" * 70)

    matched_by_state = {}
    for num in matched:
        b = gap_fill_numbers[num]
        state = b.get('state', 'Unknown')
        if state not in matched_by_state:
            matched_by_state[state] = []
        matched_by_state[state].append(num)

    for state in sorted(matched_by_state.keys()):
        nums = matched_by_state[state]
        print(f"  {state}: {', '.join(nums)}")

    # Summary by state
    print(f"\n" + "=" * 70)
    print("SUMMARY BY STATE")
    print("=" * 70)

    all_states = set()
    for b in gap_fill_branches:
        all_states.add(b.get('state', 'Unknown'))

    print(f"\n{'State':<8} {'Gap Fill':<12} {'In OMS':<10} {'New':<10}")
    print("-" * 40)

    total_gap = 0
    total_matched = 0
    total_new = 0

    for state in sorted(all_states):
        gap_count = len([b for b in gap_fill_branches if b.get('state') == state])
        matched_count = len([n for n in matched if gap_fill_numbers[n].get('state') == state])
        new_count = len([n for n in new_to_add if gap_fill_numbers[n].get('state') == state])
        print(f"{state:<8} {gap_count:<12} {matched_count:<10} {new_count:<10}")
        total_gap += gap_count
        total_matched += matched_count
        total_new += new_count

    print("-" * 40)
    print(f"{'TOTAL':<8} {total_gap:<12} {total_matched:<10} {total_new:<10}")

    # OMS enabled status
    print(f"\n" + "=" * 70)
    print("OMS ENABLED STATUS")
    print("=" * 70)

    enabled = [b for b in oms_branches if b.get('oms_enabled')]
    print(f"\nCurrently OMS Enabled: {len(enabled)} branches")
    for b in enabled:
        num = extract_branch_number(b.get('branch_name', ''))
        print(f"  {num} - {b.get('branch_name', '')} - {b.get('city', '')}, {b.get('state', '')}")

    # Save results to JSON
    results = {
        "report_date": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "oms_total": len(oms_branches),
        "gap_fill_total": len(gap_fill_branches),
        "matched_count": len(matched),
        "new_to_add_count": len(new_to_add),
        "oms_only_count": len(oms_only),
        "matched_branches": matched,
        "new_branches": new_to_add,
        "new_branches_detail": [gap_fill_numbers[n] for n in new_to_add],
        "oms_enabled": [extract_branch_number(b.get('branch_name', '')) for b in enabled]
    }

    with open(f"{BASE_DIR}/herc_cross_reference_results.json", 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n" + "=" * 70)
    print(f"Results saved to: herc_cross_reference_results.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
