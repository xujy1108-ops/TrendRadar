#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对今天抓取的全部新闻进行AI评分
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_scorer import AINewsScorer
from batch_score import load_ai_config

def extract_titles_from_txt(txt_path):
    """从TXT文件中提取新闻标题"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败：{e}")
        return []
    
    titles = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行和平台标题行
        if not line or '|' in line and not line.startswith(('1.', '2.', '3.')):
            continue
        
        # 提取新闻标题（格式：数字. 标题 [URL:...]）
        match = re.match(r'\s*\d+\.\s*(.*?)\s*\[URL:', line)
        if match:
            title = match.group(1).strip()
            if title and len(title) > 5:  # 标题长度合理
                titles.append(title)
    
    return titles

def main():
    print("\n" + "=" * 80)
    print("【全部新闻AI评分测试】")
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
    
    # 读取今天的新闻文件
    txt_file = "output/2025年12月06日/txt/11时53分.txt"
    
    print(f"📁 读取文件: {txt_file}")
    titles = extract_titles_from_txt(txt_file)
    
    if not titles:
        print("❌ 未找到有效的新闻标题")
        return
    
    print(f"✅ 提取到 {len(titles)} 条新闻标题")
    print(f"🤖 使用模型: {ai_config.get('model')}")
    print()
    
    # 只评分前50条，避免API调用过多
    max_test = min(50, len(titles))
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
                
                # 只显示高分新闻的详细信息
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
            print("\n❌ 今日无高质量新闻，建议等待更好的时机")
        
        # 统计分析
        avg_score = sum(r['score'] for r in results) / len(results)
        usable_news = len(high_score + medium_score)
        
        print(f"\n📊 统计信息:")
        print(f"   • 测试新闻: {len(results)}/{len(titles)} 条")
        print(f"   • 平均分数: {avg_score:.1f}/30")
        print(f"   • 可用新闻: {usable_news}/{len(results)} 条")
        print(f"   • 推荐使用率: {len(high_score)/len(results)*100:.1f}%")
        print(f"   • 可考虑率: {usable_news/len(results)*100:.1f}%")
        
        # 如果想测试更多新闻
        if len(titles) > max_test:
            print(f"\n💡 提示: 还有 {len(titles) - max_test} 条新闻未测试")
            print("   如需测试更多，可以修改 max_test 参数")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()


