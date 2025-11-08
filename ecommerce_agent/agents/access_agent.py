import logging
from langchain_openai import ChatOpenAI
from langchain.agents import create_json_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain import hub


class AccessAgent:
    def __init__(self, llm_config, **kwargs): # 移除了不再需要的 embedding_model_path 和 product_vector_path
        self.logger = logging.getLogger(__name__)
        self.logger.info("正在初始化 AccessAgent...")
        # 初始化大模型
        self.llm = self._init_llm(llm_config)

        # 初始化子Agent
        from .order_agent import OrderAgent
        from .product_agent import ProductAgent

        self.order_agent = OrderAgent()
        self.product_agent = ProductAgent() # ProductAgent不再需要任何参数

        # 初始化工具和执行器
        self.tools = self._init_tools()
        self.memory = self._init_memory()
        self.executor = self._create_agent_executor()
        self.logger.info("AccessAgent 初始化完成。")

    def _init_llm(self, config):
        """初始化大语言模型"""
        return ChatOpenAI(
            openai_api_key=config["api_key"],
            base_url=config["base_url"],
            model_name=config["model_name"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"]
        )

    def _init_tools(self):
        """初始化工具集合"""
        return [
            self.order_agent.get_tool()
        ] + self.product_agent.get_tools()

    def _init_memory(self):
        """初始化对话记忆"""
        return ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output",
            k=10  # 保留最近10轮对话
        )

    def _create_agent_executor(self):
        """创建Agent执行器"""
        # This agent is better at forcing the model to follow JSON output format for tool calls,
        # which is more compatible with the current model's behavior.
        prompt = hub.pull("hwchase17/react-chat-json")
        agent = create_json_chat_agent(self.llm, self.tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True  # Gracefully handle if the model doesn't output valid JSON
        )

    def handle_question(self, question: str) -> str:
        """处理用户问题的入口"""
        self.logger.info(f"AccessAgent 开始处理问题: '{question}'")
        self.logger.info("即将调用 Agent Executor...")
        try:
            result = self.executor.invoke({"input": question})
            self.logger.info(f"Agent Executor 调用完成。原始返回: {result}")
            output = result.get("output", "未能获取到输出。")
            return output.strip()
        except Exception as e:
            self.logger.error(f"调用 Agent Executor 时发生异常: {e}", exc_info=True)
            return "处理您的问题时发生了内部错误，请检查后端日志。"