from typing import Dict

from backend.core.base_agent import AgentConfig


def load_agent_configs(redis_url: str) -> Dict[str, AgentConfig]:
    """Load configurations for all agents"""
    return {
        "document_analyzer": AgentConfig(
            name="document_analyzer",
            description="Analyzes educational documents and extracts key information",
            model_name="gpt-4",
            temperature=0.3,
            redis_url=redis_url,
            prompt_template="""You are an expert document analyzer specializing in educational content.
Your task is to analyze the provided document and extract key information including:
1. Main topics and subtopics
2. Key concepts and their relationships
3. Content complexity assessment
4. Suggested module structure

Please provide your analysis in a structured format.""",
        ),
        "module_planner": AgentConfig(
            name="module_planner",
            description="Designs the learning module structure and organization",
            model_name="gpt-4",
            temperature=0.4,
            redis_url=redis_url,
            prompt_template="""You are an expert in educational content organization and learning path design.
Your task is to create an optimal learning structure based on the document analysis:
1. Break down content into logical modules
2. Determine prerequisites and dependencies
3. Suggest optimal learning paths
4. Identify key learning objectives

Please provide your module planning in a structured format.""",
        ),
        "content_generator": AgentConfig(
            name="content_generator",
            description="Generates engaging learning content for each module",
            model_name="gpt-4",
            temperature=0.7,
            redis_url=redis_url,
            prompt_template="""You are an expert educational content creator.
Your task is to generate engaging and effective learning content:
1. Create clear explanations
2. Provide relevant examples
3. Include practice exercises
4. Suggest visual aids and interactive elements

Please generate content that is both informative and engaging.""",
        ),
        "quiz_generator": AgentConfig(
            name="quiz_generator",
            description="Creates assessments and quizzes for learning modules",
            model_name="gpt-4",
            temperature=0.5,
            redis_url=redis_url,
            prompt_template="""You are an expert in educational assessment design.
Your task is to create effective quizzes and assessments:
1. Generate diverse question types
2. Ensure questions test understanding
3. Provide detailed explanations
4. Include difficulty levels

Please create assessments that effectively measure learning outcomes.""",
        ),
        "interactive_content": AgentConfig(
            name="interactive_content",
            description="Enhances content with interactive elements and UI components",
            model_name="gpt-4",
            temperature=0.6,
            redis_url=redis_url,
            prompt_template="""You are an expert in interactive learning design.
Your task is to enhance content with interactive elements:
1. Select appropriate UI components
2. Design user interactions
3. Ensure responsive design
4. Optimize user experience

Please create an engaging and effective interactive learning experience.""",
        ),
    }
