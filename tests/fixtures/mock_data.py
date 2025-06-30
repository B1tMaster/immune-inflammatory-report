"""Mock data generators for testing immune inflammatory index calculations."""

from typing import Dict, Any, List
from datetime import date, datetime
import random


class BloodTestDataGenerator:
    """Generate realistic blood test data for testing."""
    
    # Normal ranges (cells/μL)
    NORMAL_RANGES = {
        "neutrophils": (1800, 7700),
        "lymphocytes": (1000, 4000),
        "platelets": (150000, 450000),
        "monocytes": (200, 800),
    }
    
    @classmethod
    def normal_values(cls) -> Dict[str, float]:
        """Generate normal blood values."""
        return {
            "neutrophils": 4200.0,
            "lymphocytes": 1800.0,
            "platelets": 250000.0,
            "monocytes": 480.0,
        }
    
    @classmethod
    def high_inflammation_values(cls) -> Dict[str, float]:
        """Generate values indicating high inflammation."""
        return {
            "neutrophils": 8500.0,
            "lymphocytes": 1200.0,
            "platelets": 450000.0,
            "monocytes": 800.0,
        }
    
    @classmethod
    def low_inflammation_values(cls) -> Dict[str, float]:
        """Generate values indicating low inflammation."""
        return {
            "neutrophils": 2500.0,
            "lymphocytes": 2800.0,
            "platelets": 180000.0,
            "monocytes": 300.0,
        }
    
    @classmethod
    def extreme_high_values(cls) -> Dict[str, float]:
        """Generate extremely high values for edge case testing."""
        return {
            "neutrophils": 15000.0,
            "lymphocytes": 800.0,
            "platelets": 800000.0,
            "monocytes": 1200.0,
        }
    
    @classmethod
    def extreme_low_values(cls) -> Dict[str, float]:
        """Generate extremely low values for edge case testing."""
        return {
            "neutrophils": 500.0,
            "lymphocytes": 500.0,
            "platelets": 50000.0,
            "monocytes": 100.0,
        }
    
    @classmethod
    def boundary_values(cls) -> List[Dict[str, float]]:
        """Generate boundary values for testing."""
        return [
            # Lower boundaries
            {
                "neutrophils": cls.NORMAL_RANGES["neutrophils"][0],
                "lymphocytes": cls.NORMAL_RANGES["lymphocytes"][0],
                "platelets": cls.NORMAL_RANGES["platelets"][0],
                "monocytes": cls.NORMAL_RANGES["monocytes"][0],
            },
            # Upper boundaries
            {
                "neutrophils": cls.NORMAL_RANGES["neutrophils"][1],
                "lymphocytes": cls.NORMAL_RANGES["lymphocytes"][1],
                "platelets": cls.NORMAL_RANGES["platelets"][1],
                "monocytes": cls.NORMAL_RANGES["monocytes"][1],
            },
        ]
    
    @classmethod
    def random_values(cls, count: int = 10) -> List[Dict[str, float]]:
        """Generate random blood values within normal ranges."""
        values = []
        for _ in range(count):
            values.append({
                "neutrophils": random.uniform(*cls.NORMAL_RANGES["neutrophils"]),
                "lymphocytes": random.uniform(*cls.NORMAL_RANGES["lymphocytes"]),
                "platelets": random.uniform(*cls.NORMAL_RANGES["platelets"]),
                "monocytes": random.uniform(*cls.NORMAL_RANGES["monocytes"]),
            })
        return values


class PatientDataGenerator:
    """Generate patient demographic data for testing."""
    
    @classmethod
    def young_adult_male(cls) -> Dict[str, Any]:
        """Young adult male patient."""
        return {
            "age": 25,
            "sex": "M",
            "test_date": date(2025, 6, 30),
        }
    
    @classmethod
    def young_adult_female(cls) -> Dict[str, Any]:
        """Young adult female patient."""
        return {
            "age": 24,
            "sex": "F",
            "test_date": date(2025, 6, 30),
        }
    
    @classmethod
    def middle_aged_male(cls) -> Dict[str, Any]:
        """Middle-aged male patient."""
        return {
            "age": 52,
            "sex": "M",
            "test_date": date(2025, 6, 30),
        }
    
    @classmethod
    def middle_aged_female(cls) -> Dict[str, Any]:
        """Middle-aged female patient."""
        return {
            "age": 45,
            "sex": "F",
            "test_date": date(2025, 6, 30),
        }
    
    @classmethod
    def elderly_male(cls) -> Dict[str, Any]:
        """Elderly male patient."""
        return {
            "age": 72,
            "sex": "M",
            "test_date": date(2025, 6, 30),
        }
    
    @classmethod
    def elderly_female(cls) -> Dict[str, Any]:
        """Elderly female patient."""
        return {
            "age": 68,
            "sex": "F",
            "test_date": date(2025, 6, 30),
        }
    
    @classmethod
    def edge_case_ages(cls) -> List[Dict[str, Any]]:
        """Generate edge case ages for testing."""
        return [
            {"age": 18, "sex": "M", "test_date": date(2025, 6, 30)},  # Minimum adult age
            {"age": 35, "sex": "F", "test_date": date(2025, 6, 30)},  # Boundary between young and middle-aged
            {"age": 65, "sex": "M", "test_date": date(2025, 6, 30)},  # Boundary between middle-aged and elderly
            {"age": 100, "sex": "F", "test_date": date(2025, 6, 30)}, # Very elderly
        ]


class ExpectedResults:
    """Expected calculation results for test validation."""
    
    @classmethod
    def normal_indices(cls) -> Dict[str, float]:
        """Expected indices for normal blood values."""
        # Based on: neutrophils=4200, lymphocytes=1800, platelets=250000, monocytes=480
        return {
            "sii": 583.33,  # (4200 * 250000) / 1800
            "nlr": 2.33,    # 4200 / 1800
            "plr": 138.89,  # 250000 / 1800
            "siri": 1.12,   # (4200 * 480) / 1800
            "mlr": 0.27,    # 480 / 1800
            "piv": 280.0,   # (4200 * 250000 * 480) / 1800
        }
    
    @classmethod
    def high_inflammation_indices(cls) -> Dict[str, float]:
        """Expected indices for high inflammation values."""
        # Based on: neutrophils=8500, lymphocytes=1200, platelets=450000, monocytes=800
        return {
            "sii": 3187.5,   # (8500 * 450000) / 1200
            "nlr": 7.08,     # 8500 / 1200
            "plr": 375.0,    # 450000 / 1200
            "siri": 5.67,    # (8500 * 800) / 1200
            "mlr": 0.67,     # 800 / 1200
            "piv": 2550.0,   # (8500 * 450000 * 800) / 1200
        }


# Pre-defined test scenarios
TEST_SCENARIOS = [
    {
        "name": "normal_young_male",
        "blood_values": BloodTestDataGenerator.normal_values(),
        "patient_data": PatientDataGenerator.young_adult_male(),
        "expected_indices": ExpectedResults.normal_indices(),
    },
    {
        "name": "high_inflammation_elderly_female",
        "blood_values": BloodTestDataGenerator.high_inflammation_values(),
        "patient_data": PatientDataGenerator.elderly_female(),
        "expected_indices": ExpectedResults.high_inflammation_indices(),
    },
    {
        "name": "low_inflammation_middle_aged_male",
        "blood_values": BloodTestDataGenerator.low_inflammation_values(),
        "patient_data": PatientDataGenerator.middle_aged_male(),
    },
]