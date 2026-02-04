from config import JIRA_CONFIG


def check_trigger_condition(comments):
    """检查评论中是否包含@指定字段，返回是否触发"""
    if not comments:
        return False

    # 遍历所有评论，只要有一条包含触发关键词就返回True
    try:
        comment_text = comments[-1]["body"]["content"][0]["content"][0]
        # 增加判断type是否为text，不为则跳过
        if JIRA_CONFIG["trigger_keyword"] in comment_text["text"]:
            print(f"检测到触发关键词，评论作者：{comments[-1]["author"]["displayName"]}，时间：{comments[-1]["updated"]}")
            return True
    except Exception as e:
        return False

# 程序测试
if __name__ == "__main__":
    import jira_client

    try:
        # 1. 初始化客户端（官方鉴权）
        jira_cli = jira_client.connect_jira()
        # 2. 获取目标ticket（官方POST/search）
        issues = jira_cli.get_target_issues()
        # 3. 验证结果
        if issues:
            print(f"✅ 测试成功！第一个ticket：{issues}")
        else:
            print("✅ 测试成功！无符合条件的ticket")
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")

    issueKey = issues[-1]["id"]
    print(f"{issueKey}")

    comments = jira_cli.get_issue_comments(issueKey)
    print(comments)

    judge = check_trigger_condition(comments)
    print(judge)
