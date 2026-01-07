import pytest
import pandas as pd
import os
from src.DrugInteractionChecker import DrugInteractionChecker


@pytest.fixture
def sample_csv(tmp_path):
    """Create a temporary CSV file with sample drug interaction data."""
    csv_file = tmp_path / "test_drugs.csv"
    data = {
        'Drug_A': ['aspirin', 'ibuprofen', 'warfarin', 'lisinopril', 'metformin'],
        'Drug_B': ['warfarin', 'aspirin', 'ibuprofen', 'potassium', 'alcohol'],
        'Level': ['Major', 'Moderate', 'Major', 'Major', 'Moderate']
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    return str(csv_file)


@pytest.fixture
def checker(sample_csv):
    """Create a DrugInteractionChecker instance with sample data."""
    return DrugInteractionChecker(sample_csv)


class TestInitialization:
    """Test class initialization and data loading."""

    def test_successful_initialization(self, sample_csv):
        """Test that checker initializes correctly with valid CSV."""
        checker = DrugInteractionChecker(sample_csv)
        assert checker.df is not None
        assert len(checker.df) == 5
        assert checker.drug1_col is not None
        assert checker.drug2_col is not None
        assert checker.level_col is not None

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            DrugInteractionChecker('nonexistent_file.csv')

    def test_column_detection(self, checker):
        """Test that columns are detected correctly."""
        assert 'drug' in checker.drug1_col.lower()
        assert 'drug' in checker.drug2_col.lower()
        assert 'level' in checker.level_col.lower() or 'severity' in checker.level_col.lower()

    def test_data_normalization(self, checker):
        """Test that drug names are normalized to lowercase."""
        assert all(checker.df[checker.drug1_col].str.islower())
        assert all(checker.df[checker.drug2_col].str.islower())


class TestValidation:
    """Test input validation methods."""

    def test_valid_drug_input(self):
        """Test validation accepts valid drug names."""
        is_valid, error = DrugInteractionChecker._validate_drug_input("aspirin")
        assert is_valid is True
        assert error is None

    def test_empty_drug_input(self):
        """Test validation rejects empty input."""
        is_valid, error = DrugInteractionChecker._validate_drug_input("")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_whitespace_only_input(self):
        """Test validation rejects whitespace-only input."""
        is_valid, error = DrugInteractionChecker._validate_drug_input("   ")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_numeric_only_input(self):
        """Test validation rejects purely numeric input."""
        is_valid, error = DrugInteractionChecker._validate_drug_input("12345")
        assert is_valid is False
        assert "purely numeric" in error

    def test_numeric_with_decimals(self):
        """Test validation rejects numeric input with decimals."""
        is_valid, error = DrugInteractionChecker._validate_drug_input("123.45")
        assert is_valid is False
        assert "purely numeric" in error


class TestCheckInteraction:
    """Test the main check_interaction method."""

    def test_interaction_found_order1(self, checker):
        """Test finding interaction in original order (A-B)."""
        result = checker.check_interaction('aspirin', 'warfarin')
        assert result['status'] == 'found'
        assert result['data'] is not None
        assert len(result['data']) == 1
        assert result['data'][0][checker.level_col] == 'Major'

    def test_interaction_found_order2(self, checker):
        """Test finding interaction in reverse order (B-A)."""
        result = checker.check_interaction('warfarin', 'aspirin')
        assert result['status'] == 'found'
        assert result['data'] is not None

    def test_interaction_not_found(self, checker):
        """Test when no interaction exists."""
        result = checker.check_interaction('aspirin', 'metformin')
        assert result['status'] == 'not_found'
        assert result['data'] is None
        assert "No significant interaction" in result['message']

    def test_same_drug_error(self, checker):
        """Test error when checking drug against itself."""
        result = checker.check_interaction('aspirin', 'aspirin')
        assert result['status'] == 'error'
        assert "itself" in result['message']

    def test_case_insensitive_search(self, checker):
        """Test that search is case-insensitive."""
        result1 = checker.check_interaction('ASPIRIN', 'WARFARIN')
        result2 = checker.check_interaction('aspirin', 'warfarin')
        assert result1['status'] == result2['status']
        assert result1['status'] == 'found'

    def test_whitespace_handling(self, checker):
        """Test that extra whitespace is handled correctly."""
        result = checker.check_interaction('  aspirin  ', '  warfarin  ')
        assert result['status'] == 'found'

    def test_invalid_drug1_input(self, checker):
        """Test invalid input for first drug."""
        result = checker.check_interaction('', 'warfarin')
        assert result['status'] == 'invalid_input'
        assert 'Drug 1' in result['message']

    def test_invalid_drug2_input(self, checker):
        """Test invalid input for second drug."""
        result = checker.check_interaction('aspirin', '12345')
        assert result['status'] == 'invalid_input'
        assert 'Drug 2' in result['message']

    def test_multiple_interactions(self, checker):
        """Test drug with multiple interactions."""
        result = checker.check_interaction('aspirin', 'warfarin')
        assert result['status'] == 'found'
        assert 'aspirin' in result['message'].lower()
        assert 'warfarin' in result['message'].lower()


class TestGetAllInteractions:
    """Test the get_all_interactions_for_drug method."""

    def test_get_all_for_drug_with_interactions(self, checker):
        """Test getting all interactions for a drug with known interactions."""
        result = checker.get_all_interactions_for_drug('aspirin')
        assert result['status'] == 'found'
        assert result['data'] is not None
        assert len(result['data']) >= 1

    def test_get_all_for_drug_no_interactions(self, checker):
        """Test getting interactions for drug with none."""
        result = checker.get_all_interactions_for_drug('unknown_drug')
        assert result['status'] == 'not_found'
        assert result['data'] is None

    def test_get_all_case_insensitive(self, checker):
        """Test case insensitivity in get_all_interactions."""
        result = checker.get_all_interactions_for_drug('ASPIRIN')
        assert result['status'] == 'found'

    def test_get_all_invalid_input(self, checker):
        """Test invalid input for get_all_interactions."""
        result = checker.get_all_interactions_for_drug('')
        assert result['status'] == 'invalid_input'

    def test_get_all_counts_correctly(self, checker):
        """Test that interaction count is correct."""
        result = checker.get_all_interactions_for_drug('aspirin')
        if result['status'] == 'found':
            count_in_message = int(result['message'].split()[1])
            assert count_in_message == len(result['data'])


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_drug_with_special_characters(self, checker):
        """Test drug names with special characters."""
        result = checker.check_interaction('aspirin-complex', 'warfarin')
        # Should not crash, might return not_found
        assert result['status'] in ['found', 'not_found', 'invalid_input']

    def test_very_long_drug_name(self, checker):
        """Test with very long drug name."""
        long_name = 'a' * 1000
        result = checker.check_interaction(long_name, 'warfarin')
        assert result['status'] in ['found', 'not_found']

    def test_unicode_drug_name(self, checker):
        """Test with unicode characters."""
        result = checker.check_interaction('aspirín', 'warfarin')
        assert result['status'] in ['found', 'not_found']


class TestDataIntegrity:
    """Test data integrity and structure."""

    def test_return_structure_found(self, checker):
        """Test return structure when interaction is found."""
        result = checker.check_interaction('aspirin', 'warfarin')
        assert 'status' in result
        assert 'message' in result
        assert 'data' in result
        if result['data']:
            assert isinstance(result['data'], list)
            assert all(isinstance(item, dict) for item in result['data'])

    def test_return_structure_not_found(self, checker):
        """Test return structure when interaction is not found."""
        result = checker.check_interaction('drug1', 'drug2')
        assert 'status' in result
        assert 'message' in result
        assert 'data' in result
        assert result['data'] is None


# Integration test
class TestIntegration:
    """Integration tests for complete workflows."""

    def test_multiple_sequential_checks(self, checker):
        """Test multiple checks in sequence."""
        result1 = checker.check_interaction('aspirin', 'warfarin')
        result2 = checker.check_interaction('ibuprofen', 'aspirin')
        result3 = checker.check_interaction('unknown1', 'unknown2')

        assert result1['status'] == 'found'
        assert result2['status'] == 'found'
        assert result3['status'] == 'not_found'

    def test_check_then_get_all(self, checker):
        """Test checking specific interaction then getting all."""
        check_result = checker.check_interaction('aspirin', 'warfarin')
        all_result = checker.get_all_interactions_for_drug('aspirin')

        assert check_result['status'] == 'found'
        assert all_result['status'] == 'found'
        # The specific interaction should be in the full list
        assert len(all_result['data']) >= len(check_result['data'])