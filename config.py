import os
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# JIRA配置
JIRA_CONFIG = {
    "server": os.getenv("JIRA_SERVER"),  # 如https://your-jira.atlassian.net
    "username": os.getenv("JIRA_USERNAME"),
    "api_token": os.getenv("JIRA_API_TOKEN"),
    "project_key": os.getenv("JIRA_PROJECT_KEY"),  # 你指定的板块key
    "issue_type": os.getenv("JIRA_ISSUE_TYPE"),    # 你指定的ticket类型
    "trigger_keyword": "@FIN-lawhelper"         # 触发的@字段
}

# 豆包API配置（需替换为官方有效地址）
DOUBAO_CONFIG = {
    "api_url": os.getenv("ARK_API_URL"),
    "api_key": os.getenv("ARK_API_KEY"),
    "ai_model": os.getenv("doubao_model")
}

# 配置附件下载地址
ATTACHMENT_CONFIG = {
    "save_path": os.getenv("attachment_save_path", "./downloads")
}

# 支持的附件格式
SUPPORTED_FILE_TYPES = [".pdf", ".docx", ".doc"]