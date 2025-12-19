import pandas as pd
import re


class DrugInteractionChecker:

    def __init__(self, csv_file):
        try:
            self.df = pd.read_csv(csv_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{csv_file}' not found")
        except Exception as e:
            raise Exception(f"Error reading CSV: {e}")

        # Clean column names
        self.df.columns = self.df.columns.str.strip()

        # Auto-detect columns with fallback
        cols = self.df.columns

        # Find drug A column
        drug_a = [c for c in cols if 'drug' in c.lower() and 'a' in c.lower()]
        self.drug1_col = drug_a[0] if drug_a else cols[0]

        # Find drug B column
        drug_b = [c for c in cols if 'drug' in c.lower() and 'b' in c.lower()]
        self.drug2_col = drug_b[0] if drug_b else cols[1]

        # Find level column
        level = [c for c in cols if 'level' in c.lower() or 'severity' in c.lower()]
        self.level_col = level[0] if level else cols[2]

        print(f"Using columns: {self.drug1_col}, {self.drug2_col}, {self.level_col}")

        # Check if columns exist and have data
        if self.df.empty:
            raise ValueError("CSV file is empty")

        # Normalize to lowercase and handle NaN values
        self.df[self.drug1_col] = self.df[self.drug1_col].astype(str).str.lower().str.strip()
        self.df[self.drug2_col] = self.df[self.drug2_col].astype(str).str.lower().str.strip()

        # Remove rows with 'nan' strings
        self.df = self.df[
            (self.df[self.drug1_col] != 'nan') &
            (self.df[self.drug2_col] != 'nan')
            ]

        # Store all drugs for quick lookup
        self.all_drugs = set(self.df[self.drug1_col]) | set(self.df[self.drug2_col])

        print(f"Loaded {len(self.df)} interactions with {len(self.all_drugs)} drugs\n")

    @staticmethod
    def is_valid_input(drug):
        # Check empty
        if not drug or not drug.strip():
            return False, "Drug name cannot be empty"

        # Check only letters (no numbers or symbols)
        if not re.match(r'^[a-zA-Z\s-]+$', drug.strip()):
            return False, "Only English letters allowed (no numbers/symbols)"

        return True, ""

    def check_interaction(self, drug1, drug2):
        # Validate inputs
        valid, msg = self.is_valid_input(drug1)
        if not valid:
            print(f"Error: {msg}")
            return

        valid, msg = self.is_valid_input(drug2)
        if not valid:
            print(f"Error: {msg}")
            return

        # Normalize
        d1 = drug1.lower().strip()
        d2 = drug2.lower().strip()

        # Check same drug
        if d1 == d2:
            print("Error: Cannot check a drug with itself")
            return

        # Check if drugs exist
        if d1 not in self.all_drugs:
            print(f"Drug not found: '{drug1}' - Check spelling")
            return

        if d2 not in self.all_drugs:
            print(f"Drug not found: '{drug2}' - Check spelling")
            return

        # Find interaction
        result = self.df[
            ((self.df[self.drug1_col] == d1) & (self.df[self.drug2_col] == d2)) |
            ((self.df[self.drug1_col] == d2) & (self.df[self.drug2_col] == d1))
            ]

        # Print result
        print("\n" + "=" * 60)
        if not result.empty:
            print("⚠️  INTERACTION FOUND")
            print("=" * 60)
            level = result.iloc[0][self.level_col]
            print(f"Drug A: {drug1.title()}")
            print(f"Drug B: {drug2.title()}")
            print(f"Level: {level}")
        else:
            print("✓ NO INTERACTION")
            print("=" * 60)
            print(f"{drug1.title()} and {drug2.title()} can be used together")
        print("=" * 60 + "\n")


def main():
    # Load database
    try:
        checker = DrugInteractionChecker('drug_interaction.csv')
    except FileNotFoundError:
        print("Error: 'drug_interaction.csv' not found in current folder!")
        return
    except ValueError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print("=" * 60)
    print("         DRUG INTERACTION CHECKER")
    print("=" * 60)
    print("Type 'quit' to exit\n")

    # Main loop
    while True:
        try:
            drug1 = input("Drug 1: ").strip()
            if drug1.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            drug2 = input("Drug 2: ").strip()
            if drug2.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            checker.check_interaction(drug1, drug2)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()