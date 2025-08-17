from app.categorize import Categorizer

def test_rules_win_over_model():
    c = Categorizer("rules.yaml", "model.pkl")
    assert c.predict("UBER *TRIP", 42.0) == "transport"
    assert c.predict("SUSHI RIO", 25.0) == "dining"
