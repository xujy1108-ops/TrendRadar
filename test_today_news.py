#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试今天实际新闻的AI评分
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_scorer import AINewsScorer
from batch_score import load_ai_config

def main():
    print("\n" + "=" * 80)
    print("【今日新闻AI评分测试】")
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
    
    # 今天的相关新闻标题
    test_news = [
        "碧桂园开启\"二次创业\"",
        "创业板指2连涨收复60日线",
        "部分银行上调存款利率",
        "美一机器人公司欠中国代工厂25亿元",
        "女子跑外卖15个月出版12万字小说",
        "少拿500可休10天员工称很开心",
        "普通人如何避免税务踩坑",
        "陈震偷逃税被罚缴247.48万",
        "中国人保集团副总裁于泽被查"
    ]
    
    print(f"✅ 使用模型: {ai_config.get('model')}")
    print(f"📰 测试新闻数量: {len(test_news)}")
    print()
    
    results = []
    
    for i, title in enumerate(test_news, 1):
        print(f"[{i}/{len(test_news)}] 评分: {title}")
        
        try:
            result = scorer.score_news(title)
            if result:
                score = result.get('total_score', 0)
                reason = result.get('reason', '无')
                ad_direction = result.get('ad_direction', '无')
                emotion = result.get('emotion', 'neutral')
                
                # 评级
                if score >= 25:
                    rating = "⭐⭐⭐⭐⭐ 完美"
                    suggestion = "✅ 立即使用"
                elif score >= 20:
                    rating = "⭐⭐⭐⭐ 优秀"
                    suggestion = "✅ 推荐使用"
                elif score >= 15:
                    rating = "⭐⭐⭐ 良好"
                    suggestion = "⚠️ 可以考虑"
                elif score >= 10:
                    rating = "⭐⭐ 一般"
                    suggestion = "❌ 不建议"
                else:
                    rating = "⭐ 较差"
                    suggestion = "❌ 不适用"
                
                print(f"   📊 总分: {score}/30")
                print(f"   📈 评级: {rating}")
                print(f"   💬 建议: {suggestion}")
                print(f"   🤖 分析: {reason}")
                print(f"   💡 引子: {ad_direction}")
                print(f"   😊 情感: {emotion}")
                
                results.append({
                    'title': title,
                    'score': score,
                    'rating': rating,
                    'suggestion': suggestion,
                    'reason': reason,
                    'ad_direction': ad_direction,
                    'emotion': emotion
                })
            else:
                print("   ❌ 评分失败")
                
        except Exception as e:
            print(f"   ❌ 评分出错: {e}")
        
        print()
    
    # 汇总结果
    print("=" * 80)
    print("【评分汇总】")
    print("=" * 80)
    
    if results:
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        high_score = [r for r in results if r['score'] >= 20]
        medium_score = [r for r in results if 15 <= r['score'] < 20]
        low_score = [r for r in results if r['score'] < 15]
        
        print(f"🏆 高分新闻 (≥20分): {len(high_score)} 条")
        for r in high_score:
            print(f"   • {r['title']} ({r['score']}分)")
        
        print(f"\n⚠️  中等新闻 (15-19分): {len(medium_score)} 条")
        for r in medium_score:
            print(f"   • {r['title']} ({r['score']}分)")
        
        print(f"\n❌ 低分新闻 (<15分): {len(low_score)} 条")
        for r in low_score:
            print(f"   • {r['title']} ({r['score']}分)")
        
        if high_score:
            print(f"\n🎯 推荐使用: {high_score[0]['title']}")
            print(f"   💡 广告引子: {high_score[0]['ad_direction']}")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()
