import random
import pandas as pd

categories = {
    "Road Damage": ["pothole", "road crack", "damaged pavement", "broken road"],
    "Waste Management": ["garbage", "trash", "waste dump", "overflowing bin"],
    "Electrical Issues": ["electric wire", "power failure", "streetlight issue", "spark"],
    "Water Leakage": ["water leak", "pipe burst", "drain overflow", "flood"],
    "Illegal Construction": ["illegal building", "unauthorized construction", "encroachment"]
}

data = []

for _ in range(200):
    category = random.choice(list(categories.keys()))
    keyword = random.choice(categories[category])

    description = f"{keyword} reported in area causing issues"

    if category == "Electrical Issues":
        score = random.randint(60, 100)
    elif category == "Road Damage":
        score = random.randint(30, 80)
    elif category == "Water Leakage":
        score = random.randint(40, 90)
    elif category == "Waste Management":
        score = random.randint(20, 60)
    else:
        score = random.randint(50, 85)

    data.append([description, category, score])

df = pd.DataFrame(data, columns=["description", "category", "risk_score"])
df.to_csv("data.csv", index=False)

print("dataset created!")