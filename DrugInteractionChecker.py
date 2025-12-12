import pandas as pd
import re


class DrugInteractionChecker:
    """
    A class to check drug-drug interactions from a CSV database.
    """

    def __init__(self, csv_filepath):
        """Initialize the checker with the CSV file path."""
        self.df = None
        self.filepath = csv_filepath
        self.drug1_col = None
        self.drug2_col = None
        self.level_col = None
        self._load_data()

    def _load_data(self):
        """Load and preprocess the drug interaction data."""
        try:
            self.df = pd.read_csv(self.filepath)

            print(f"Detected columns: {list(self.df.columns)}")

            # Detect Drug_A column
            drug_a_candidates = [col for col in self.df.columns if 'drug' in col.lower() and 'a' in col.lower()]
            self.drug1_col = drug_a_candidates[0] if drug_a_candidates else self.df.columns[1]

            # Detect Drug_B column
            drug_b_candidates = [col for col in self.df.columns if 'drug' in col.lower() and 'b' in col.lower()]
            self.drug2_col = drug_b_candidates[0] if drug_b_candidates else self.df.columns[3]

            # Detect Level column
            level_candidates = [col for col in self.df.columns if 'level' in col.lower() or 'severity' in col.lower()]
            self.level_col = level_candidates[0] if level_candidates else self.df.columns[4]

            print(f"Using columns: {self.drug1_col}, {self.drug2_col}, {self.level_col}")

            # Normalize drug names to lowercase
            self.df[self.drug1_col] = self.df[self.drug1_col].str.lower().str.strip()
            self.df[self.drug2_col] = self.df[self.drug2_col].str.lower().str.strip()

            print(f"Successfully loaded {len(self.df)} drug interactions\n")

        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.filepath}")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    @staticmethod
    def _validate_drug_input(drug_name):
        """Validate that drug input is not empty or purely numeric."""
        if not drug_name or not drug_name.strip():
            return False, "Drug name cannot be empty"
        if re.match(r'^[\d.,\s]+$', drug_name.strip()):
            return False, "Invalid input: Drug name cannot be purely numeric"
        return True, None

    def check_interaction(self, drug1, drug2):
        """
        Check for interaction between two drugs.

        Args:
            drug1: First drug name
            drug2: Second drug name

        Returns:
            dict: Contains status, message, and data
        """
        # Validate inputs
        is_valid, error_msg = self._validate_drug_input(drug1)
        if not is_valid:
            return {
                'status': 'invalid_input',
                'message': f"Drug 1 - {error_msg}",
                'data': None
            }

        is_valid, error_msg = self._validate_drug_input(drug2)
        if not is_valid:
            return {
                'status': 'invalid_input',
                'message': f"Drug 2 - {error_msg}",
                'data': None
            }

        # Normalize inputs
        d1 = drug1.lower().strip()
        d2 = drug2.lower().strip()

        # Check same drug
        if d1 == d2:
            return {
                'status': 'error',
                'message': "Cannot check interaction of a drug with itself",
                'data': None
            }

        # Search for interaction (both directions: A-B and B-A)
        match = self.df[
            ((self.df[self.drug1_col] == d1) & (self.df[self.drug2_col] == d2)) |
            ((self.df[self.drug1_col] == d2) & (self.df[self.drug2_col] == d1))
            ]

        # Return results
        if not match.empty:
            interactions = match[[self.drug1_col, self.drug2_col, self.level_col]].to_dict('records')
            return {
                'status': 'found',
                'message': f"Interaction found between {drug1} and {drug2}",
                'data': interactions
            }
        else:
            return {
                'status': 'not_found',
                'message': "No significant interaction found",
                'data': None
            }

    def get_all_interactions_for_drug(self, drug_name):
        """
        Get all interactions for a specific drug.

        Args:
            drug_name: The drug to search for

        Returns:
            dict: Contains status, message, and list of all interactions
        """
        is_valid, error_msg = self._validate_drug_input(drug_name)
        if not is_valid:
            return {
                'status': 'invalid_input',
                'message': error_msg,
                'data': None
            }

        drug = drug_name.lower().strip()

        # Find all interactions
        matches = self.df[
            (self.df[self.drug1_col] == drug) | (self.df[self.drug2_col] == drug)
            ]

        if not matches.empty:
            interactions = matches[[self.drug1_col, self.drug2_col, self.level_col]].to_dict('records')
            return {
                'status': 'found',
                'message': f"Found {len(interactions)} interaction(s) for {drug_name}",
                'data': interactions
            }
        else:
            return {
                'status': 'not_found',
                'message': f"No interactions found for {drug_name}",
                'data': None
            }


def main():
    """Main function with continuous user input."""

    # Initialize the checker
    try:
        checker = DrugInteractionChecker('drug_interaction.csv')
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure 'drug_interaction.csv' is in the same folder as this script.")
        return

    # Welcome message
    print("=" * 70)
    print(" " * 18 + "DRUG-DRUG INTERACTION CHECKER")
    print("=" * 70)
    print("Enter two drug names to check for interactions")
    print("Type 'quit' or 'exit' at any time to close")
    print("=" * 70)

    # Main loop
    while True:
        print("\n")
        drug1 = input("Enter Drug 1: ").strip()

        if drug1.lower() in ['quit', 'exit', 'q']:
            print("\nThank you for using Drug Interaction Checker. Goodbye!")
            break

        drug2 = input("Enter Drug 2: ").strip()

        if drug2.lower() in ['quit', 'exit', 'q']:
            print("\nThank you for using Drug Interaction Checker. Goodbye!")
            break

        # Check interaction
        result = checker.check_interaction(drug1, drug2)

        # Display results
        print("\n" + "=" * 70)
        print(f"STATUS: {result['status'].upper()}")
        print("=" * 70)
        print(result['message'])

        if result['data']:
            print("-" * 70)
            for interaction in result['data']:
                print(f"\nDrug A: {interaction[checker.drug1_col].title()}")
                print(f"Drug B: {interaction[checker.drug2_col].title()}")
                print(f"Interaction Level: {interaction[checker.level_col]}")

        print("=" * 70)


if __name__ == "__main__":
    main()