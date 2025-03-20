from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

#load the model and tokenizer

model_name = "t5-small" #lightweight option
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def summarize(text:str , max_length: int = 400) -> str:
    input_text = "summarize:" + text.strip().replace("\n", "")
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512 ,truncation=True)
    summary_ids = model.generate(inputs, max_length=max_length, min_length=100, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
