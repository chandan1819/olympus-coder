"""
End-to-End Testing Package for Olympus-Coder-v1

This package provides comprehensive end-to-end testing capabilities including:
- Multi-turn conversation testing
- Real-world coding task simulations  
- Complete scenario-based testing
- Requirements validation and compliance checking

Requirements addressed: 5.1, 5.2, 5.4, 5.5
"""

from .end_to_end_test_suite import EndToEndTestSuite, EndToEndTestScenario
from .conversation_tests import ConversationTestSuite, ConversationValidator
from .real_world_simulations import RealWorldTaskSimulator, RealWorldTask
from .run_end_to_end_tests import ComprehensiveEndToEndRunner

__all__ = [
    "EndToEndTestSuite",
    "EndToEndTestScenario", 
    "ConversationTestSuite",
    "ConversationValidator",
    "RealWorldTaskSimulator",
    "RealWorldTask",
    "ComprehensiveEndToEndRunner"
]