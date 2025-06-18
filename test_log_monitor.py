import unittest
from log_monitor import LogMonitor

class TestLogMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = LogMonitor("dummy_path", "dummy_host", 12201)

    def test_parse_debug_line(self):
        test_cases = [
            (
                "14:25 19376  152ms   195M 3650G 173/200U INFO terranbot.builds.plans.acts.tbone_attack:1077 self.ai.game_analyzer.enemy_power=(ExtendedPower) self.power=5.0, self.air_power=0, self.ground_power=5.0 self.siege_power=0",
                {
                    'game_time': '14:25',
                    'game_step': 19376,
                    'step_length': '152ms',
                    'minerals': '195M',
                    'gas': '3650G',
                    'supply_used': 173,
                    'supply_capacity': 200,
                    'log_level': 'INFO',
                    'source_file': 'terranbot.builds.plans.acts.tbone_attack',
                    'line_number': 1077,
                    'message': 'self.ai.game_analyzer.enemy_power=(ExtendedPower) self.power=5.0, self.air_power=0, self.ground_power=5.0 self.siege_power=0'
                }
            ),
            (
                "14:29 19476  170ms   380M 3702G 173/200U Level 20 sharpy.managers.core.log_manager:71 [EnemyArmyPredicter] Predicting negative free minerals for enemy: -1135",
                {
                    'game_time': '14:29',
                    'game_step': 19476,
                    'step_length': '170ms',
                    'minerals': '380M',
                    'gas': '3702G',
                    'supply_used': 173,
                    'supply_capacity': 200,
                    'log_level': 'Level 20',
                    'source_file': 'sharpy.managers.core.log_manager',
                    'line_number': 71,
                    'message': '[EnemyArmyPredicter] Predicting negative free minerals for enemy: -1135'
                }
            ),
            (
                "14:35 19604  161ms    45M 3637G 177/200U INFO terranbot.builds.plans.acts.tbone_attack:1074 self.ai.game_analyzer.our_army_predict=<Advantage.OverwhelmingAdvantage: 4>",
                {
                    'game_time': '14:35',
                    'game_step': 19604,
                    'step_length': '161ms',
                    'minerals': '45M',
                    'gas': '3637G',
                    'supply_used': 177,
                    'supply_capacity': 200,
                    'log_level': 'INFO',
                    'source_file': 'terranbot.builds.plans.acts.tbone_attack',
                    'line_number': 1074,
                    'message': 'self.ai.game_analyzer.our_army_predict=<Advantage.OverwhelmingAdvantage: 4>'
                }
            ),
            (
                "06:07 8232   86ms    61M  212G  84/110U DEBUG terranbot.builds.plans.acts.zone_defense:299 Number enemies near main natural: 2",
                {
                    'game_time': '06:07',
                    'game_step': 8232,
                    'step_length': '86ms',
                    'minerals': '61M',
                    'gas': '212G',
                    'supply_used': 84,
                    'supply_capacity': 110,
                    'log_level': 'DEBUG',
                    'source_file': 'terranbot.builds.plans.acts.zone_defense',
                    'line_number': 299,
                    'message': 'Number enemies near main natural: 2'
                }
            ),
            (
                "06:07 8232   86ms    61M  212G  84/110U DEBUG terranbot.builds.plans.acts.zone_defense:339 Zone 1 enemies: Counter({UnitTypeId.ROACH: 2})",
                {
                    'game_time': '06:07',
                    'game_step': 8232,
                    'step_length': '86ms',
                    'minerals': '61M',
                    'gas': '212G',
                    'supply_used': 84,
                    'supply_capacity': 110,
                    'log_level': 'DEBUG',
                    'source_file': 'terranbot.builds.plans.acts.zone_defense',
                    'line_number': 339,
                    'message': 'Zone 1 enemies: Counter({UnitTypeId.ROACH: 2})'
                }
            ),
            (
                "06:07 8232   86ms    61M  212G  84/110U DEBUG terranbot.builds.plans.acts.zone_defense:358 Ranked enemy groups: 0.80 - [Unit(name='Roach', tag=4396679170)]((134.005859375, 128.77978515625)), 0.80 - [Unit(name='Roach', tag=4399824897)]((132.64990234375, 128.68408203125))",
                {
                    'game_time': '06:07',
                    'game_step': 8232,
                    'step_length': '86ms',
                    'minerals': '61M',
                    'gas': '212G',
                    'supply_used': 84,
                    'supply_capacity': 110,
                    'log_level': 'DEBUG',
                    'source_file': 'terranbot.builds.plans.acts.zone_defense',
                    'line_number': 358,
                    'message': "Ranked enemy groups: 0.80 - [Unit(name='Roach', tag=4396679170)]((134.005859375, 128.77978515625)), 0.80 - [Unit(name='Roach', tag=4399824897)]((132.64990234375, 128.68408203125))"
                }
            ),
            (
                "09:21 12572 116ms 164M 993G 81/158U WARNING terranbot.builds.plans.acts.tbone_attack:747 No ground units for main_army, using center of group",
                {
                    'game_time': '09:21',
                    'game_step': 12572,
                    'step_length': '116ms',
                    'minerals': '164M',
                    'gas': '993G',
                    'supply_used': 81,
                    'supply_capacity': 158,
                    'log_level': 'WARNING',
                    'source_file': 'terranbot.builds.plans.acts.tbone_attack',
                    'line_number': 747,
                    'message': 'No ground units for main_army, using center of group'
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
            "14:25 19376  152ms   195M 3650G 173/200U",  # Missing log level and source
        ]

        for line in invalid_lines:
            with self.subTest(line=line):
                result = self.monitor._parse_debug_line(line)
                self.assertIsNone(result, f"Should not parse invalid line: {line}")

if __name__ == '__main__':
    unittest.main() 