import io
import os
import json
from docx import Document

def conver_docx_response_to_json(response):
    # 0. 判断是否为docx文档
    content_type = response.headers.get("Content-Type","")
    DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOC_MIME = "application/msword"

    if DOCX_MIME in content_type:
        print("确认文件类型: Word (.docx)，开始解析...")
    elif DOC_MIME in content_type:
        print("检测到旧版 .doc 格式文件，请转换为 .docx 格式文件上传")
        return False
    else:
        print(f"附件格式为：{content_type}，程序不支持。请上传 .docx 格式文件！")
        return False


    # 1. 将二进制流放入内存文件对象
    doc_file = io.BytesIO(response.content)

    # 2. 加载文档
    doc = Document(doc_file)
    full_content = {
        "title": "Jira Attachment Content",
        "paragraphs": [],
        "tables": []
    }

    # 3. 提取段落文字
    for para in doc.paragraphs:
        if para.text.strip():
            full_content["paragraphs"].append(para.text.strip())

    # 4. 提取表格信息
    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_content = [cell.text.strip() for cell in row.cells]
            table_data.append(row_content)
        full_content["tables"].append(table_data)

    # 5. 转换为JSON格式
    return json.dumps(full_content, ensure_ascii=False, indent=2)


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

    issueKey = issues[1]["id"]
    print(f"{issueKey}")

    comments = jira_cli.get_issue_comments(issueKey)
    print(comments)

    attachmentKey = issues[1]["fields"]["attachment"][-1]["id"]
    print(f"{attachmentKey}")
    jira_respones = jira_cli.get_issue_attachments(attachmentKey)
    print(f"{jira_respones}, {type(jira_respones)}")
    print(f"Content-Type: {jira_respones.headers.get('Content-Type')}")  # 文件类型，如 image/png, application/pdf
    print(f"Content-Length: {jira_respones.headers.get('Content-Length')}")  # 文件大小（字节）
    jira_attachment = conver_docx_response_to_json(jira_respones)
    print(jira_attachment)
