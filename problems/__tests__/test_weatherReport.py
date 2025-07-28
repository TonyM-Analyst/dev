# test_refactor.py

import unittest

class FakeHttpClient:
    def get(self, url):
        class FakeResponse:
            def json(self):
                return {"temperature": 22}
        return FakeResponse()

class TestableWeatherReporter:
    def __init__(self):
        from problems.weatherReport import WeatherReporter
        self.output_message = None
        self.reporter = WeatherReporter(http_client=FakeHttpClient())
        self.reporter.output = self.capture_output

    def capture_output(self, msg):
        self.output_message = msg

    def run_test(self):
        self.reporter.report("NewYork")
        return self.output_message

class TestWeatherReporter(unittest.TestCase):
    def test_report_outputs_temperature(self):
        testable = TestableWeatherReporter()
        result = testable.run_test()
        self.assertEqual(result, "The temperature in NewYork is 22°C.")

if __name__ == "__main__":
    unittest.main()
