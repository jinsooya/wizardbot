def opik_trace(input_data, output):
    trace = opik_client.trace(
        name='chat',
        input={'user_input': input_data},
        output={'response': output}
    )

    trace.span(
        name='llm_call',
        type='llm',
        input={'context': context},
        output={'response': output}
    )
