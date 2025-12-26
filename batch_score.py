#!/usr/bin/env python
# coding=utf-8
"""
批量评分TXT文件中的新闻
适用于TrendRadar项目输出的新闻文件

支持三种评分模式：
- keyword: 仅关键词评分（快速，免费）
- ai: 仅AI评分（准确，有成本）
- hybrid: 混合模式（推荐，关键词粗筛 + AI精评）
"""

import sys
import os
import re
import yaml
from pathlib import Path
from news_scorer import batch_score_news, NewsScorer
from ai_scorer import AINewsScorer


def get_rating_label(score: int) -> str:
    """获取评分等级标签"""
    if score >= 27:
        return '⭐⭐⭐⭐⭐ 完美'
    elif score >= 23:
        return '⭐⭐⭐⭐ 优质'
    elif score >= 18:
        return '⭐⭐⭐ 一般'
    elif score >= 12:
        return '⭐⭐ 勉强'
    else:
        return '⭐ 不推荐'


def get_usage_suggestion(score: int) -> str:
    """获取使用建议"""
    if score >= 27:
        return '✅ 立即使用'
    elif score >= 23:
        return '✅ 推荐使用'
    elif score >= 18:
        return '⚠️ 谨慎使用'
    elif score >= 12:
        return '⚠️ 需要改写'
    else:
        return '❌ 直接放弃'


def load_ai_config():
    """加载 AI 配置"""
    config_path = Path('config/ai_config.yaml')
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 优先使用环境变量
        api_key = os.environ.get('OPENROUTER_API_KEY', config.get('api_key', ''))
        
        if api_key:
            config['api_key'] = api_key
        
        return config
    except Exception as e:
        print(f"⚠️  配置文件加载失败: {e}")
        return None


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
        
        # 跳过空行和分隔线
        if not line or line.startswith('━') or line.startswith('='):
            continue
        
        # 跳过标题行
        if any(keyword in line for keyword in ['热点词汇统计', '更新时间', '本次新增', '共', '条']):
            continue
        
        # 跳过emoji开头的分类行
        if line.startswith(('📊', '🔥', '📈', '📌', '🆕')):
            continue
        
        # 提取新闻标题（格式：1. [平台] 🆕 标题 [排名] - 时间 (次数)）
        # 使用正则匹配
        match = re.match(r'\s*\d+\.\s*\[.*?\]\s*(?:🆕\s*)?(.*?)\s*\[', line)
        if match:
            title = match.group(1).strip()
            if title and len(title) > 5:  # 标题长度合理
                titles.append(title)
    
    return titles


def score_txt_file(txt_path, min_score=18, output_json=False, mode='keyword', ai_config=None):
    """
    评分TXT文件中的新闻
    
    Args:
        txt_path: TXT文件路径
        min_score: 最低分数阈值
        output_json: 是否输出JSON文件
        mode: 评分模式 (keyword/ai/hybrid)
        ai_config: AI配置字典
    """
    print("\n" + "=" * 80)
    print(f"【新闻评分系统】")
    print("=" * 80)
    print(f"文件路径：{txt_path}")
    print(f"评分模式：{mode}")
    if mode == 'keyword':
        print(f"  └─ 仅关键词评分（快速，免费）")
    elif mode == 'ai':
        print(f"  └─ 仅AI评分（准确，有成本）")
    elif mode == 'hybrid':
        print(f"  └─ 混合模式（关键词粗筛 + AI精评，推荐）⭐")
    print(f"最低分数：{min_score}分")
    print("=" * 80)
    
    # 检查文件是否存在
    if not Path(txt_path).exists():
        print(f"❌ 文件不存在：{txt_path}")
        return
    
    # 提取标题
    print("\n[1/3] 提取新闻标题...")
    titles = extract_titles_from_txt(txt_path)
    
    if not titles:
        print("❌ 未找到有效的新闻标题")
        print("\n提示：请确保文件是TrendRadar输出的新闻报告格式")
        return
    
    print(f"✅ 共找到 {len(titles)} 条新闻标题")
    
    # 根据模式选择评分方法
    if mode == 'keyword':
        # 仅关键词评分
        print(f"\n[2/3] 关键词评分中（过滤 {min_score}分以下）...")
        results = batch_score_news(titles, min_score=min_score)
        
    elif mode == 'ai':
        # 仅AI评分
        if not ai_config or not ai_config.get('api_key'):
            print(f"\n❌ AI模式需要配置 API Key")
            print(f"   请设置环境变量：export OPENROUTER_API_KEY='your-key'")
            print(f"   或在 config/ai_config.yaml 中配置")
            return
        
        print(f"\n[2/3] AI评分中...")
        ai_scorer = AINewsScorer(
            api_key=ai_config['api_key'],
            model=ai_config.get('model', 'openai/gpt-4o-mini'),
            base_url=ai_config.get('base_url', 'https://openrouter.ai/api/v1')
        )
        
        ai_results = ai_scorer.batch_score_news(
            titles, 
            verbose=ai_config.get('verbose', False),
            delay=ai_config.get('batch_delay', 0.5)
        )
        
        # 转换为统一格式
        results = []
        for item in ai_results:
            if item['ai_score'] >= min_score:
                results.append({
                    'title': item['title'],
                    'score': item['ai_score'],
                    'score_details': item['ai_details'],
                    'rating_label': get_rating_label(item['ai_score']),
                    'usage_suggestion': get_usage_suggestion(item['ai_score']),
                    'ai_reason': item.get('ai_reason', ''),
                    'ad_direction': item.get('ad_direction', ''),
                })
        
    elif mode == 'hybrid':
        # 混合模式：关键词粗筛 + AI精评
        if not ai_config or not ai_config.get('api_key'):
            print(f"\n❌ 混合模式需要配置 API Key")
            print(f"   请设置环境变量：export OPENROUTER_API_KEY='your-key'")
            print(f"   或在 config/ai_config.yaml 中配置")
            return
        
        # 第一步：关键词粗筛
        keyword_threshold = ai_config.get('keyword_threshold', 12)
        print(f"\n[2/4] 关键词粗筛中（阈值 {keyword_threshold}分）...")
        keyword_results = batch_score_news(titles, min_score=keyword_threshold)
        
        if not keyword_results:
            print(f"  ⚠️  没有新闻通过关键词粗筛（{keyword_threshold}分）")
            results = []
        else:
            print(f"  ✅ {len(keyword_results)} 条新闻通过粗筛")
            
            # 第二步：AI精评
            print(f"\n[3/4] AI精评中...")
            ai_scorer = AINewsScorer(
                api_key=ai_config['api_key'],
                model=ai_config.get('model', 'openai/gpt-4o-mini'),
                base_url=ai_config.get('base_url', 'https://openrouter.ai/api/v1')
            )
            
            filtered_titles = [item['title'] for item in keyword_results]
            ai_results = ai_scorer.batch_score_news(
                filtered_titles,
                verbose=ai_config.get('verbose', False),
                delay=ai_config.get('batch_delay', 0.5)
            )
            
            # 第三步：综合评分
            print(f"\n[4/4] 综合评分中...")
            weights = ai_config.get('hybrid_weights', {'keyword_weight': 0.3, 'ai_weight': 0.7})
            kw_weight = weights['keyword_weight']
            ai_weight = weights['ai_weight']
            
            # 建立标题到关键词评分的映射
            kw_scores = {item['title']: item['score'] for item in keyword_results}
            
            results = []
            for ai_item in ai_results:
                title = ai_item['title']
                kw_score = kw_scores.get(title, 0)
                ai_score = ai_item['ai_score']
                
                # 计算综合评分
                final_score = int(kw_score * kw_weight + ai_score * ai_weight)
                
                if final_score >= min_score:
                    results.append({
                        'title': title,
                        'score': final_score,
                        'keyword_score': kw_score,
                        'ai_score': ai_score,
                        'score_details': ai_item['ai_details'],
                        'rating_label': get_rating_label(final_score),
                        'usage_suggestion': get_usage_suggestion(final_score),
                        'ai_reason': ai_item.get('ai_reason', ''),
                        'ad_direction': ai_item.get('ad_direction', ''),
                    })
            
            # 按最终评分排序
            results.sort(key=lambda x: x['score'], reverse=True)
    
    else:
        print(f"\n❌ 不支持的模式: {mode}")
        print(f"   支持的模式: keyword, ai, hybrid")
        return
    
    if not results:
        print(f"\n❌ 没有新闻达到 {min_score} 分以上")
        print(f"\n建议：")
        print(f"  1. 降低分数标准（如改为 15分）")
        print(f"  2. 检查关键词配置是否过于严格")
        return
    
    # 显示结果
    print(f"✅ 共 {len(results)} 条新闻达标（已按分数降序排列）")
    
    print("\n[3/3] 评分结果：")
    print("\n" + "=" * 80)
    
    # 统计各分数段
    perfect = sum(1 for r in results if r['score'] >= 27)
    excellent = sum(1 for r in results if 23 <= r['score'] < 27)
    good = sum(1 for r in results if 18 <= r['score'] < 23)
    
    print(f"【评分统计】")
    print(f"  ⭐⭐⭐⭐⭐ 完美（27-30分）：{perfect}条")
    print(f"  ⭐⭐⭐⭐   优质（23-26分）：{excellent}条")
    print(f"  ⭐⭐⭐     一般（18-22分）：{good}条")
    print("=" * 80)
    
    # 详细结果
    for i, news in enumerate(results, 1):
        score = news['score']
        details = news['score_details']
        rating = news['rating_label']
        suggestion = news['usage_suggestion']
        title = news['title']
        
        print(f"\n{i}. 【{score}分】{title}")
        
        # 显示评分详情
        if mode == 'hybrid':
            kw_score = news.get('keyword_score', 0)
            ai_score = news.get('ai_score', 0)
            print(f"   综合评分：关键词{kw_score}分 + AI{ai_score}分 = {score}分")
        
        print(f"   评分详情：受众广度{details['受众广度']}分 + 切身利益{details['切身利益']}分 + 易理解度{details['易理解度']}分")
        print(f"   评级：{rating}")
        print(f"   建议：{suggestion}")
        
        # 显示AI分析（ai和hybrid模式）
        if mode in ['ai', 'hybrid']:
            if 'ai_reason' in news and news['ai_reason']:
                print(f"   🤖 AI分析：{news['ai_reason']}")
            if 'ad_direction' in news and news['ad_direction']:
                print(f"   💡 广告引子：{news['ad_direction']}")
    
    print("\n" + "=" * 80)
    print(f"【使用建议】")
    if perfect > 0:
        print(f"  ✅ 优先使用 {perfect} 条完美素材（27分以上）")
    if excellent > 0:
        print(f"  ✅ 推荐使用 {excellent} 条优质素材（23-26分）")
    if good > 0:
        print(f"  ⚠️  谨慎使用 {good} 条一般素材（18-22分）")
    print("=" * 80)
    
    # 输出JSON（可选）
    if output_json:
        import json
        output_path = txt_path.replace('.txt', '_scored.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 评分结果已保存到：{output_path}")


def find_latest_txt():
    """查找最新的输出TXT文件"""
    output_dir = Path('output')
    if not output_dir.exists():
        return None
    
    # 找到最新的日期文件夹
    date_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()], reverse=True)
    if not date_dirs:
        return None
    
    latest_date = date_dirs[0]
    txt_dir = latest_date / 'txt'
    if not txt_dir.exists():
        return None
    
    # 找到最新的TXT文件
    txt_files = sorted(txt_dir.glob('*.txt'), reverse=True)
    if not txt_files:
        return None
    
    return str(txt_files[0])


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 尝试自动查找最新文件
        latest_txt = find_latest_txt()
        if latest_txt:
            print(f"未指定文件，使用最新文件：{latest_txt}")
            score_txt_file(latest_txt, min_score=18, mode='keyword')
        else:
            print("=" * 80)
            print("【用法说明】")
            print("=" * 80)
            print("python batch_score.py <txt文件路径> [选项]")
            print("\n参数说明：")
            print("  txt文件路径     必需，TrendRadar输出的新闻TXT文件")
            print("  --mode <模式>   可选，评分模式：keyword(默认)/ai/hybrid")
            print("  --score <分数>  可选，最低分数，默认18分（范围：0-30）")
            print("  --json          可选，同时输出JSON格式结果")
            print("\n评分模式：")
            print("  keyword  关键词评分（快速，免费）")
            print("  ai       AI深度评分（准确，有成本）")
            print("  hybrid   混合模式（推荐，关键词粗筛+AI精评）⭐")
            print("\n示例：")
            print("  # 关键词评分（默认）")
            print("  python batch_score.py output/2025年12月06日/txt/10时30分.txt")
            print("\n  # AI评分")
            print("  python batch_score.py output/2025年12月06日/txt/10时30分.txt --mode ai")
            print("\n  # 混合模式（推荐）⭐")
            print("  python batch_score.py output/2025年12月06日/txt/10时30分.txt --mode hybrid")
            print("\n  # 设置更高标准（25分）")
            print("  python batch_score.py output/2025年12月06日/txt/10时30分.txt --score 25 --mode hybrid")
            print("\n  # 输出JSON文件")
            print("  python batch_score.py output/2025年12月06日/txt/10时30分.txt --mode hybrid --json")
            print("\n环境变量：")
            print("  OPENROUTER_API_KEY  OpenRouter API Key（AI模式必需）")
            print("=" * 80)
        return
    
    txt_path = sys.argv[1]
    min_score = 18
    output_json = False
    mode = 'keyword'
    
    # 解析参数
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--json':
            output_json = True
            i += 1
        elif arg == '--mode':
            if i + 1 < len(sys.argv):
                mode = sys.argv[i + 1]
                if mode not in ['keyword', 'ai', 'hybrid']:
                    print(f"⚠️  不支持的模式: {mode}，已重置为 keyword")
                    mode = 'keyword'
                i += 2
            else:
                print(f"⚠️  --mode 需要指定模式参数")
                i += 1
        elif arg == '--score':
            if i + 1 < len(sys.argv) and sys.argv[i + 1].isdigit():
                min_score = int(sys.argv[i + 1])
                if min_score < 0 or min_score > 30:
                    print(f"⚠️  分数范围应在0-30之间，已重置为18")
                    min_score = 18
                i += 2
            else:
                print(f"⚠️  --score 需要指定分数参数")
                i += 1
        elif arg.isdigit():
            # 兼容旧版本参数格式
            min_score = int(arg)
            if min_score < 0 or min_score > 30:
                print(f"⚠️  分数范围应在0-30之间，已重置为18")
                min_score = 18
            i += 1
        else:
            print(f"⚠️  未知参数: {arg}")
            i += 1
    
    # 加载AI配置
    ai_config = None
    if mode in ['ai', 'hybrid']:
        ai_config = load_ai_config()
        if not ai_config:
            print("\n⚠️  未找到 AI 配置文件: config/ai_config.yaml")
            print("   尝试从环境变量读取 API Key...")
            api_key = os.environ.get('OPENROUTER_API_KEY', '')
            if api_key:
                ai_config = {
                    'api_key': api_key,
                    'model': 'openai/gpt-4o-mini',
                    'base_url': 'https://openrouter.ai/api/v1',
                    'batch_delay': 0.5,
                    'keyword_threshold': 12,
                    'hybrid_weights': {'keyword_weight': 0.3, 'ai_weight': 0.7},
                    'verbose': False
                }
                print("   ✅ 成功从环境变量读取 API Key")
            else:
                print("   ❌ 未设置 OPENROUTER_API_KEY 环境变量")
                print("   请设置：export OPENROUTER_API_KEY='your-key'")
                return
    
    score_txt_file(txt_path, min_score, output_json, mode, ai_config)


if __name__ == '__main__':
    main()

