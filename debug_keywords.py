#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试关键词配置和匹配逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import load_frequency_words, matches_word_groups

def main():
    print("\n" + "=" * 80)
    print("【关键词配置调试】")
    print("=" * 80)
    
    # 1. 检查关键词文件加载
    try:
        word_groups, filter_words = load_frequency_words()
        print(f"✅ 成功加载关键词配置")
        print(f"📊 词组数量: {len(word_groups)}")
        print(f"🚫 过滤词数量: {len(filter_words)}")
        print()
        
        # 显示前几个词组
        print("📋 词组详情:")
        for i, group in enumerate(word_groups[:5], 1):
            print(f"   {i}. 词组: {group.get('group_key', 'N/A')}")
            print(f"      必须词: {group.get('required', [])}")
            print(f"      普通词: {group.get('normal', [])}")
            print(f"      最大数量: {group.get('max_count', 0)}")
            print()
        
        if len(word_groups) > 5:
            print(f"   ... 还有 {len(word_groups) - 5} 个词组")
            print()
        
        print(f"🚫 过滤词列表: {filter_words[:10]}{'...' if len(filter_words) > 10 else ''}")
        print()
        
    except Exception as e:
        print(f"❌ 关键词加载失败: {e}")
        return
    
    # 2. 测试关键词匹配
    print("=" * 80)
    print("【关键词匹配测试】")
    print("=" * 80)
    
    # 测试新闻标题
    test_titles = [
        "部分银行上调存款利率",
        "物价持续上涨，生活成本增加", 
        "多地房租价格上涨，年轻人租房压力大",
        "马克龙访华把熊猫弄到手了",
        "《疯狂动物城2》何以沦为疯狂盗摄城",
        "碧桂园开启\"二次创业\"",
        "普通人如何避免税务踩坑",
        "稳经济关键在稳企业",
        "创业板指2连涨收复60日线",
        "女子跑外卖15个月出版12万字小说"
    ]
    
    matched_count = 0
    
    for title in test_titles:
        is_match = matches_word_groups(title, word_groups, filter_words)
        status = "✅ 匹配" if is_match else "❌ 不匹配"
        print(f"{status}: {title}")
        
        if is_match:
            matched_count += 1
            # 找出匹配的词组
            for group in word_groups:
                title_lower = title.lower()
                
                # 检查必须词
                required_match = True
                if group["required"]:
                    required_match = all(
                        req_word.lower() in title_lower 
                        for req_word in group["required"]
                    )
                
                # 检查普通词
                normal_match = True
                if group["normal"]:
                    normal_match = any(
                        normal_word.lower() in title_lower 
                        for normal_word in group["normal"]
                    )
                
                if required_match and normal_match:
                    print(f"   └─ 匹配词组: {group['group_key']}")
                    if group["required"]:
                        print(f"      必须词: {group['required']}")
                    if group["normal"]:
                        matched_words = [w for w in group["normal"] if w.lower() in title_lower]
                        print(f"      匹配的普通词: {matched_words}")
                    break
    
    print()
    print(f"📊 匹配统计: {matched_count}/{len(test_titles)} 条新闻匹配关键词")
    print(f"📈 匹配率: {matched_count/len(test_titles)*100:.1f}%")
    
    # 3. 如果匹配率很低，给出建议
    if matched_count == 0:
        print("\n⚠️  警告: 没有新闻匹配关键词！")
        print("可能的原因:")
        print("1. 关键词配置过于严格")
        print("2. 关键词与实际新闻内容不匹配")
        print("3. 关键词文件格式有问题")
        print("\n💡 建议:")
        print("1. 检查 config/frequency_words.txt 文件内容")
        print("2. 适当放宽关键词条件")
        print("3. 添加更多相关关键词")
    elif matched_count < len(test_titles) * 0.3:
        print(f"\n⚠️  警告: 匹配率较低 ({matched_count/len(test_titles)*100:.1f}%)")
        print("建议适当调整关键词配置以提高匹配率")
    else:
        print(f"\n✅ 匹配率正常 ({matched_count/len(test_titles)*100:.1f}%)")
    
    print("\n✅ 调试完成！")

if __name__ == "__main__":
    main()


