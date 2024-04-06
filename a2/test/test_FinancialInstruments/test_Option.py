from src.FinancialInstruments.Option import Option
TOL = 1e-3


class TestOption:
    def test_basic_price(self):
        option = Option(300, 250, 0.03, 1, 0.15)
        assert abs(option.price() - 58.82) < TOL
    
    def test_basic_delta(self):
        option = Option(300, 250, 0.03, 1, 0.15)
        assert abs(option.delta() - 0.932) < TOL