# coding=utf-8
"""
新闻素材评分模块 - 小额贷款广告专用
基于三大黄金法则：受众广度 + 切身利益 + 理解简单
"""

from typing import Dict, List, Tuple
import re


class NewsScorer:
    """新闻适配度评分器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化评分器
        
        Args:
            config: 评分配置，包含各类关键词权重
        """
        self.config = config or {}
        self.min_score = self.config.get('min_score', 18)  # 最低可用分数
        
        # 受众广度关键词（10分）
        self.high_audience_keywords = [
            '工资', '薪资', '裁员', '失业', '待业', '找工作', '求职',
            '房租', '租金', '押金', '物价', '菜价', '猪肉', '鸡蛋', 
            '米面油', '生活成本', '油价', '水电费', '燃气费',
            '打工', '上班族', '年轻人', '90后', '00后',
        ]
        
        self.medium_audience_keywords = [
            '结婚', '彩礼', '婚礼', '份子钱', '红包',
            '过年', '春节', '年货', '人情', '礼金',
            '租房', '搬家', '换房', '车贷', '停车费', '保养',
        ]
        
        self.low_audience_keywords = [
            '创业', '副业', '摆摊', '小生意', '个体户', '小店',
            '兼职', '外卖', '跑腿', '开店',
        ]
        
        # 切身利益关键词（10分）
        self.direct_interest_keywords = [
            '拖欠', '延迟发放', '缩水', '下降', '欠薪',
            '裁员', '失业', '上涨', '涨价', '贵', '暴涨',
        ]
        
        self.indirect_interest_keywords = [
            '费用', '成本', '开销', '支出', '花费', '压力',
            '负担', '攀比', '焦虑', '不易', '艰难',
        ]
        
        self.policy_benefit_keywords = [
            '补贴', '贴息', '优惠', '减免', '发放', '申请',
            '消费券', '购物券', '惠民', '领取',
        ]
        
        # 易理解程度（10分） - 通过专业术语反向判断
        self.professional_terms = [
            'LPR', 'MLF', 'GDP', 'CPI', 'PMI', 'PPI',
            '利率', '汇率', '货币政策', '金融监管', '宏观经济',
            '央行', '货币', '政策调整', '经济指标',
        ]
        
        # 直接排除的关键词（0分，立即放弃）
        self.blacklist_keywords = [
            '富豪', '千万', '亿万', '豪宅', '豪车', '奢侈品',
            '明星', '网红', '直播', '娱乐', '八卦',
            '学费', '培训', '考证', '教育', '课程',
            '医院', '医保', '看病', '疾病', '癌症', '手术',
            '股票', '基金', '炒股', '投资理财', '虚拟货币', '比特币',
            '彩票', '赌博', '传销', '诈骗', '洗钱', '高利贷',
        ]
    
    def score_news(self, title: str) -> Tuple[int, Dict[str, int]]:
        """
        对新闻标题进行评分
        
        Args:
            title: 新闻标题
            
        Returns:
            (总分, 评分详情字典)
        """
        title_lower = title.lower()
        
        # 1. 黑名单检查（直接0分）
        for keyword in self.blacklist_keywords:
            if keyword.lower() in title_lower:
                return 0, {
                    '受众广度': 0,
                    '切身利益': 0,
                    '易理解度': 0,
                    '拒绝原因': f'包含禁用词: {keyword}'
                }
        
        # 2. 受众广度评分（0-10分）
        audience_score = self._score_audience(title_lower)
        
        # 3. 切身利益评分（0-10分）
        interest_score = self._score_interest(title_lower)
        
        # 4. 易理解度评分（0-10分）
        understanding_score = self._score_understanding(title_lower)
        
        total_score = audience_score + interest_score + understanding_score
        
        details = {
            '受众广度': audience_score,
            '切身利益': interest_score,
            '易理解度': understanding_score,
        }
        
        return total_score, details
    
    def _score_audience(self, title_lower: str) -> int:
        """评估受众广度（0-10分）"""
        # 高受众关键词：10分
        for keyword in self.high_audience_keywords:
            if keyword in title_lower:
                return 10
        
        # 中等受众关键词：7-8分
        medium_matches = sum(
            1 for keyword in self.medium_audience_keywords
            if keyword in title_lower
        )
        if medium_matches >= 2:
            return 8
        elif medium_matches == 1:
            return 7
        
        # 低受众关键词：5-6分
        low_matches = sum(
            1 for keyword in self.low_audience_keywords
            if keyword in title_lower
        )
        if low_matches >= 2:
            return 6
        elif low_matches == 1:
            return 5
        
        # 默认：4分（普通话题）
        return 4
    
    def _score_interest(self, title_lower: str) -> int:
        """评估切身利益（0-10分）"""
        # 直接利益关键词：10分
        for keyword in self.direct_interest_keywords:
            if keyword in title_lower:
                return 10
        
        # 间接利益关键词：6-7分
        indirect_matches = sum(
            1 for keyword in self.indirect_interest_keywords
            if keyword in title_lower
        )
        if indirect_matches >= 2:
            return 7
        elif indirect_matches == 1:
            return 6
        
        # 政策福利关键词：5分
        policy_matches = sum(
            1 for keyword in self.policy_benefit_keywords
            if keyword in title_lower
        )
        if policy_matches >= 1:
            return 5
        
        # 默认：3分
        return 3
    
    def _score_understanding(self, title_lower: str) -> int:
        """评估易理解程度（0-10分）"""
        # 检查专业术语数量（越多分数越低）
        professional_count = sum(
            1 for term in self.professional_terms
            if term.lower() in title_lower
        )
        
        if professional_count == 0:
            # 无专业术语：10分（易理解）
            return 10
        elif professional_count == 1:
            # 1个专业术语：6分（需要简单解释）
            return 6
        elif professional_count == 2:
            # 2个专业术语：4分（需要详细解释）
            return 4
        else:
            # 3个以上专业术语：2分（难以理解）
            return 2
    
    def get_rating_label(self, score: int) -> str:
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
    
    def get_usage_suggestion(self, score: int) -> str:
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
    
    def should_keep(self, score: int) -> bool:
        """判断是否应该保留该新闻"""
        return score >= self.min_score
    
    def filter_news_list(self, news_list: List[Dict]) -> List[Dict]:
        """
        批量过滤新闻列表
        
        Args:
            news_list: 新闻列表，每个元素包含 'title' 字段
            
        Returns:
            过滤后的新闻列表（包含评分信息）
        """
        filtered_list = []
        
        for news in news_list:
            title = news.get('title', '')
            if not title:
                continue
            
            score, details = self.score_news(title)
            
            if self.should_keep(score):
                news_with_score = news.copy()
                news_with_score['score'] = score
                news_with_score['score_details'] = details
                news_with_score['rating_label'] = self.get_rating_label(score)
                news_with_score['usage_suggestion'] = self.get_usage_suggestion(score)
                filtered_list.append(news_with_score)
        
        # 按评分降序排序
        filtered_list.sort(key=lambda x: x['score'], reverse=True)
        
        return filtered_list


# === 便捷函数 ===

def score_single_news(title: str, config: Dict = None) -> Tuple[int, Dict, str, str]:
    """
    为单条新闻评分（便捷函数）
    
    Args:
        title: 新闻标题
        config: 评分配置（可选）
        
    Returns:
        (总分, 评分详情, 评级标签, 使用建议)
    """
    scorer = NewsScorer(config)
    score, details = scorer.score_news(title)
    rating = scorer.get_rating_label(score)
    suggestion = scorer.get_usage_suggestion(score)
    
    return score, details, rating, suggestion


def batch_score_news(titles: List[str], config: Dict = None, min_score: int = 18) -> List[Dict]:
    """
    批量评分新闻（便捷函数）
    
    Args:
        titles: 新闻标题列表
        config: 评分配置（可选）
        min_score: 最低分数阈值
        
    Returns:
        评分结果列表（已按分数降序排序）
    """
    if config is None:
        config = {}
    config['min_score'] = min_score
    
    scorer = NewsScorer(config)
    news_list = [{'title': title} for title in titles]
    
    return scorer.filter_news_list(news_list)


# === 测试代码 ===

if __name__ == '__main__':
    print("=" * 60)
    print("新闻素材评分系统 - 测试")
    print("=" * 60)
    
    # 测试案例
    test_cases = [
        "多地房租价格上涨，年轻人租房压力大",
        "央行宣布下调LPR利率",
        "90后小伙靠摆摊月入过万",
        "某银行中介违规被查",
        "物价上涨，猪肉每斤超过30元",
        "国家出台小微企业税收优惠政策",
        "ChatGPT新功能发布",
        "明星结婚豪宅曝光",
        "多家公司宣布裁员计划",
        "春节临近，年货价格普遍上涨",
    ]
    
    scorer = NewsScorer({'min_score': 18})
    
    print("\n【评分结果】\n")
    for i, title in enumerate(test_cases, 1):
        score, details, rating, suggestion = score_single_news(title)
        
        print(f"{i}. {title}")
        print(f"   总分：{score}/30")
        print(f"   详情：受众{details['受众广度']}分 + 利益{details['切身利益']}分 + 理解{details['易理解度']}分")
        print(f"   评级：{rating}")
        print(f"   建议：{suggestion}")
        print()
    
    print("=" * 60)
    print(f"过滤标准：{scorer.min_score}分以上")
    print("=" * 60)

