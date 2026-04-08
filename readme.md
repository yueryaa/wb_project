# LLM驱动的招聘信息分析器

这是一个利用大型语言模型（LLM）对招聘信息（Job Descriptions）进行自动化分析的项目。项目通过迭代式提示词工程（Prompt Engineering），实现了对职位的高精度业务职能分类和关键AI技能提取。

## 核心功能

-   **业务职能分类**:
    -   利用Zero-Shot Prompt快速建立分类基线。
    -   通过分析错误案例，迭代到Few-Shot Prompt，显著提升分类准确率。
    -   最终分类体系包括："Engineering, Data & AI ", "IT & Security", "Product & Design", "Marketing & Sales","Corporate & Ops","Education & Research ","others"。

-   **AI技能提取**:
    -   从非结构化的职位描述文本中，根据预定义的技能清单提取关键技能。
    -   要求并解析LLM返回的JSON格式数据，确保输出的稳定性和机器可读性。

## 技术栈

-   **核心语言**: Python 3.10.20
-   **数据处理**: Pandas 2.3.3
-   **LLM API**: openrouter (qwen/qwen3.6-plus:free)
-   **开发环境**: Jupyter Notebook
-   **辅助工具**: Tqdm, BeautifulSoup4, python-dotenv

## 项目结构

```
.
├── 📜 process_data.ipynb       # 数据预处理、实验和完整分析流程的Jupyter Notebook。
├── 📜 data_show.ipynb          # 数据探索的Jupyter Notebook。
├── 🐍 main.py              # 封装了调用OpenAI API的核心函数。
├── 📂 prompts/             # 存放所有提示词（Prompt）模板。
│   ├── 📄 classification_prompt_v1.txt   # V1: Zero-Shot 分类
│   ├── 📄 classification_prompt_v2.txt   # V2: Few-Shot 分类
│   └── 📄 extraction_prompt.txt         # 技能提取
├── 📂 docs/
│   └── 📄 methodology.md    # 详细的方法论、分类体系定义和Prompt迭代日志。
├── 📄 validation_set_for_annotation.csv    # 使用prompt V1得到的分类结果
├── 📄 validation_set_for_annotation_50.csv    # 增加人工批注
├── 📄 validation_set_for_annotation_v1+v2_50.csv    # 增加使用prompt V2得到的分类结果
├── 📄 .env                 # 环境变量文件。
├── 📄 requirements.txt     # 项目依赖库。
└── 📄 README.md            # 本项目介绍文件。
```

## 如何运行

1.  **克隆仓库**
    ```bash
    git clone [你的仓库HTTPS链接]
    cd [你的项目文件夹]
    ```

2.  **安装依赖**
    (建议在虚拟环境中操作)
    ```bash
    pip install -r requirements.txt
    ```

3.  **运行分析**
    -   启动 Jupyter Notebook:
        ```bash
        jupyter notebook
        ```
    -   打开 `process_data.ipynb` 并按顺序运行所有代码单元格。

## 核心发现与分析：从V1到V2的迭代

本项目最核心的成果体现在通过数据驱动的方式优化Prompt，从而提升模型性能。

#### 性能对比

我们在一个包含 **50** 条手动标注数据的验证集上，评估了两种Prompt策略的性能：

| 模型 | Prompt 策略 | 验证集准确率 |
| :--- | :--- | :--- |
| V1 | Zero-Shot | 82.00% |
| V2 | Few-Shot  | 94.00% |

#### 问题分析 (边缘案例)

V1（Zero-Shot）模型在处理以下几类模糊职位时表现不佳：

-   **others类别被严重滥用**:
    - LLM 在面对零售、客服、地勤、门店运营、设施维护等岗位时，大量输出 others。  
    - 这些岗位实际属于公司运营支持体系（Corporate & Ops），并非无关职位。  
    - 说明 LLM 对“Corporate & Ops”这一类别的边界理解非常模糊，倾向于把“不明显是技术/销售/教育”的职位丢进 others。  
-   **销售 vs 运营的边界模糊**:   
    - LLM 容易把带有 “Account Executive”、“Sales”、“Merchandiser”、“Client Relationship” 等词的岗位直接归为 Marketing & Sales。  
-   **技术方向判断不准**:  
    - “System Integration Tester” 被归为 Engineering/Data & AI，而不是更准确的 IT & Security。  


#### 解决方案 (Prompt V2)

针对上述问题，V2 Prompt采用了**Few-Shot**策略。我们没有改变模型的任何参数，仅仅是在Prompt中加入了4个高质量的、针对性的示例，直接向模型展示了我们期望它如何处理这些“边缘案例”。

这种方法有效地为模型在模糊决策点上提供了清晰的“判例法”，使其能够更好地理解分类边界，从而实现了 **+12.00%** 的性能提升。这证明了在LLM应用中，高质量的Prompt工程是提升模型效果的最具性价比的手段之一。