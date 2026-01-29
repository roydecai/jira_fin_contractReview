import doubao_client
import jira_client
from trigger_checker import check_trigger_condition
from attachment_processor import conver_docx_response_to_json
from doubao_client import call_doubao_api

def main():
    # 1. 连接JIRA
    jira = jira_client.connect_jira()

    # 2. 获取目标ticket列报
    issues = jira.get_target_issues()

    for issue in issues:
        issue_key = issue["id"]
        issue_simpName = issue["key"]
        print(f"\n处理ticket：{issue_simpName}")

        # 3. 检查触发条件
        comments = jira.get_issue_comments(issue_key)
        if not check_trigger_condition(comments):
            print(f"{issue_simpName}未触发审阅条件，跳过")
            continue

        # 4. 获取并读取最新附件
        try:
            attachment_key = issues[1]["fields"]["attachment"][-1]["id"]
            jira_attachment = jira.get_issue_attachments(attachment_key)
            attachment = conver_docx_response_to_json(jira_attachment)
            print(attachment)
        except Exception as e:
            print(f"{issue_key}附件处理失败：{str(e)}")
            continue

        # 5. 调取豆包获取合同审阅意见
        try:
            doubao_output = call_doubao_api(attachment)
            print(doubao_output)
            review_opinion = doubao_output["output"][1]["content"][0]["text"]
            print(review_opinion)

        except Exception as e:
            print(f"{issue_key}调用豆包API失败：{str(e)}")
            continue









# 主程序测试
if __name__ == "__main__":
    main()