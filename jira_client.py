import sys
import os
import requests
import base64
import urllib.parse  # 🆕 保留：URL编码JQL
from requests.auth import HTTPBasicAuth
from config import JIRA_CONFIG

# 1. 打印环境信息
print('Python %s on %s' % (sys.version, sys.platform))

# 2. 扩展项目内utils目录
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.join(current_dir, "utils")
sys.path.extend([utils_dir])
print(f"✅ 已加载团队工具目录：{utils_dir}")


# 基于原生requests的JIRA客户端（切换到API v2，修复410 Gone）
class SimpleJiraClient:
    def __init__(self):
        """初始化JIRA客户端，优化鉴权逻辑"""
        self.base_url = JIRA_CONFIG["server"]
        # 基础鉴权（备用）
        self.auth = HTTPBasicAuth(JIRA_CONFIG["username"], JIRA_CONFIG["api_token"])
        # 优先使用Base64编码的Authorization头
        auth_string = f"{JIRA_CONFIG['username']}:{JIRA_CONFIG['api_token']}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_base64}"
        }

    def get_current_user(self):
        """验证JIRA连接（优先使用headers鉴权）"""
        # 🔧 修改：API路径从v3改为v2
        # 原代码：url = f"{self.base_url}/rest/api/3/myself"
        url = f"{self.base_url}/rest/api/2/myself"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            user_data = response.json()
            print(f"✅ Jira连接成功！当前用户：{user_data['displayName']} (ID: {user_data['accountId']})")
            return True
        except requests.exceptions.RequestException as e:
            # 备用方案：使用HTTPBasicAuth重试
            try:
                response = requests.get(url, auth=self.auth, headers=self.headers, timeout=10)
                response.raise_for_status()
                user_data = response.json()
                print(f"✅ Jira连接成功（备用鉴权）！当前用户：{user_data['displayName']}")
                return True
            except Exception as e2:
                raise Exception(f"Jira API请求失败：{str(e2)}")

    def get_target_issues(self):
        """获取指定project和issue type的所有ticket（切换到API v2，修复410 Gone）"""
        # 1. 构造JQL查询语句
        jql = f'spaceJira = "{JIRA_CONFIG['project_key']}" AND worktype = {JIRA_CONFIG["issue_type"]} AND (createdDate >= startOfWeek() AND createdDate <= endOfWeek())'
        # 2. URL编码JQL（解决特殊字符/空格问题）
        encoded_jql = urllib.parse.quote(jql)
        # 🔧 修改：API路径从v3改为v2（核心修复410 Gone）
        # 原代码：url = f"{self.base_url}/rest/api/3/search?jql={encoded_jql}&maxResults=100"
        url = f"{self.base_url}/rest/api/3/search?jql={encoded_jql}&maxResults=100"

        try:
            # 使用GET请求（已验证v2接口支持）
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            issues = result.get("issues", [])
            print(f"✅ 获取到{len(issues)}个目标ticket（{JIRA_CONFIG['project_key']}/{JIRA_CONFIG['issue_type']}）")
            return issues
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取ticket失败：{str(e)} | 请检查JQL：{jql}")

    def get_issue_comments(self, issue_key):
        """获取指定ticket的所有评论"""
        # 🔧 修改：API路径从v3改为v2
        # 原代码：url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result.get("comments", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取{issue_key}评论失败：{str(e)}")

    def get_issue_attachments(self, issue_key):
        """获取指定ticket的所有附件"""
        # 🔧 修改：API路径从v3改为v2
        # 原代码：url = f"{self.base_url}/rest/api/3/issue/{issue_key}?fields=attachment"
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}?fields=attachment"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result.get("fields", {}).get("attachment", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取{issue_key}附件失败：{str(e)}")

    def download_attachment(self, attachment_content_url):
        """下载附件二进制内容"""
        try:
            response = requests.get(attachment_content_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise Exception(f"下载附件失败：{str(e)}")

    def add_comment_to_issue(self, issue_key, comment_content):
        """回写评论到ticket"""
        # 🔧 修改：API路径从v3改为v2
        # 原代码：url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
        payload = {
            "body": comment_content
        }
        try:
            # 评论接口支持POST，无需修改
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            print(f"✅ 法律意见已回写到{issue_key}的评论中")
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"回写评论失败：{str(e)}")


# 对外统一的初始化方法
def connect_jira():
    """创建并验证JIRA客户端连接"""
    try:
        jira_client = SimpleJiraClient()
        jira_client.get_current_user()
        return jira_client
    except Exception as e:
        print(f"❌ JIRA连接失败：{str(e)}")
        raise


# 测试代码
if __name__ == "__main__":
    try:
        jira_client = connect_jira()
        issues = jira_client.get_target_issues()
        if issues:
            print(f"✅ 测试成功！第一个ticket：{issues[0]['key']}")
        else:
            print("✅ 测试成功！无符合条件的ticket")
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")