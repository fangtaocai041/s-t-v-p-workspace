"""
Example: Automated Literature Review

This example demonstrates how Porpoise Agent conducts a literature review
on Yangtze finless porpoise passive acoustic monitoring.

Usage:
    python examples/literature_review.py
"""

import asyncio
import logging

from src.agent.orchestrator import Orchestrator
from src.agent.loop import PorpoiseLoop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run a literature review example"""
    
    # Initialize the orchestrator
    orchestrator = Orchestrator()
    
    # Research question
    question = (
        "检索近5年(2020-2024)关于长江江豚(Neophocaena asiaeorientalis)"
        "被动声学监测(PAM)的文献，重点关注click检测和丰度估计方法"
    )
    
    logger.info(f"Starting literature review: {question}")
    
    # Run the orchestrator
    result = await orchestrator.run(question)
    
    logger.info(f"Result: {result}")
    return result


if __name__ == "__main__":
    asyncio.run(main())
