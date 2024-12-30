from schemas.Ai import PromptSchema

from utils.ai.default_values import get_do_sample, get_early_stopping, get_max_length, get_no_repeat_ngram_size, get_num_beans, get_num_return_sequences, get_skip_special_tokens, get_temperature, get_top_k, get_top_p

def get_response(prompt: PromptSchema, tokenizer, model):
    input_ids = tokenizer.encode(prompt.message, return_tensors="pt")
    num_return_sequences = get_num_return_sequences(prompt)

    output = model.generate(input_ids,
        max_length = get_max_length(prompt),
        num_beams = get_num_beans(prompt),
        no_repeat_ngram_size = get_no_repeat_ngram_size(prompt),
        num_return_sequences = num_return_sequences,
        do_sample = get_do_sample(prompt),
        early_stopping = get_early_stopping(prompt),
        top_k = get_top_k(prompt),
        top_p = get_top_p(prompt),
        temperature=get_temperature(prompt),
    )

    response = []
    for idx in range(num_return_sequences):
        response.append(tokenizer.decode(output[idx], skip_special_tokens = get_skip_special_tokens(prompt)))
    return { "response": response }
