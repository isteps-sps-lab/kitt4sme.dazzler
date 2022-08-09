from dazzler.dash.board.insight import IgRecommendationMatrix


def example_ngsi_structured_value() -> dict:
    return {
		"KPI_name": ["KPI1", "KPI2"],
		"features_names":[
            ["AcelX", "AcelY", "AcelR", "fz", "Diam", "FaMS"],
            ["AcelR", "Fy", "fz", "Diam", "ae", "HB"]
        ],
		"features_values":[
            [2.224, 2.539, 3.445, 0.085, 14.317, 5.097],
            [3.445, 213.942, 0.033, 9.464, 4.635, 125.412]
        ],
		"KPI_best": ["160.3168", "0.0"]
	}


def test_from_struct_val_to_recommendations():
    ngsi = example_ngsi_structured_value()
    recommendations = IgRecommendationMatrix(ngsi).to_recommendations()

    assert len(recommendations) == 2

    r1 = recommendations[0]
    r2 = recommendations[1]

    assert r1.kpi_name == "KPI1"
    assert r1.kpi_best == 160.3168
    assert len(r1.features) == 6

    r1_feature_tuples = [(f.name, f.value) for f in r1.features]

    assert r1_feature_tuples == [
        ("AcelX", 2.224), ("AcelY", 2.539), ("AcelR", 3.445),
        ("fz", 0.085), ("Diam", 14.317), ("FaMS", 5.097)
    ]

    assert r2.kpi_name == "KPI2"
    assert r2.kpi_best == 0
    assert len(r2.features) == 6

    r2_feature_tuples = [(f.name, f.value) for f in r2.features]

    assert r2_feature_tuples == [
        ("AcelR", 3.445), ("Fy", 213.942), ("fz", 0.033),
        ("Diam", 9.464), ("ae", 4.635), ("HB", 125.412)
    ]
