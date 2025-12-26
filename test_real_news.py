#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试今天实际相关新闻的AI评分
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_scorer import AINewsScorer
from batch_score import load_ai_config

def main():
    print("\n" + "=" * 80)
    print("【今日相关新闻AI评分测试】")
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
    
    # 今天实际抓取到的相关新闻标题
    real_news = [
        # 金融相关
        "部分银行上调存款利率",
        "超千亿险资活水来了！险企投资股票风险因子再度下调",
        "金砖国家新开发银行在华发行30亿元人民币熊猫债",
        "日本长期利率升至历史高位",
        
        # 经济民生
        "稳经济关键在稳企业",
        "\"创新\"成为中国经济社会发展关键词",
        "普通人如何避免税务踩坑",
        
        # 企业财务
        "碧桂园开启\"二次创业\"",
        "碧桂园完成境内外债务重组，降债超 900 亿元",
        "税务部门公布陈震偷税案件细节",
        "网络车评人陈震偷税被查",
        
        # 投资理财
        "证监会：对市值管理、现金分红、股份回购等作出明确要求",
        "多路资金激烈博弈航天发展 3.28亿元资金抢筹航天科技",
        
        # 其他可能相关
        "赖清德要\"帮大陆解决经济问题\"，哪里来的自信？"
    ]
    
    print(f"✅ 使用模型: {ai_config.get('model')}")
    print(f"📰 测试新闻数量: {len(real_news)}")
    print()
    
    results = []
    
    for i, title in enumerate(real_news, 1):
        print(f"[{i}/{len(real_news)}] 评分: {title}")
        
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
                elif score >= 14:
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
        medium_score = [r for r in results if 14 <= r['score'] < 20]
        low_score = [r for r in results if r['score'] < 14]
        
        print(f"🏆 高分新闻 (≥20分): {len(high_score)} 条")
        for r in high_score:
            print(f"   • {r['title']} ({r['score']}分)")
        
        print(f"\n⚠️  中等新闻 (14-19分): {len(medium_score)} 条")
        for r in medium_score:
            print(f"   • {r['title']} ({r['score']}分)")
        
        print(f"\n❌ 低分新闻 (<14分): {len(low_score)} 条")
        for r in low_score:
            print(f"   • {r['title']} ({r['score']}分)")
        
        if high_score:
            print(f"\n🎯 最佳推荐: {high_score[0]['title']}")
            print(f"   💡 广告引子: {high_score[0]['ad_direction']}")
            print(f"   🤖 AI分析: {high_score[0]['reason']}")
        elif medium_score:
            print(f"\n🎯 备选推荐: {medium_score[0]['title']}")
            print(f"   💡 广告引子: {medium_score[0]['ad_direction']}")
            print(f"   🤖 AI分析: {medium_score[0]['reason']}")
        else:
            print("\n❌ 今日无高质量新闻，建议等待更好的时机")
        
        # 统计分析
        avg_score = sum(r['score'] for r in results) / len(results)
        print(f"\n📊 统计信息:")
        print(f"   • 平均分数: {avg_score:.1f}/30")
        print(f"   • 可用新闻: {len(high_score + medium_score)}/{len(results)} 条")
        print(f"   • 推荐使用率: {len(high_score)/len(results)*100:.1f}%")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()
