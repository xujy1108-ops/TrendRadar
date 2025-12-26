#!/usr/bin/env python
# coding=utf-8
"""
AI 评分功能快速测试脚本
用于验证 API Key 配置和评分功能是否正常
"""

import os
import sys
from ai_scorer import AINewsScorer


def load_api_key():
    """加载 API Key（优先环境变量，其次配置文件）"""
    # 优先使用环境变量
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    if api_key:
        return api_key
    
    # 尝试从配置文件读取
    try:
        import yaml
        config_path = 'config/ai_config.yaml'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                api_key = config.get('api_key', '')
                if api_key:
                    return api_key
    except Exception as e:
        print(f"⚠️  读取配置文件失败: {e}")
    
    return None


def test_single_news():
    """测试单条新闻评分"""
    print("=" * 80)
    print("【AI评分功能测试】")
    print("=" * 80)
    
    # 检查 API Key
    api_key = load_api_key()
    if not api_key:
        print("\n❌ 未找到 API Key")
        print("\n请设置 API Key（两种方式任选一种）：")
        print("  方式1：环境变量")
        print("    export OPENROUTER_API_KEY='your-api-key'")
        print("  方式2：配置文件")
        print("    编辑 config/ai_config.yaml，填写 api_key")
        return False
    
    print(f"\n✅ API Key: {api_key[:20]}...")
    
    # 创建评分器
    print(f"\n初始化 AI 评分器...")
    scorer = AINewsScorer(
        api_key=api_key,
        model='openai/gpt-4o-mini'
    )
    print(f"✅ 使用模型: {scorer.model}")
    
    # 测试新闻
    test_news = "多地房租价格上涨，年轻人租房压力大"
    
    print(f"\n" + "=" * 80)
    print(f"【测试新闻】")
    print(f"  {test_news}")
    print("=" * 80)
    
    print(f"\n正在评分（需要5-10秒）...")
    result = scorer.score_news(test_news, verbose=True)
    
    if not result:
        print("\n❌ 评分失败！")
        print("\n可能的原因：")
        print("  1. API Key 无效")
        print("  2. 网络连接问题")
        print("  3. API 余额不足")
        return False
    
    # 显示结果
    print("\n" + "=" * 80)
    print("【评分结果】")
    print("=" * 80)
    print(f"\n📊 总分: {result['total_score']}/30")
    print(f"   ├─ 受众广度: {result['audience_score']}/10")
    print(f"   ├─ 切身利益: {result['interest_score']}/10")
    print(f"   └─ 易理解度: {result['simplicity_score']}/10")
    
    print(f"\n🤖 AI分析:")
    print(f"   {result['reason']}")
    
    print(f"\n💡 广告引子建议:")
    print(f"   {result['ad_direction']}")
    
    print(f"\n👥 目标受众:")
    print(f"   {result.get('target_audience', '未指定')}")
    
    print(f"\n😊 情感倾向:")
    print(f"   {result.get('emotion', 'neutral')}")
    
    # 评级
    if result['total_score'] >= 27:
        rating = '⭐⭐⭐⭐⭐ 完美'
        suggestion = '✅ 立即使用'
    elif result['total_score'] >= 23:
        rating = '⭐⭐⭐⭐ 优质'
        suggestion = '✅ 推荐使用'
    elif result['total_score'] >= 18:
        rating = '⭐⭐⭐ 一般'
        suggestion = '⚠️ 谨慎使用'
    else:
        rating = '⭐⭐ 勉强'
        suggestion = '⚠️ 需要改写'
    
    print(f"\n📈 评级: {rating}")
    print(f"💬 建议: {suggestion}")
    
    print("\n" + "=" * 80)
    print("✅ 测试成功！AI评分功能正常工作")
    print("=" * 80)
    
    return True


def test_batch_news():
    """测试批量评分"""
    print("\n\n" + "=" * 80)
    print("【批量评分测试】")
    print("=" * 80)
    
    api_key = load_api_key()
    if not api_key:
        print("\n⚠️  跳过批量测试（未找到API Key）")
        return False
    
    test_cases = [
        "多地房租价格上涨，年轻人租房压力大",
        "90后小伙靠摆摊月入过万",
        "央行宣布下调LPR利率"
    ]
    
    print(f"\n测试新闻数量: {len(test_cases)}条")
    print("=" * 80)
    
    scorer = AINewsScorer(api_key=api_key, model='openai/gpt-4o-mini')
    results = scorer.batch_score_news(test_cases, verbose=False, delay=0.5)
    
    if not results:
        print("\n❌ 批量评分失败")
        return False
    
    print(f"\n✅ 成功评分 {len(results)} 条新闻")
    print("\n【评分结果汇总】\n")
    
    for i, item in enumerate(results, 1):
        print(f"{i}. 【{item['ai_score']}分】{item['title']}")
        print(f"   {item['ai_reason'][:60]}...")
        print()
    
    print("=" * 80)
    print("✅ 批量评分测试成功")
    print("=" * 80)
    
    return True


def main():
    """主函数"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                     TrendRadar AI评分测试                         ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    # 测试单条评分
    success1 = test_single_news()
    
    if not success1:
        print("\n❌ 基础测试失败，请检查配置")
        sys.exit(1)
    
    # 询问是否继续批量测试
    print("\n是否继续批量评分测试？（需要更多时间和API调用）")
    choice = input("输入 y 继续，其他键跳过: ").lower()
    
    if choice == 'y':
        test_batch_news()
    else:
        print("\n跳过批量测试")
    
    print("\n" + "=" * 80)
    print("🎉 所有测试完成！")
    print("\n下一步：")
    print("  python batch_score.py output/xxx.txt --mode hybrid")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()

