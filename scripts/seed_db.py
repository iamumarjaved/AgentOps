"""Seed the database with sample data for development."""
import sys
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, "src")

from agentops.config import settings
from agentops.db.models import ABTest, Base, GroundTruth


def seed():
    engine = create_engine(settings.database_url_sync)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        # Seed A/B test
        ab_test = ABTest(
            name="model_comparison_v1",
            description="Compare GPT-4o vs GPT-4o-mini for research pipeline",
            variants=[
                {"name": "control", "weight": 0.5, "config": {"model": "gpt-4o"}},
                {"name": "treatment", "weight": 0.5, "config": {"model": "gpt-4o-mini"}},
            ],
        )
        session.add(ab_test)

        # Seed ground truths
        ground_truths = [
            GroundTruth(
                topic="The impact of quantum computing on cryptography",
                expected_output="Quantum computing poses a significant threat to current cryptographic systems, particularly RSA and ECC. Post-quantum cryptography standards (NIST) are being developed. Key points: Shor's algorithm, lattice-based cryptography, quantum key distribution.",
            ),
            GroundTruth(
                topic="Recent advances in CRISPR gene editing technology",
                expected_output="CRISPR-Cas9 has evolved with base editing, prime editing, and CRISPR-Cas13. Clinical trials for sickle cell disease (Casgevy) approved. Key concerns: off-target effects, ethical considerations, regulatory frameworks.",
            ),
        ]
        for gt in ground_truths:
            session.add(gt)

        session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    seed()
