"""
Example: Acoustic Data Analysis

This example demonstrates the NBHF click detection pipeline
for Yangtze finless porpoise PAM data.

Usage:
    python examples/acoustic_analysis.py --input data/sample.wav
"""

import argparse
import asyncio
import logging

from src.agent.orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main(input_file: str):
    """Run acoustic analysis on a PAM recording"""
    
    orchestrator = Orchestrator()
    
    question = (
        f"分析PAM录音文件 {input_file} 中的江豚声信号。"
        "检测NBHF click脉冲，提取click train，识别buzz事件，"
        "并生成声学行为分析报告。"
    )
    
    logger.info(f"Starting acoustic analysis: {input_file}")
    
    result = await orchestrator.run(question)
    
    logger.info(f"Analysis complete: {result}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Porpoise Agent - Acoustic Analysis"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to PAM recording (.wav/.flac)"
    )
    args = parser.parse_args()
    asyncio.run(main(args.input))
