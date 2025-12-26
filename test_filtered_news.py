#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对筛选后的新闻进行AI评分
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_scorer import AINewsScorer
from batch_score import load_ai_config

def extract_filtered_news_from_html(html_path):
    """从HTML报告中提取筛选后的新闻标题"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取HTML文件失败：{e}")
        return []
    
    titles = []
    
    # 查找新闻项目
    # HTML中的新闻格式类似：<div class="news-title">标题</div>
    title_pattern = r'<div class="news-title"[^>]*>(.*?)</div>'
    matches = re.findall(title_pattern, content, re.DOTALL)
    
    for match in matches:
        # 清理HTML标签
        title = re.sub(r'<[^>]+>', '', match).strip()
        if title and len(title) > 5:
            titles.append(title)
    
    # 如果上面的方法没找到，尝试其他模式
    if not titles:
        # 尝试查找其他可能的新闻标题格式
        patterns = [
            r'<h3[^>]*>(.*?)</h3>',
            r'<span class="title"[^>]*>(.*?)</span>',
            r'<a[^>]*title="([^"]+)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                title = re.sub(r'<[^>]+>', '', match).strip()
                if title and len(title) > 5:
                    titles.append(title)
    
    # 去重
    titles = list(dict.fromkeys(titles))
    return titles

def main():
    print("\n" + "=" * 80)
    print("【筛选后新闻AI评分测试】")
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
    
    # 读取筛选后的新闻
    html_file = "output/2025年12月06日/html/当日汇总.html"
    
    print(f"📁 读取文件: {html_file}")
    titles = extract_filtered_news_from_html(html_file)
    
    if not titles:
        print("❌ 未找到筛选后的新闻标题，尝试手动提取...")
        # 手动提取一些已知的相关新闻进行测试
        titles = [
            "部分银行上调存款利率",
            "碧桂园开启\"二次创业\"",
            "稳经济关键在稳企业",
            "创业板指2连涨收复60日线",
            "物价持续上涨，生活成本增加"
        ]
        print(f"📰 使用测试新闻: {len(titles)} 条")
    else:
        print(f"✅ 提取到 {len(titles)} 条筛选后的新闻标题")
    
    print(f"🤖 使用模型: {ai_config.get('model')}")
    print()
    
    # 限制测试数量以节省成本
    max_test = min(20, len(titles))
    if len(titles) > max_test:
        print(f"⚠️  为节省成本，只评分前 {max_test} 条新闻")
        print()
    
    results = []
    
    for i, title in enumerate(titles[:max_test], 1):
        print(f"[{i}/{max_test}] 评分: {title}")
        
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
                
                # 显示评分结果
                if score >= 14:
                    print(f"   📊 总分: {score}/30 - {rating}")
                    print(f"   🤖 分析: {reason}")
                    print(f"   💡 引子: {ad_direction}")
                else:
                    print(f"   📊 总分: {score}/30 - {rating}")
                
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
        
        # 显示最佳推荐
        if high_score:
            print(f"\n🎯 最佳推荐: {high_score[0]['title']}")
            print(f"   💡 广告引子: {high_score[0]['ad_direction']}")
            print(f"   🤖 AI分析: {high_score[0]['reason']}")
        elif medium_score:
            print(f"\n🎯 备选推荐: {medium_score[0]['title']}")
            print(f"   💡 广告引子: {medium_score[0]['ad_direction']}")
            print(f"   🤖 AI分析: {medium_score[0]['reason']}")
        else:
            print("\n❌ 筛选后的新闻质量仍然较低")
        
        # 统计分析
        avg_score = sum(r['score'] for r in results) / len(results)
        usable_news = len(high_score + medium_score)
        
        print(f"\n📊 筛选效果统计:")
        print(f"   • 关键词筛选: 从 445 条缩减到 46 条 (筛选率: 89.7%)")
        print(f"   • AI评分测试: {len(results)} 条")
        print(f"   • 平均分数: {avg_score:.1f}/30")
        print(f"   • 可用新闻: {usable_news}/{len(results)} 条")
        print(f"   • 推荐使用率: {len(high_score)/len(results)*100:.1f}%")
        print(f"   • 可考虑率: {usable_news/len(results)*100:.1f}%")
        
        print(f"\n🎯 双重筛选效果:")
        print(f"   • 原始新闻: 445 条")
        print(f"   • 关键词筛选后: 46 条 (10.3%)")
        print(f"   • AI高质量新闻: {len(high_score)} 条")
        print(f"   • 最终可用率: {len(high_score)/445*100:.2f}%")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()


