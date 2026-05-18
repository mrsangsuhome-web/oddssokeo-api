```python id="live-engine-v2"
        steam_data = [

            {

                "match": "PSG vs Marseille",

                "home_team": "PSG",

                "away_team": "Marseille",

                "status": "LIVE",

                "minute": random.randint(12, 88),

                "kickoff_in": 0,

                "market": "O/U 2.5",

                "line": "2.5",

                "odds": round(

                    random.uniform(
                        0.80,
                        1.20
                    ),

                    2

                ),

                "steam_level": random.choice(

                    [

                        "LOW",

                        "MEDIUM",

                        "HIGH",

                        "EXTREME"

                    ]

                ),

                "velocity": random.randint(

                    40,

                    95

                ),

                "lead_book": "SBOBET",

                "follow_book": "ISN",

                "follow_delay": random.randint(

                    1,

                    8

                ),

                "move": "+0.05"

            },

            {

                "match": "Barcelona vs Real Madrid",

                "home_team": "Barcelona",

                "away_team": "Real Madrid",

                "status": "STARTING SOON",

                "minute": 0,

                "kickoff_in": random.randint(

                    5,

                    28

                ),

                "market": "O/U 3.0",

                "line": "3.0",

                "odds": round(

                    random.uniform(
                        0.80,
                        1.20
                    ),

                    2

                ),

                "steam_level": random.choice(

                    [

                        "LOW",

                        "MEDIUM",

                        "HIGH"

                    ]

                ),

                "velocity": random.randint(

                    30,

                    90

                ),

                "lead_book": "SABA",

                "follow_book": "KSPORT",

                "follow_delay": random.randint(

                    1,

                    8

                ),

                "move": "-0.04"

            }

        ]
```
