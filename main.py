import jira_client
import schedule
import time
from datetime import datetime
from trigger_checker import check_trigger_condition
from attachment_processor import convert_response_to_json
from doubao_client import call_doubao_api
from config import DOUBAO_CONFIG


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
            attachment_key = issue["fields"]["attachment"][0]["id"]
            jira_attachment = jira.get_issue_attachments(attachment_key)
            attachment = convert_response_to_json(jira_attachment)
            print(attachment)
        except Exception as e:
            print(f"{issue_key}附件处理失败：{str(e)}")
            continue

        # 5. 调取豆包获取合同审阅意见
        try:
            doubao_output = call_doubao_api(attachment)
            print(doubao_output)

            # 记录豆包API使用ID
            doubao_id = doubao_output.id

            # 获取使用信息
            doubao_usage = doubao_output.usage
            total_tokens = getattr(doubao_usage, "total_tokens")
            print(f"本次调用ID为: {doubao_id}, 总消耗tokens: {total_tokens}")

            # 获取豆包回复意见
            doubao_resp = doubao_output.output
            doubao_data = doubao_resp[1].content[0].text
            print(doubao_data)

            # 拼接输出内容
            doubao_to_jira = (f"{doubao_data}\n\n"
                              f"本次调用的AI模型为{DOUBAO_CONFIG['ai_model']}, AI回复ID为{doubao_id}, AI Token消耗为{total_tokens}。")

            # 将回复放入jira
            jira.add_comment_to_issue(issue_key=issue_key, comment_content=doubao_to_jira)

        except Exception as e:
            print(f"{issue_key}调用豆包API失败：{str(e)}")
            continue


def task_with_time_check():
    """
    带时间段检查的包装任务：先判断时间，再执行核心业务
    """
    now = datetime.now()
    current_hour = now.hour

    # 定义运行时间段
    start_hour = 9
    end_hour = 19

    # 时间判断
    if start_hour <= current_hour <= end_hour:
        main()


# 主程序测试
if __name__ == "__main__":
    # 配置任务执行间隔
    task_interval = 5
    schedule.every(task_interval).minutes.do(task_with_time_check)

    print("程序已启动，将在每天9:00-19:00内按固定间隔运行（按Ctrl+C停止）...")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n程序已被手动停止")