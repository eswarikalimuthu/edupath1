"""
CareerCompass - Profile-aware Retrieval Test
"""

from src.agents.retrieval_agent import retrieve_for_profile


profile = {
    "stream": "engineering",
    "education_stage": "school",
    "current_year": "12th standard",
    "state": "Tamil Nadu",
    "category": "SC",
    "board_percentage": 88,
    "annual_income": 200000,
    "interests": ["computer science", "robotics"],
    "constraints": "family income 2 lakh per year",
    "goal": "scholarship options and career advice",
}


def main():

    print("\n" + "=" * 80)
    print("CAREERCOMPASS - PROFILE-AWARE RETRIEVAL TEST")
    print("=" * 80)

    print("\nPROFILE:")
    for key, value in profile.items():
        print(f"{key}: {value}")

    print("\n" + "-" * 80)
    print("RUNNING RETRIEVAL PIPELINE...")
    print("-" * 80)

    results = retrieve_for_profile(profile)

    if not results:
        print("\nNo results returned.")
        return

    print("\nRESULT CATEGORIES:")

    for category, items in results.items():

        print("\n" + "=" * 80)
        print(f"{category.upper()}")
        print("=" * 80)

        if not items:
            print("No results.")
            continue

        for i, item in enumerate(items[:10], 1):

            print(f"\n[{i}]")

            print(
                "Score:",
                item.get(
                    "score",
                    item.get(
                        "retrieval_score",
                        "N/A"
                    )
                )
            )

            print(
                "Source:",
                item.get(
                    "source",
                    "N/A"
                )
            )

            print(
                "Eligibility:",
                item.get(
                    "eligibility_status",
                    "N/A"
                )
            )

            if "match_details" in item:
                print(
                    "Match:",
                    item["match_details"]
                )

            text = item.get(
                "text",
                item.get(
                    "document",
                    ""
                )
            )

            print(
                "Text:",
                text[:500]
            )


if __name__ == "__main__":
    main()