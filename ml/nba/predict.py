import sys
from pathlib import Path


# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# --------------------------------------------------
# Import existing ML + NBA components
# --------------------------------------------------
from ml.customer_profile import create_customer_profile
from ml.nba.engine import get_next_best_action


# --------------------------------------------------
# Complete Customer Recommendation
# --------------------------------------------------
def get_customer_recommendation(
    recency,
    frequency,
    monetary,
    total_quantity,
    avg_order_value
):
    """
    Generate the ML customer profile and
    apply the owner's NBA rules.
    """

    profile = create_customer_profile(
        recency=recency,
        frequency=frequency,
        monetary=monetary,
        total_quantity=total_quantity,
        avg_order_value=avg_order_value
    )

    recommendation = get_next_best_action(profile)

    return {
        "customer_profile": profile,
        "next_best_action": recommendation
    }
