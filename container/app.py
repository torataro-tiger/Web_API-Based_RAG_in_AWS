from typing import Final

import boto3
from botocore.config import Config
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_aws import ChatBedrock
from langchain_community.retrievers import AmazonKendraRetriever
from settings import INDEX_ID

MAIN_REGION: Final = "ap-northeast-1"
MODEL_REGION: Final = "us-east-1"
MODEL_ID: Final = "anthropic.claude-3-sonnet-20240229-v1:0"


def handler(event, context):

    message = event.get("message", None)
    if message is None:
        return {"error": "Missing 'message' in request"}

    chat = ChatBedrock(  # type: ignore
        region=MODEL_REGION,
        model_id=MODEL_ID,  # type: ignore
        model_kwargs=dict(temperature=0),
        streaming=True,
        config=Config(
            retries={"max_attempts": 10, "mode": "adaptive"},
        ),
    )

    retriever = AmazonKendraRetriever(
        index_id=INDEX_ID,
        client=boto3.client(
            "kendra",
            region_name=MAIN_REGION,
        ),
        min_score_confidence=None,
        attribute_filter={
            "EqualsTo": {
                "Key": "_language_code",
                "Value": {"StringValue": "ja"},
            },
        },
    )

    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="weather_search",
        description="天気に関する情報を検索します。今日の天気を聞かれたときにこちらのツールを使います。",
    )

    tools = [retriever_tool]

    prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(
        llm=chat,
        tools=tools,
        prompt=prompt,  # type: ignore
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )

    result = agent_executor.invoke({"input": message})
    print(result)

    return result
