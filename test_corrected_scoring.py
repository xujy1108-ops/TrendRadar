#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修正后的AI评分逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_scorer import AINewsScorer
from batch_score import load_ai_config

def main():
    print("\n" + "=" * 80)
    print("【修正后AI评分测试】")
    print("=" * 80)
    
    # 加载AI配置
    ai_config = load_ai_config()
    if not ai_config:
        print("❌ 无法加载AI配置")
        return
    
    # 初始化AI评分器
    scorer = AINewsScorer(
        api_key=ai_config.get('api_key'),
        model=ai_config.get('model', 'openai/gpt-4o-mini'),
        base_url=ai_config.get('base_url', 'https://openrouter.ai/api/v1')
    )
    
    # 重点测试和钱直接相关的新闻
    test_news = [
        # 应该高分的新闻（直接涉及钱）
        "部分银行上调存款利率",
        "多地房租价格上涨，年轻人租房压力大",
        "物价持续上涨，生活成本增加",
        "多地最低工资标准上调",
        "国家发放消费券刺激经济",
        
        # 中等分数（间接涉及钱）
        "稳经济关键在稳企业",
        "碧桂园开启\"二次创业\"",
        "普通人如何避免税务踩坑",
        
        # 应该低分的新闻（和钱无关）
        "马克龙访华把熊猫弄到手了",
        "《疯狂动物城2》何以沦为疯狂盗摄城"
    ]
    
    print(f"✅ 使用修正后的评分标准")
    print(f"📰 测试新闻数量: {len(test_news)}")
    print()
    
    results = []
    
    for i, title in enumerate(test_news, 1):
        print(f"[{i}/{len(test_news)}] 评分: {title}")
        
        try:
            result = scorer.score_news(title)
            if result:
                audience_score = result.get('audience_score', 0)
                interest_score = result.get('interest_score', 0)
                simplicity_score = result.get('simplicity_score', 0)
                total_score = result.get('total_score', 0)
                reason = result.get('reason', '无')
                ad_direction = result.get('ad_direction', '无')
                
                print(f"   📊 总分: {total_score}/30")
                print(f"   ├─ 受众广度: {audience_score}/10")
                print(f"   ├─ 利益直接性: {interest_score}/10")
                print(f"   └─ 理解简单度: {simplicity_score}/10")
                print(f"   🤖 分析: {reason}")
                print(f"   💡 引子: {ad_direction}")
                
                results.append({
                    'title': title,
                    'total_score': total_score,
                    'audience_score': audience_score,
                    'interest_score': interest_score,
                    'simplicity_score': simplicity_score,
                    'reason': reason
                })
            else:
                print("   ❌ 评分失败")
                
        except Exception as e:
            print(f"   ❌ 评分出错: {e}")
        
        print()
    
    # 分析结果
    print("=" * 80)
    print("【评分分析】")
    print("=" * 80)
    
    if results:
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        print("🏆 评分排行榜:")
        for i, r in enumerate(results, 1):
            score_color = "🟢" if r['total_score'] >= 20 else "🟡" if r['total_score'] >= 15 else "🔴"
            print(f"   {i:2d}. {score_color} {r['title']} ({r['total_score']}分)")
            print(f"       受众:{r['audience_score']} 利益:{r['interest_score']} 理解:{r['simplicity_score']}")
        
        # 验证修正效果
        deposit_rate_news = next((r for r in results if "存款利率" in r['title']), None)
        if deposit_rate_news:
            print(f"\n🎯 关键验证 - 存款利率新闻:")
            print(f"   总分: {deposit_rate_news['total_score']}/30")
            print(f"   利益直接性: {deposit_rate_news['interest_score']}/10")
            print(f"   分析: {deposit_rate_news['reason']}")
            
            if deposit_rate_news['interest_score'] >= 8:
                print("   ✅ 修正成功！现在正确识别了和钱的直接关联性")
            else:
                print("   ❌ 仍需进一步调整")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()


