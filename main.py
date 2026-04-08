# 利用大语言模型（LLM）的零样本（Zero-Shot）能力,快速实现一个基础版的职位分类器

import os
from dotenv import load_dotenv
import openai
from openai import OpenAI, RateLimitError, APIError
import time

# 加载环境变量 (如果你使用 .env 文件存储 API Key)
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)


def create_prompt_v1(job_description: str) -> str:
    """
    读取模板文件并生成一个完整的 prompt。

    Args:
        job_description: 清洗后的职位描述文本。

    Returns:
        一个准备好发送给 LLM 的完整 prompt 字符串。
    """
    with open("prompts/classification_prompt_v1.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    return prompt_template.format(job_description=job_description)


# 定义一个新的 prompt 创建函数
def create_prompt_v2(job_description: str) -> str:
    with open("prompts/classification_prompt_v2.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()
    return prompt_template.format(job_description=job_description)


def classify_with_llm(prompt: str, max_retries: int) -> str:
    """
    调用 OpenAI API 进行分类。

    Args:
        prompt: 包含任务描述和职位信息的完整 prompt。

    Returns:
        LLM 返回的分类结果，或在出错时返回错误信息。
    """
    for i in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="qwen/qwen3.6-plus:free",
                # model="xiaomi/mimo-v2-pro",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                extra_body={"reasoning": {"enabled": True}},
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            # 如果报错速率限制，等待时间随重试次数增加 (2s, 4s, 8s...)
            wait_time = (2**i) + 1
            print(f"速率受限，等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
        except Exception as e:
            return f"Error: {str(e)}"
    return "Error: 达到最大重试次数"


# 添加提出非结构化数据

import json  # 确保在文件顶部导入 json 库


def create_extraction_prompt(job_description: str) -> str:
    """
    读取技能提取模板并生成一个完整的 prompt。
    """
    with open("prompts/extraction_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    return prompt_template.format(job_description=job_description)


def extract_skills_with_llm(job_description: str) -> list:
    """
    调用LLM提取技能，并安全地解析JSON输出。

    Args:
        job_description: 清洗后的职位描述文本。

    Returns:
        一个包含提取出的技能的列表 (list)，如果解析失败或未找到则为空列表。
    """
    if not isinstance(job_description, str) or not job_description.strip():
        return []  # 处理空文本的边缘情况

    # 1. 创建 Prompt
    prompt = create_extraction_prompt(job_description)

    try:
        # 2. 调用 OpenAI API
        response = client.chat.completions.create(
            model="qwen/qwen3-coder:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            extra_body={"reasoning": {"enabled": True}},
        )

        # 3. 提取并解析返回的字符串
        llm_output_string = response.choices[0].message.content.strip()

        # 尝试将字符串解析为 Python 列表
        extracted_skills = json.loads(llm_output_string)

        # 确保返回的是一个列表
        if isinstance(extracted_skills, list):
            return extracted_skills
        else:
            print(f"警告: LLM返回了非列表的JSON格式。内容: {llm_output_string}")
            return []

    except json.JSONDecodeError:
        print(f"警告: LLM返回了非法的JSON格式，无法解析。内容: {llm_output_string}")
        return []  # 如果LLM没有遵循指令返回标准JSON，则返回空列表
    except Exception as e:
        print(f"发生未知错误: {e}")
        return []  # 在其他任何错误情况下，也返回空列表
