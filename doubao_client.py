import os

import requests
import dotenv
from volcenginesdkarkruntime import Ark

dotenv.load_dotenv()


def build_contract_review_prompt(contract_content):
    """构建合同审阅的Prompt，让豆包成为专业法律助手"""
    prompt = f"""
    你现在是一名专业的合同法律及财税审阅助手，需要严格按照以下要求审阅合同内容并输出法律意见：
    
    ### 审阅要求
    1. 合法性：检查合同条款是否符合《民法典》《合同法》等相关法律法规，指出违法/违规条款；
    2. 完整性：检查合同必备要素（当事人、标的、数量、质量、价款、履行期限/地点/方式、违约责任、争议解决）是否齐全；
    3. 法律风险：识别合同中的潜在法律风险（如模糊条款、不公平格式条款、权责不清、争议解决方式不合理等）；
    4. 税务风险：识别合同中的潜在的税务风险（包括增值税、个人所得税、企业所得税等）；
    5. 财务风险：识别合同中的财务风险（包括付款结构与合同履约的匹配性、核算与报表业绩影响等）；
    4. 建议：针对发现的问题给出具体、可落地的修改建议；
    5. 结论：给出合同整体合评价（如“基本合规，需修改XX条款”“存在重大法律风险，建议重新拟定”）。

    ### 合同内容
    {contract_content}
    
    ### 输出格式要求
    1. 分模块输出：【合法性检查】【完整性检查】【法律风险点识别】【税务风险点识别】【财务风险点识别】【修改建议】【整体结论】；
    2. 对于重大风险（风险发生概率大于80%或风险发生后的损失金额大于50万元的）重点提示；
    2. 语言专业且易懂，避免过于晦涩的法律术语，若使用需解释；
    3. 针对每一个问题，明确指出对应的合同条款位置（如“第3条第2款”）；
    4. 建议具体，避免“完善条款”等模糊表述。
    """
    return prompt


def call_doubao_api(contract_content):

    api_key = os.getenv("ARK_API_KEY")
    base_url = os.getenv("ARK_API_URL")
    model = os.getenv("DOUBAO_MODEL")

    # 建立豆包链接
    client = Ark(
        base_url=base_url,
        api_key=api_key
    )

    """调用豆包API获取合同审阅意见"""
    prompt = build_contract_review_prompt(contract_content)

    # 让豆包返还内容
    try:
        print(f"✅ 豆包AI模型：{model}，开始处理合同文件")
        response = client.responses.create(
            model=model,
            input=[{
                "role":"user",
                "content":[{
                    "type":"input_text",
                    "text":prompt
                }]
            }],
            thinking={"type":"enabled"},
            temperature=0.7
        )

        # 按豆包API实际返回格式解析（以下为示例，需根据真实返回调整）
        result = response
        return result
    except requests.exceptions.RequestException as e:
        print(f"调用豆包API失败：{str(e)}")
        raise


# 程序测试
if __name__ == "__main__":
    import jira_client
    import attachment_processor

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

    issueKey = issues[1]["id"]
    print(f"{issueKey}")

    comments = jira_cli.get_issue_comments(issueKey)
    print(comments)

    attachmentKey = issues[1]["fields"]["attachment"][-1]["id"]
    print(f"{attachmentKey}")
    jira_response = jira_cli.get_issue_attachments(attachmentKey)
    print(f"{jira_response}, {type(jira_response)}")
    print(f"Content-Type: {jira_response.headers.get('Content-Type')}")  # 文件类型，如 image/png, application/pdf
    print(f"Content-Length: {jira_response.headers.get('Content-Length')}")  # 文件大小（字节）
    jira_attachment = attachment_processor.conver_docx_response_to_json(jira_response)
    print(jira_attachment)

    review_opinion = call_doubao_api(jira_attachment)
    print(review_opinion)
