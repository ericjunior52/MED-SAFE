import pandas as pd

# Load the CSV
df = pd.read_csv('drug_interaction.csv')

# Normalize columns
df['Drug_A'] = df['Drug_A'].str.lower().str.strip()
df['Drug_B'] = df['Drug_B'].str.lower().str.strip()

# Check if these exact drugs exist
d1 = 'methoxsalen'
d2 = 'verteporfin'

print(f"Searching for: '{d1}' and '{d2}'")
print("\n1. Check if methoxsalen exists in Drug_A or Drug_B:")
print(f"   In Drug_A: {(df['Drug_A'] == d1).sum()} times")
print(f"   In Drug_B: {(df['Drug_B'] == d1).sum()} times")

print("\n2. Check if verteporfin exists in Drug_A or Drug_B:")
print(f"   In Drug_A: {(df['Drug_A'] == d2).sum()} times")
print(f"   In Drug_B: {(df['Drug_B'] == d2).sum()} times")

print("\n3. Check for the interaction (both directions):")
match1 = df[(df['Drug_A'] == d1) & (df['Drug_B'] == d2)]
match2 = df[(df['Drug_A'] == d2) & (df['Drug_B'] == d1)]

print(f"   Drug_A=methoxsalen AND Drug_B=verteporfin: {len(match1)} matches")
print(f"   Drug_A=verteporfin AND Drug_B=methoxsalen: {len(match2)} matches")

print("\n4. All interactions involving methoxsalen:")
methox_interactions = df[(df['Drug_A'] == d1) | (df['Drug_B'] == d1)]
print(f"   Found {len(methox_interactions)} interactions")
if len(methox_interactions) > 0:
    print("\n   First 10 interactions:")
    print(methox_interactions[['Drug_A', 'Drug_B', 'Level']].head(10))

print("\n5. All interactions involving verteporfin:")
vertep_interactions = df[(df['Drug_A'] == d2) | (df['Drug_B'] == d2)]
print(f"   Found {len(vertep_interactions)} interactions")
if len(vertep_interactions) > 0:
    print("\n   First 10 interactions:")
    print(vertep_interactions[['Drug_A', 'Drug_B', 'Level']].head(10))