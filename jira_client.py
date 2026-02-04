import json
import sys
import os
import requests
from requests.auth import HTTPBasicAuth  # 🔧 保留：官方推荐的鉴权方式
from config import JIRA_CONFIG

# 1. 打印环境信息（团队排查用）
print('Python %s on %s' % (sys.version, sys.platform))

# 2. 扩展项目内utils目录（团队托管规范）
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.join(current_dir, "utils")
sys.path.extend([utils_dir])
print(f"✅ 已加载团队工具目录：{utils_dir}")

# 基于JIRA官方REST API v3规范实现的客户端（回归官方标准）
class SimpleJiraClient:
    def __init__(self):
        """初始化客户端（严格遵循官方鉴权规范）"""
        self.base_url = JIRA_CONFIG["server"]
        # 使用官方推荐的HTTP Basic Auth（移除手动Base64编码）
        self.auth = HTTPBasicAuth(JIRA_CONFIG["username"], JIRA_CONFIG["api_token"])
        # 仅保留官方要求的headers（移除冗余Authorization）
        self.headers = {
            "Accept": "application/json",          # 官方要求：指定返回JSON
            "Content-Type": "application/json"     # 官方要求：POST请求必须设置
        }

    def get_current_user(self):
        """验证JIRA连接（官方/myself接口）"""
        url = f"{self.base_url}/rest/api/3/myself"
        try:
            # 使用官方鉴权方式（auth参数），移除冗余headers鉴权
            response = requests.get(
                url=url,
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()  # 抛出HTTP错误（官方推荐）
            user_data = response.json()
            print(f"✅ Jira连接成功！当前用户：{user_data['displayName']} (ID: {user_data['accountId']})")
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jira API请求失败：{str(e)} | 请检查邮箱/API Token是否正确")

    def get_target_issues(self):
        """获取指定项目/类型的ticket（严格遵循官方/search接口规范）"""
        # 1. 官方标准的search-post接口URL
        url = f"{self.base_url}/rest/api/3/search/jql"

        # 2. 构造jql
        jql = (f'spaceJira = "{JIRA_CONFIG["project_key"]}" AND worktype = {JIRA_CONFIG["issue_type"]}'
               f' AND (updatedDate >= startOfMonth()) AND status = "Pre Authorize"'
               f' AND attachments IS NOT EMPTY')

        # 2. 构造官方要求的POST payload（JSON格式）
        payload = json.dumps({
            "fields": ["id","attachment"],
            "fieldsByKeys": True,
            "jql": jql,
            "maxResults": 200
        })

        try:
            # 使用POST请求
            response = requests.request(
                "POST",
                url=url,
                auth=self.auth,
                headers=self.headers,
                data=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            issues = result.get("issues", [])
            print(f"✅ 获取到{len(issues)}个目标ticket（{JIRA_CONFIG['project_key']}/{JIRA_CONFIG['issue_type']}）")
            return issues
        except requests.exceptions.RequestException as e:
            error_detail = f"获取ticket失败：{str(e)} | JQL：{jql}"
            # 补充官方文档提示
            error_detail += "\n💡 官方文档参考：https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-post"
            raise Exception(error_detail)

    def get_issue_comments(self, issue_key):
        """获取ticket评论（官方/comment接口）"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        try:
            response = requests.request(
                "GET",
                url=url,
                auth=self.auth,
                headers=self.headers,
                timeout=20
            )
            response.raise_for_status()
            result = response.json()
            return result.get("comments", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取{issue_key}评论失败：{str(e)} | 官方文档：https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get")

    def get_issue_attachments(self, attachment_key):
        """获取ticket附件（官方/issue接口）"""
        url = f"{self.base_url}/rest/api/3/attachment/content/{attachment_key}"
        try:
            response = requests.request(
                "GET",
                url=url,
                auth=self.auth,
                allow_redirects=True,
                timeout=20
            )
            response.raise_for_status()
            # 返回附件本身，待根据格式处理
            result = response
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取{attachment_key}附件失败：{str(e)} | 官方文档：https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get")

    def add_comment_to_issue(self, issue_key, comment_content):
        """回写评论（官方/comment POST接口）"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        payload = json.dumps({
            "body": {
                "content": [
                    {
                        "content": [
                            {
                                "text": comment_content,
                                "type": "text"
                            }
                        ],
                        "type": "paragraph"
                    }
                ],
                "type": "doc",
                "version": 1
            }
        })
        try:
            response = requests.request(
                "POST",
                url=url,
                auth=self.auth,
                headers=self.headers,
                data=payload,
                timeout=30
            )
            response.raise_for_status()
            print(f"✅ 法律意见已回写到{issue_key}的评论中")
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"回写评论失败：{str(e)} | 官方文档：https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post")

# 对外统一的初始化方法（保持兼容）
def connect_jira():
    """创建并验证JIRA客户端连接"""
    try:
        jira_client = SimpleJiraClient()
        jira_client.get_current_user()
        return jira_client
    except Exception as e:
        print(f"❌ JIRA连接失败：{str(e)}")
        raise

# 测试代码（按官方规范验证）
if __name__ == "__main__":
    try:
        # 1. 初始化客户端（官方鉴权）
        jira_client = connect_jira()
        # 2. 获取目标ticket（官方POST/search）
        issues = jira_client.get_target_issues()
        # 3. 验证结果
        if issues:
            print(f"✅ 测试成功！第一个ticket：{issues}")
        else:
            print("✅ 测试成功！无符合条件的ticket")
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")

    issueKey = issues[1]["id"]
    print(f"{issueKey}")

    comments = jira_client.get_issue_comments(issueKey)
    print(comments)
    print(f"{comments[-1]["body"]["content"][0]["content"]}")
    for comment in comments[-1]["body"]["content"][0]["content"]:
        print(comment)

    attachmentKey = issues[1]["fields"]["attachment"][-1]["id"]
    print(f"{attachmentKey}")

    issueAttachement = jira_client.get_issue_attachments(attachmentKey)
    print(f"{issueAttachement}, {type(issueAttachement)}")
    print(f"Content-Type: {issueAttachement.headers.get('Content-Type')}")  # 文件类型，如 image/png, application/pdf
    print(f"Content-Length: {issueAttachement.headers.get('Content-Length')}")  # 文件大小（字节）

    '''
    commentContent = "FIN jira AI law helper test."
    jira_client.add_comment_to_issue(issueKey, commentContent)
    '''