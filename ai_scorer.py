# coding=utf-8
"""
AI 深度评分模块 - 基于大模型的智能评分
支持 OpenRouter API，可访问多种模型
"""

import json
import requests
from typing import Dict, Optional, Tuple
import time


class AINewsScorer:
    """
    AI 深度评分器
    基于大模型的语义理解进行智能评分
    """
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini", base_url: str = "https://openrouter.ai/api/v1"):
        """
        初始化 AI 评分器
        
        Args:
            api_key: OpenRouter API Key
            model: 模型名称，推荐：
                   - openai/gpt-4o-mini (快速，便宜，推荐)
                   - anthropic/claude-3.5-sonnet (最准确)
                   - meta-llama/llama-3.1-8b-instruct:free (免费)
            base_url: API 地址
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = 30
        
        # 评分 Prompt 模板
        self.scoring_prompt = """你是小额贷款广告专家，需要评估新闻是否适合用于抖音口播号的贷款广告脚本。

【评分标准】三个维度，每个0-10分：

1. 受众广度（10分）
   - 10分：90%以上的人相关（如：物价上涨、房租上涨、工资拖欠、裁员失业）
   - 8分：70-90%的人相关（如：结婚彩礼、过年开销、搬家费用）
   - 6分：50-70%的人相关（如：创业、副业、摆摊）
   - 4分：30-50%的人相关（行业特定话题）
   - 2分：10-30%的人相关（小众群体话题）
   - 0分：只有极少数人关心（如：富豪、明星、奢侈品）

2. 利益直接性（10分）
   - 10分：直接涉及钱的收支（如：工资、存款利率、房租、物价、补贴）
   - 8分：明显的资金需求场景（如：买房、结婚、创业、搬家、医疗）
   - 6分：可能产生资金需求（如：副业机会、投资理财、消费升级）
   - 4分：间接影响个人财务（如：政策调整、经济形势）
   - 2分：需要思考才能关联到钱（如：行业数据、宏观指标）
   - 0分：和钱无关（如：娱乐八卦、体育赛事）

3. 理解简单度（10分）
   - 10分：一听就懂，无需解释（如：物价涨了、房租贵了、工资少了）
   - 8分：稍微想想就能懂（如：消费贷贴息、补贴发放）
   - 6分：需要简单解释（如：利率调整）
   - 4分：需要详细解释（如：金融监管政策）
   - 2分：有专业术语（如：LPR、MLF）
   - 0分：需要专业知识（如：复杂金融概念）

【注意事项】
- 必须严格按照评分标准打分
- 受众广度：重点看覆盖人群比例
- 利益直接性：重点看是否直接涉及"钱"（不是缺钱，而是和钱相关）
- 理解简单度：重点看是否需要解释背景知识

【新闻标题】
{title}

【输出格式】
请严格按照以下JSON格式输出，不要有任何其他文字：
{{
    "audience_score": <0-10的整数>,
    "interest_score": <0-10的整数>,
    "simplicity_score": <0-10的整数>,
    "total_score": <0-30的整数>,
    "reason": "<100字以内的评分理由，说明为什么这样打分>",
    "ad_direction": "<30字以内的广告引子建议>",
    "target_audience": "<目标受众描述，20字以内>",
    "emotion": "<positive或negative或neutral>"
}}"""
    
    def score_news(self, title: str, verbose: bool = False) -> Optional[Dict]:
        """
        对单条新闻进行 AI 评分
        
        Args:
            title: 新闻标题
            verbose: 是否显示详细信息
            
        Returns:
            评分结果字典，失败返回 None
        """
        try:
            # 构建请求
            prompt = self.scoring_prompt.format(title=title)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # 降低温度以获得更稳定的输出
                "max_tokens": 500
            }
            
            if verbose:
                print(f"  🤖 调用 AI 模型: {self.model}")
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                print(f"  ❌ API 请求失败: {response.status_code}")
                if verbose:
                    print(f"  错误信息: {response.text}")
                return None
            
            # 解析响应
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # 尝试提取 JSON（有些模型可能在 JSON 前后加文字）
            if '```json' in content:
                # 提取 JSON 代码块
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content
            
            # 解析 JSON
            score_data = json.loads(json_str)
            
            # 验证数据完整性
            required_fields = ['audience_score', 'interest_score', 'simplicity_score', 
                             'total_score', 'reason', 'ad_direction']
            for field in required_fields:
                if field not in score_data:
                    print(f"  ⚠️  缺少字段: {field}")
                    return None
            
            # 验证分数范围
            if not (0 <= score_data['audience_score'] <= 10):
                score_data['audience_score'] = max(0, min(10, score_data['audience_score']))
            if not (0 <= score_data['interest_score'] <= 10):
                score_data['interest_score'] = max(0, min(10, score_data['interest_score']))
            if not (0 <= score_data['simplicity_score'] <= 10):
                score_data['simplicity_score'] = max(0, min(10, score_data['simplicity_score']))
            
            # 重新计算总分（防止模型计算错误）
            score_data['total_score'] = (
                score_data['audience_score'] + 
                score_data['interest_score'] + 
                score_data['simplicity_score']
            )
            
            return score_data
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON 解析失败: {e}")
            if verbose:
                print(f"  原始内容: {content}")
            return None
        except requests.exceptions.Timeout:
            print(f"  ❌ 请求超时（>{self.timeout}秒）")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 网络请求失败: {e}")
            return None
        except Exception as e:
            print(f"  ❌ 未知错误: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return None
    
    def batch_score_news(self, titles: list, verbose: bool = False, delay: float = 0.5) -> list:
        """
        批量评分新闻
        
        Args:
            titles: 新闻标题列表
            verbose: 是否显示详细信息
            delay: 每次请求间隔（秒），避免请求过快
            
        Returns:
            评分结果列表
        """
        results = []
        total = len(titles)
        
        for i, title in enumerate(titles, 1):
            if verbose:
                print(f"\n[{i}/{total}] 评分中: {title[:50]}...")
            
            score_data = self.score_news(title, verbose=verbose)
            
            if score_data:
                results.append({
                    'title': title,
                    'ai_score': score_data['total_score'],
                    'ai_details': {
                        '受众广度': score_data['audience_score'],
                        '切身利益': score_data['interest_score'],
                        '易理解度': score_data['simplicity_score']
                    },
                    'ai_reason': score_data['reason'],
                    'ad_direction': score_data.get('ad_direction', ''),
                    'target_audience': score_data.get('target_audience', ''),
                    'emotion': score_data.get('emotion', 'neutral')
                })
                
                if verbose:
                    print(f"  ✅ AI评分: {score_data['total_score']}/30")
            else:
                print(f"  ⚠️  评分失败，跳过")
            
            # 延迟以避免请求过快
            if i < total:
                time.sleep(delay)
        
        return results


def test_ai_scorer():
    """测试 AI 评分器"""
    print("=" * 80)
    print("AI 评分器测试")
    print("=" * 80)
    
    # 从环境变量或配置文件读取 API Key
    import os
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    
    if not api_key:
        print("\n⚠️  未设置 OPENROUTER_API_KEY 环境变量")
        print("请先设置：export OPENROUTER_API_KEY='your-api-key'")
        return
    
    # 测试案例
    test_cases = [
        "多地房租价格上涨，年轻人租房压力大",
        "央行宣布下调LPR利率",
        "90后小伙靠摆摊月入过万",
        "某银行中介违规被查",
        "物价上涨，猪肉每斤超过30元",
    ]
    
    # 创建评分器
    scorer = AINewsScorer(api_key=api_key, model="openai/gpt-4o-mini")
    
    print(f"\n使用模型: {scorer.model}")
    print("=" * 80)
    
    # 批量评分
    results = scorer.batch_score_news(test_cases, verbose=True)
    
    print("\n" + "=" * 80)
    print(f"【评分结果汇总】")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   AI评分: {result['ai_score']}/30")
        print(f"   详情: 受众{result['ai_details']['受众广度']} + "
              f"利益{result['ai_details']['切身利益']} + "
              f"理解{result['ai_details']['易理解度']}")
        print(f"   理由: {result['ai_reason']}")
        print(f"   建议: {result['ad_direction']}")


if __name__ == '__main__':
    test_ai_scorer()

