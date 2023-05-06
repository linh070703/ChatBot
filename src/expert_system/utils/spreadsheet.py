import os
import sys

sys.path.append("/home/thaiminhpv/Workspace/Code/FUNiX-ChatGPT-Hackathon/Chatbot/Chatbot/")

from typing import Literal, Dict, List, Tuple, Union, Any, Optional
import pandas as pd
import logging
from src.expert_system.utils.calculator import format_vnd

def calculate_economical_table(
        income: float,
        target_money: Optional[float],
        target_time: Optional[int]
    ) -> Tuple[Dict[str, float], str]:
    """
    Calculate economical table.
    
    Args:
        income (float): Income.
        target_money (float): Target money.
        target_time (int): Target time.
        
    Returns:
        answer (Dict[str, float]): Answer.
        economical_table (str): Economical table in markdown format.
    """
    df = _calculate_economical_table(income, target_money, target_time)
    
    if target_money and target_time:
        logging.warning(f"Both target money and target time are extracted from model output")

    table = df.set_index("Số năm")
    # bold column "Tổng lượng tiết kiệm"
    table["Tổng lượng tiết kiệm"] = table["Tổng lượng tiết kiệm"].apply(lambda x: f"**{x}**")
    # bold last row
    table.iloc[-1] = table.iloc[-1].apply(lambda x: f"**{x}**")
    # remove duplicate bold
    table = table.apply(lambda x: x.str.replace(r"\*\*\*\*", r"**"), axis=1)
    table = table.to_markdown()

    if target_money:
        # get last row
        last_row = df.iloc[-1]
        time = last_row["Số năm"]
        return {
            'time': time,
        }, table
            
    
    if target_time:
        # get last row
        last_row = df.iloc[-1]
        money = last_row["Tổng lượng tiết kiệm"]
        return {
            'money': money,
        }, table
        
    

def _calculate_economical_table(
        income: float,
        target_money: Optional[float],
        target_time: Optional[int]
    ) -> pd.DataFrame:
    """
    Calculate economical table.
    
    Args:
        income (float): Income.
        target_money (float): Target money.
        target_time (int): Target time.
        
    Returns:
        economical_table (pd.DataFrame): Economical table.
    """
    # Số năm | Thu nhập  | %  tiết kiệm mỗi tháng | Lượng tiết kiệm mỗi năm | Tổng lượng tiết kiệm  | Lãi suất tiết kiệm của ngân hàng
    # 1|    5,000,000.00|   10.00%  |  500,000.00|   6,000,000.00|  480,000.00
    # 2|    5,250,000.00|   10.00%  |  525,000.00|   12,780,000.00|  1,022,400.00
    # n|    (income at n-1) * 1.05 |   10.00%  |  Thu nhập * 10.00% |   previous Tổng lượng tiết kiệm + this Lượng tiết kiệm mỗi năm * 12 + previous Lãi suất tiết kiệm của ngân hàng|  this Tổng lượng tiết kiệm * 0.08

    rows = []
    if target_time:
        for i in range(1, target_time + 1):
            if i == 1:
                rows.append([i, income, "10%", income * 0.1, income * 0.1 * 12, income * 0.1 * 12 * 0.08])
            else:
                previous_row = rows[-1]
                previous_income = previous_row[1]
                previous_target_saving = previous_row[4]
                previous_target_interest = previous_row[5]
                this_target_saving = previous_target_saving + previous_income * 1.05 * 0.1 * 12 + previous_target_interest
                rows.append([i, previous_income * 1.05, "10%", previous_income * 1.05 * 0.1, this_target_saving, this_target_saving * 0.08])
    elif target_money:
        for i in range(1, 100):
            if i == 1:
                rows.append([i, income, "10%", income * 0.1, income * 0.1 * 12, income * 0.1 * 12 * 0.08])
            else:
                previous_row = rows[-1]
                previous_income = previous_row[1]
                previous_target_saving = previous_row[4]
                previous_target_interest = previous_row[5]
                this_target_saving = previous_target_saving + previous_income * 1.05 * 0.1 * 12 + previous_target_interest
                rows.append([i, previous_income * 1.05, "10%", previous_income * 1.05 * 0.1, this_target_saving, this_target_saving * 0.08])
                if this_target_saving >= target_money:
                    break
    
    economical_table = pd.DataFrame(rows, columns=["Số năm", "Thu nhập", "% tiết kiệm mỗi tháng", "Lượng tiết kiệm mỗi năm", "Tổng lượng tiết kiệm", "Lãi suất tiết kiệm của ngân hàng"])
    economical_table["Thu nhập"] = economical_table["Thu nhập"].apply(format_vnd)
    economical_table["Lượng tiết kiệm mỗi năm"] = economical_table["Lượng tiết kiệm mỗi năm"].apply(format_vnd)
    economical_table["Tổng lượng tiết kiệm"] = economical_table["Tổng lượng tiết kiệm"].apply(format_vnd)
    economical_table["Lãi suất tiết kiệm của ngân hàng"] = economical_table["Lãi suất tiết kiệm của ngân hàng"].apply(format_vnd)
    return economical_table

if __name__ == "__main__":
    income = 5000000
    target_money = 3e9
    target_time = None
    answer, economical_table = calculate_economical_table(income, target_money, target_time)
    print(answer)
    print(economical_table)