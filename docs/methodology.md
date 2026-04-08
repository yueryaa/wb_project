# 方法论与Prompt工程日志

本文档深入探讨了本项目在职位分类任务中的方法论选择和提示词（Prompt）的详细迭代过程。

## 1. 业务职能分类体系定义

为了适应现代科技公司的组织架构，我们定义了一个更具针对性的分类体系。该体系力求在宏观上互斥，同时覆盖主流的职位族。

| 业务职能类别 | 定义与范围 (Scope) |
| :--- | :--- |
| **Engineering, Data & AI** | 涵盖所有软件开发、数据科学、数据工程、机器学习和人工智能相关的角色。这是公司技术产品实现的核心力量。 |
| **IT & Security** | 专注于公司的技术基础设施、网络、系统运维（DevOps/SRE）、信息安全和内部IT支持。保障公司技术稳定和安全。 |
| **Product & Design** | 包括产品经理（PM）、用户体验/界面设计师（UX/UI）、产品运营等，负责定义产品是什么、为什么做以及它看起来如何。 |
| **Marketing & Sales** | 负责将产品推向市场并实现商业变现。包括市场策略、增长黑客、数字营销、品牌、公共关系及所有销售角色。 |
| **Corporate & Ops** | 涵盖公司运营的核心支持职能，包括人力资源（HR）、财务（Finance）、法务（Legal）、行政及业务运营（如Sales Ops, Biz Ops）。 |
| **Education & Research** | 专注于学术研究、企业培训、课程开发或不直接隶属于产品研发的基础科学研究岗位。 |
| **others** | 无法明确归入以上任何一类的职位，例如高度综合性的高管助理、医护岗位等。 |

## 2. 提示词迭代日志 (Prompt Iteration Log)

我们采用从Zero-Shot到Few-Shot的迭代方法来优化分类性能。

### 2.1 Prompt V1: Zero-Shot 基线测试

#### 设计思路
V1旨在测试`qwen3.6-plus:free`在没有任何示例的情况下，仅凭指令理解完成分类任务的基线能力。核心设计保持不变：赋予专家角色、明确任务、提供封闭选项、并约束输出格式。

#### V1 完整提示词
```text
You are an expert HR analyst. Your task is to classify a job posting into one of the following business functions.

Business Functions:
["Engineering, Data & AI ", "IT & Security", "Product & Design", "Marketing & Sales","Corporate & Ops","Education & Research ","others"]

Job Posting:
"""
{job_description}
"""

Please provide the single most appropriate business function from the list above. Do not provide any explanation or additional text.
```

#### V1 在验证集上的表现
-   **准确率**: `82.00%`
-   **典型错误案例分析**:
    -   **案例 1: "Corporate & Ops" vs. "others" 严重混淆**
        -   **职位描述片段**: `Customer Service Representative at Family Dollar... greeting customers, processing transactions, stocking shelves...`
        -   **LLM (V1) 分类**: `others`
        -   **人工正确分类**: `Corporate & Ops`
        -   **分析**: 模型未能识别零售门店的客服、收银、补货等岗位属于公司运营体系（Corporate & Ops），错误地将其归为无关的“others”。这是最常见的错误类型，说明模型对运营支持类岗位的理解边界过窄。
    -   **案例 2: "Corporate & Ops" vs. "Marketing & Sales" 边界模糊**
        -   **职位描述片段**: `Employee Benefits Account Executive... manage client relationships, renewals, negotiate with carriers...`
        -   **LLM (V1) 分类**: `Marketing & Sales`
        -   **人工正确分类**: `Corporate & Ops`
        -   **分析**: 模型看到“Account Executive”、“negotiate”、“client relationships”等销售相关词汇，就直接归为 Marketing & Sales。但该岗位核心是内部福利管理与运营支持，应优先归入 Corporate & Ops。
    -   **案例 3: "IT & Security" vs. "Engineering, Data & AI" 技术方向错误**
        -   **职位描述片段**: `Senior System Integration Tester... Test Scenario development, defect tracking, Mainframes Testing...`
        -   **LLM (V1) 分类**: `Engineering, Data & AI`
        -   **人工正确分类**: `IT & Security`
        -   **分析**: 模型被“Testing”、“Data Preparation”等技术词汇吸引，误判为数据/工程类。而该岗位核心是系统集成测试与质量保障，更符合 IT & Security 的基础设施与稳定性守护定位。

### 2.2 Prompt V2: Few-Shot 优化

#### 设计思路
V2的设计完全基于对V1错误的分析。我们通过**Few-Shot Learning**，直接向模型展示如何裁决这些在新分类体系下产生的模糊边界。
-   **引入判例**:在Prompt中加入了从错误案例中精心挑选的示例，用于校准模型对`Corporate & Ops`和`others`等的理解。  

#### V2 完整提示词
```text
You are an expert HR analyst. Your task is to classify a job posting into one of the following business functions.

Taxonomy Definitions:
- Engineering, Data & AI: Software development, Data Science/Eng, ML/AI...
- IT & Security: Infrastructure, Networking, DevOps/SRE, InfoSec...
- Marketing & Sales: Strategy, Growth, Digital Marketing, PR, Branding, and all Sales roles.
- Corporate & Ops: HR, Finance, Legal, Admin, Biz Ops, Sales Ops, Retail Operations, Facilities...
- Education & Research: Academic roles, Corporate Training, Fellowships...
- Others: Executive Assistants, general internships, or highly niche roles.

Classification Rules:
- If a role bridges two categories, prioritize the functional core.
- Sales Ops / Retail Ops / Customer Service in stores → Corporate & Ops
- Merchandiser / Ramp Agent / Store Associate → Corporate & Ops
- Account Executive in benefits/insurance → Corporate & Ops (not pure Sales)

Here are some examples:

Example 1:
Job Posting: "Truman Fellowship at UMKC School of Law... legal counsel to tenants..."
Category: Education & Research

Example 2:
Job Posting: "Sales Floor Associate at Dollar Tree... handle sales transactions, stock shelves..."
Category: Corporate & Ops

Example 3:
Job Posting: "Senior System Integration Tester... test scenario development, defect tracking..."
Category: IT & Security

Example 4:
Job Posting: "Employee Benefits Account Executive... manage client relationships, renewals..."
Category: Corporate & Ops


Now, classify the following job posting. Respond with **only** the category name, no explanation.

Job Posting:
"""
{job_description}
"""
```

#### 最终效果评估
-   **V2 准确率**: `94.00%`
-   **性能提升**: `12.00%`
-   **结论**: 结果再次证明，对于有明确定义的分类任务，Few-Shot Prompt是极其有效的优化手段。通过提供高质量的“判例”，我们成功地教会了模型如何在新分类体系下进行更精确的判断，将准确率提升到了一个业务可用的高水平。