import unittest
from log_monitor import LogMonitor

class TestLogMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = LogMonitor("dummy_path", "dummy_host", 12201)

    def test_parse_debug_line(self):
        test_cases = [
            (
                "00:10  240   43ms     0M    0G  13/ 15U sharpy.managers.core.log_manager:71 [GameAnalyzer] Income advantage is now SlightAdvantage",
                {
                    'game_time': '00:10',
                    'game_step': 240,
                    'step_length': '43ms',
                    'minerals': '0M',
                    'gas': '0G',
                    'supply_used': 13,
                    'supply_capacity': 15,
                    'source_file': 'sharpy.managers.core.log_manager',
                    'line_number': 71,
                    'message': '[GameAnalyzer] Income advantage is now SlightAdvantage'
                }
            ),
            (
                "00:15  340   37ms     0M    0G  13/ 15U sharpy.managers.core.log_manager:71 [TrainSCV] SCV from COMMANDCENTER at (154.5, 114.5)",
                {
                    'game_time': '00:15',
                    'game_step': 340,
                    'step_length': '37ms',
                    'minerals': '0M',
                    'gas': '0G',
                    'supply_used': 13,
                    'supply_capacity': 15,
                    'source_file': 'sharpy.managers.core.log_manager',
                    'line_number': 71,
                    'message': '[TrainSCV] SCV from COMMANDCENTER at (154.5, 114.5)'
                }
            ),
            (
                "00:20  456   35ms    65M    0G  14/ 15U terranbot.builds.plans.acts.tbone_attack:1074 self.ai.game_analyzer.our_army_predict=<Advantage.SlightAdvantage: 1>",
                {
                    'game_time': '00:20',
                    'game_step': 456,
                    'step_length': '35ms',
                    'minerals': '65M',
                    'gas': '0G',
                    'supply_used': 14,
                    'supply_capacity': 15,
                    'source_file': 'terranbot.builds.plans.acts.tbone_attack',
                    'line_number': 1074,
                    'message': 'self.ai.game_analyzer.our_army_predict=<Advantage.SlightAdvantage: 1>'
                }
            ),
            (
                "00:20  456   35ms    65M    0G  14/ 15U terranbot.builds.plans.acts.tbone_attack:1075 self.ai.game_analyzer.enemy_predict_power=(ExtendedPower) self.power=0, self.air_power=0, self.ground_power=0 self.siege_power=0",
                {
                    'game_time': '00:20',
                    'game_step': 456,
                    'step_length': '35ms',
                    'minerals': '65M',
                    'gas': '0G',
                    'supply_used': 14,
                    'supply_capacity': 15,
                    'source_file': 'terranbot.builds.plans.acts.tbone_attack',
                    'line_number': 1075,
                    'message': 'self.ai.game_analyzer.enemy_predict_power=(ExtendedPower) self.power=0, self.air_power=0, self.ground_power=0 self.siege_power=0'
                }
            )
        ]

        for input_line, expected_output in test_cases:
            with self.subTest(input_line=input_line):
                result = self.monitor._parse_debug_line(input_line)
                self.assertIsNotNone(result, f"Failed to parse line: {input_line}")
                self.assertEqual(result, expected_output, f"Parsing mismatch for line: {input_line}")

    def test_invalid_lines(self):
        invalid_lines = [
            "00",  # Too short
            "Not a debug line",  # Wrong format
            "00:10  240   43ms     0M    0G  13/ 15U",  # Missing source and message
        ]

        for line in invalid_lines:
            with self.subTest(line=line):
                result = self.monitor._parse_debug_line(line)
                self.assertIsNone(result, f"Should not parse invalid line: {line}")

if __name__ == '__main__':
    unittest.main() 